import http from 'http';
import WebSocket from 'ws';

const BASE_URL = process.env.TEST_URL || 'http://localhost:8080';
const WS_URL = process.env.TEST_WS_URL || 'ws://localhost:8080/tauk-stream';

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function getHealth() {
  console.log('[Test 1] Testing /healthz probe...');
  const res = await fetch(`${BASE_URL}/healthz`);
  const data = await res.json();
  console.log('Health response:', JSON.stringify(data, null, 2));
  if (data.status !== 'OK') throw new Error('Health check failed');
  console.log('✔ /healthz probe OK\n');
}

async function testWebSocketStream() {
  console.log('[Test 2] Testing /tauk-stream WebSocket...');
  return new Promise<void>((resolve, reject) => {
    const ws = new WebSocket(WS_URL);
    let messageReceived = false;

    ws.on('open', () => {
      console.log('Connected to WebSocket stream');
      // Ingest test state over WS
      ws.send(
        JSON.stringify({
          action: 'ingest',
          agent_id: 'ws_test_agent',
          phase_or_key: 'branch:harmonic-test',
          coherence: 0.95,
          valence: 1.0,
          payload: 'Verification impulse'
        })
      );
    });

    ws.on('message', (data) => {
      const parsed = JSON.parse(data.toString());
      console.log('Received WebSocket message event/type:', parsed.event || parsed.schema || 'telemetry');
      messageReceived = true;
      ws.close();
      resolve();
    });

    ws.on('error', (err) => {
      reject(err);
    });

    setTimeout(() => {
      if (!messageReceived) {
        ws.close();
        reject(new Error('WebSocket timeout waiting for messages'));
      }
    }, 5000);
  });
}

async function testMCPSSEAndJsonRpc() {
  console.log('[Test 3] Testing MCP SSE Transport & JSON-RPC...');

  return new Promise<void>((resolve, reject) => {
    const pendingRequests = new Map<number | string, (res: any) => void>();
    let endpointUrl = '';

    const sseReq = http.request(
      `${BASE_URL}/sse`,
      {
        headers: {
          Accept: 'text/event-stream'
        }
      },
      (res) => {
        let buffer = '';

        res.on('data', async (chunk) => {
          buffer += chunk.toString();
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line.startsWith('event: endpoint')) {
              // The next line contains data: ...
              const nextLine = lines[i + 1] || buffer;
              if (nextLine.startsWith('data: ')) {
                endpointUrl = nextLine.replace('data: ', '').trim();
                console.log('Received MCP endpoint via SSE:', endpointUrl);
                startJsonRpcFlow();
              }
            } else if (line.startsWith('data: ') && !line.includes('/messages?sessionId=')) {
              try {
                const jsonStr = line.replace('data: ', '').trim();
                const rpcMsg = JSON.parse(jsonStr);
                if (rpcMsg.id && pendingRequests.has(rpcMsg.id)) {
                  const handler = pendingRequests.get(rpcMsg.id)!;
                  pendingRequests.delete(rpcMsg.id);
                  handler(rpcMsg);
                }
              } catch (err) {
                // Not JSON data
              }
            }
          }
        });
      }
    );

    async function sendJsonRpc(id: number, method: string, params: any): Promise<any> {
      return new Promise(async (resHandler, errHandler) => {
        pendingRequests.set(id, resHandler);

        const resp = await fetch(`${BASE_URL}${endpointUrl}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            jsonrpc: '2.0',
            id,
            method,
            params
          })
        });

        if (resp.status !== 200 && resp.status !== 202) {
          errHandler(new Error(`POST /messages returned status ${resp.status}`));
        }
      });
    }

    async function startJsonRpcFlow() {
      try {
        // 1. List tools
        console.log('Requesting tools/list via JSON-RPC...');
        const toolsRes = await sendJsonRpc(1, 'tools/list', {});
        const tools = toolsRes.result.tools;
        console.log(`Discovered ${tools.length} Xen-Tools:`);
        for (const t of tools) {
          console.log(` - ${t.name}: ${t.description.substring(0, 65)}...`);
        }

        // 2. Call execute_harmonic_mutation
        console.log('\nCalling execute_harmonic_mutation...');
        const mutationRes = await sendJsonRpc(2, 'tools/call', {
          name: 'execute_harmonic_mutation',
          arguments: {
            action: 'execute_balance_reallocation',
            alpha_aperture: 0.85,
            psi_attribution: 1.0,
            parameters: {
              from_account: '94105',
              to_account: '94106',
              amount_cents: 250000
            }
          }
        });
        console.log('Mutation tool response:');
        console.log(mutationRes.result.content[0].text);

        // 3. Call cdt_ingest_state
        console.log('\nCalling cdt_ingest_state...');
        const ingestRes = await sendJsonRpc(3, 'tools/call', {
          name: 'cdt_ingest_state',
          arguments: {
            agent_id: 'agent_gamma',
            phase_or_key: 'branch:feature-superposition',
            coherence: 0.92,
            valence: 1.0,
            payload: 'Superposition consensus state'
          }
        });
        console.log('Ingest response:');
        console.log(ingestRes.result.content[0].text);

        // 4. Call cdt_compute_phase_lock
        console.log('\nCalling cdt_compute_phase_lock...');
        const lockRes = await sendJsonRpc(4, 'tools/call', {
          name: 'cdt_compute_phase_lock',
          arguments: { threshold: 0.8 }
        });
        console.log('Phase lock response:');
        console.log(lockRes.result.content[0].text);

        // 5. Read Resource xen://enterprise/ledger
        console.log('\nReading resource xen://enterprise/ledger...');
        const readRes = await sendJsonRpc(5, 'resources/read', {
          uri: 'xen://enterprise/ledger'
        });
        console.log('Resource content:');
        console.log(readRes.result.contents[0].text);

        sseReq.destroy();
        resolve();
      } catch (err) {
        sseReq.destroy();
        reject(err);
      }
    }

    sseReq.on('error', (err) => reject(err));
    sseReq.end();
  });
}

async function runAll() {
  try {
    await getHealth();
    await testWebSocketStream();
    console.log('✔ /tauk-stream WebSocket OK\n');
    await testMCPSSEAndJsonRpc();
    console.log('\n✔ All Xenware Enterprise Harmonic Bridge tests passed successfully!');
    process.exit(0);
  } catch (err) {
    console.error('Test execution failed:', err);
    process.exit(1);
  }
}

runAll();
