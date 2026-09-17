import express, { Request, Response } from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { WebSocketServer, WebSocket } from 'ws';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema
} from '@modelcontextprotocol/sdk/types.js';

import { HarmonicCoherenceEngine } from './coherence/cdt.js';
import { LivingRepertoire } from './repertoire/repertoire.js';
import { SecurityGovernanceEngine } from './security/governance.js';
import { getXenToolDefinitions, handleXenToolCall } from './mcp/tools.js';
import { getXenResourceDefinitions, handleXenReadResource } from './mcp/resources.js';
import { getXenPromptDefinitions, handleXenGetPrompt } from './mcp/prompts.js';

const app = express();
app.use(cors({ origin: '*' }));

const httpServer = createServer(app);
const port = process.env.PORT ? parseInt(process.env.PORT, 10) : 8080;

// Initialize Core Xenware Engines
const coherenceEngine = new HarmonicCoherenceEngine(64);
const repertoire = new LivingRepertoire();
const governance = new SecurityGovernanceEngine();

// ---------------------------------------------------------------------------
// 1. Health Probe for Cloud Run (Startup & Liveness)
// ---------------------------------------------------------------------------
app.get('/healthz', (_req: Request, res: Response) => {
  const lock = coherenceEngine.computePhaseLock();
  res.status(200).json({
    status: 'OK',
    service: 'augmntd-mcp-xenware',
    version: '1.0.0',
    uptime_seconds: Math.floor(process.uptime()),
    timestamp: new Date().toISOString(),
    tau_k: coherenceEngine.tauK,
    cheeger_floor: coherenceEngine.cheegerFloor,
    coherence_status: lock.coherence_status,
    kuramoto_r: lock.kuramoto_r,
    repertoire_sigma: repertoire.getSigma(),
    total_traces: repertoire.getTraceCount(),
    memory_usage_mb: Math.round(process.memoryUsage().rss / 1024 / 1024)
  });
});

// ---------------------------------------------------------------------------
// 2. MCP Core Server Instance & Handlers
// ---------------------------------------------------------------------------
const mcpServer = new Server(
  {
    name: 'augmntd-mcp-xenware',
    version: '1.0.0'
  },
  {
    capabilities: {
      resources: {},
      tools: {},
      prompts: {}
    }
  }
);

// Map active SSE sessions
const transports = new Map<string, SSEServerTransport>();
const sessionAuthContexts = new Map<string, any>();

// List Tools
mcpServer.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: getXenToolDefinitions()
  };
});

// Call Tool
mcpServer.setRequestHandler(CallToolRequestSchema, async (request, extra) => {
  const { name, arguments: args } = request.params;
  const securityContext = governance.authenticate(); // Uses ambient/ephemeral token
  return await handleXenToolCall(
    name,
    args || {},
    coherenceEngine,
    repertoire,
    governance,
    securityContext
  );
});

// List Resources
mcpServer.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: getXenResourceDefinitions()
  };
});

// Read Resource
mcpServer.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;
  return await handleXenReadResource(uri, coherenceEngine, repertoire, governance);
});

// List Prompts
mcpServer.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: getXenPromptDefinitions()
  };
});

// Get Prompt
mcpServer.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  return handleXenGetPrompt(name, args);
});

// ---------------------------------------------------------------------------
// 3. MCP SSE Transport Endpoints
// ---------------------------------------------------------------------------
app.get('/sse', async (req: Request, res: Response) => {
  console.log(`[MCP-SSE] New incoming connection from ${req.ip}`);
  const authHeader = req.headers.authorization;
  const securityContext = governance.authenticate(authHeader);

  const transport = new SSEServerTransport('/messages', res);
  const sessionId = transport.sessionId;

  transports.set(sessionId, transport);
  sessionAuthContexts.set(sessionId, securityContext);

  req.on('close', () => {
    console.log(`[MCP-SSE] Session ${sessionId} closed`);
    transports.delete(sessionId);
    sessionAuthContexts.delete(sessionId);
  });

  await mcpServer.connect(transport);
});

// ---------------------------------------------------------------------------
// 4. MCP JSON-RPC Message Dispatch
// ---------------------------------------------------------------------------
app.post('/messages', async (req: Request, res: Response) => {
  const sessionId = req.query.sessionId as string;
  if (!sessionId) {
    res.status(400).send('Missing sessionId parameter');
    return;
  }

  const transport = transports.get(sessionId);
  if (!transport) {
    res.status(404).send('Session not found or expired');
    return;
  }

  await transport.handlePostMessage(req, res);
});

// ---------------------------------------------------------------------------
// 5. WebSocket Server for Live tau_k Coherence Stream
// ---------------------------------------------------------------------------
const wss = new WebSocketServer({ server: httpServer, path: '/tauk-stream' });

wss.on('connection', (ws: WebSocket, req) => {
  console.log(`[WebSocket] Client connected to /tauk-stream from ${req.socket.remoteAddress}`);

  // Send initial snapshot immediately upon connection
  ws.send(JSON.stringify(coherenceEngine.exportStreamPayload()));

  // Broadcast periodic tau_k field metrics to connected client (1000ms cadence)
  const interval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(coherenceEngine.exportStreamPayload()));
    }
  }, 1000);

  // Allow client to push telemetry or test commands directly over WebSocket
  ws.on('message', (data: string) => {
    try {
      const msg = JSON.parse(data.toString());
      if (msg.action === 'ingest' && msg.agent_id && msg.phase_or_key) {
        coherenceEngine.ingestState(
          msg.agent_id,
          msg.phase_or_key,
          msg.coherence ?? 1.0,
          msg.valence ?? 1.0,
          msg.payload
        );
        ws.send(
          JSON.stringify({
            event: 'state_ingested',
            status: 'OK',
            lock: coherenceEngine.computePhaseLock()
          })
        );
      } else if (msg.action === 'resolve_drift') {
        const driftRes = coherenceEngine.resolveDrift();
        ws.send(JSON.stringify({ event: 'drift_resolved', ...driftRes }));
      }
    } catch (err: any) {
      ws.send(JSON.stringify({ error: err.message }));
    }
  });

  ws.on('close', () => {
    clearInterval(interval);
    console.log('[WebSocket] Client disconnected from /tauk-stream');
  });

  ws.on('error', (err) => {
    console.error('[WebSocket] Error:', err);
  });
});

// ---------------------------------------------------------------------------
// 6. Graceful Shutdown for Cloud Run / Container Lifecycle
// ---------------------------------------------------------------------------
function gracefulShutdown(signal: string) {
  console.log(`[augmntd-mcp] Received ${signal}. Initiating graceful shutdown...`);
  wss.close(() => {
    console.log('[WebSocket] Server terminated.');
  });
  httpServer.close(() => {
    console.log('[HTTP/SSE] Server stopped accepting requests.');
    process.exit(0);
  });

  // Force close after 10s if hanging
  setTimeout(() => {
    console.error('[augmntd-mcp] Could not close connections in time, forcefully shutting down');
    process.exit(1);
  }, 10000);
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// ---------------------------------------------------------------------------
// 7. Start Server
// ---------------------------------------------------------------------------
httpServer.listen(port, '0.0.0.0', () => {
  console.log(`=======================================================`);
  console.log(` augLABS augmntd MCP (Xenware) Enterprise Bridge Active `);
  console.log(` Listening on port: ${port}`);
  console.log(` Health probe:      http://0.0.0.0:${port}/healthz`);
  console.log(` MCP SSE endpoint:  http://0.0.0.0:${port}/sse`);
  console.log(` τ_k stream (WSS):  ws://0.0.0.0:${port}/tauk-stream`);
  console.log(`=======================================================`);
});
