# Contributing to augLABS augmntd MCP (Xenware)

Thank you for your interest in contributing to the **augLABS augmntd MCP (Xenware) Enterprise Harmonic Bridge**!

## Development Workflow

1. Clone or navigate to the repository.
2. Install dependencies:
   ```bash
   cd augmntd-mcp
   npm install
   ```
3. Run locally in watch mode:
   ```bash
   npm run dev
   ```
4. Run integration tests:
   ```bash
   npm test
   ```
5. Ensure TypeScript compiles with zero errors:
   ```bash
   npm run build
   ```

## Architectural Guidelines

- **Harmonic Coherence:** State mutation should prioritize continuous wave superposition rather than destructive binary search / lock acquisition.
- **Topological Integrity:** Mutating actions must maintain topological knot complexity $C_{\text{topo}} \ge \phi^{-1} \approx 0.618034$.
- **Security & Privacy:** Ensure all data outputs pass through the zero-leakage sanitizer (`governance.sanitizeOutput`).

## Pull Requests

1. Create a feature branch.
2. Ensure `npm run build` and `npm test` pass.
3. Submit a Pull Request with a clear description of changes.
