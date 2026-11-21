# 0001 - Initial stack

Decision: TypeScript + Vite + Three.js (client), Node.js + Colyseus 0.16 via `@colyseus/core` and `@colyseus/ws-transport` (server), pnpm monorepo. Rationale: see the "Technology" section of [game-plan.md](../game-plan.md).

The `colyseus` meta-package is avoided because it pulls a git-hosted dependency (uWebSockets.js) that requires git at install time.
