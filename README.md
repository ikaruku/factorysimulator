# Factory Simulator

Open-world 3D multiplayer game with a factory theme (browser: laptop, tablet, phone). Factory mechanics come after the open world is finished.

Primary reference: [docs/game-plan.md](docs/game-plan.md) (defines scope, stages and test gates). Project standards: [docs/standards.md](docs/standards.md). Summary: [docs/preparation-summary.md](docs/preparation-summary.md).

## Prerequisites

- Node.js 20 LTS or newer (check: `node -v`).
- pnpm (install: `npm install -g pnpm`, check: `pnpm -v`).

## Running

On Windows, double-click `start-dev.bat` in the project root to install missing dependencies (if needed), start both the client and server (accessible on localhost and your local Wi-Fi/LAN), and print the exact Network URL to open from another device.

Or from a terminal:

```bash
pnpm install
pnpm dev        # client http://localhost:5173, server ws://localhost:2567
pnpm lint
pnpm test
pnpm build
```

For phone testing on the same Wi-Fi, run `pnpm dev -- --host` inside `packages/client` or:

```bash
pnpm --filter @factory-simulator/client dev -- --host
```

Copy `.env.example` to `.env` if you need to change the port.

## 3D Asset Pipeline

All 3D assets (characters, props, buildings, machines, and map pieces) are built reproducibly with headless Blender 4.2 LTS and exported as `.glb` into `content/` (see [docs/guides/asset-pipeline.md](docs/guides/asset-pipeline.md)).

```bash
pnpm setup:blender    # caches portable Blender 4.2 LTS in tools/.cache/blender/
pnpm build:character  # exports content/characters/default/character.glb + 4-angle previews
```

## Controls & Visual Lab

- Desktop: `WASD` or Arrow keys to move, `Shift` to run, drag mouse (left or right button) to rotate camera, press `L` or click `Mouse Look` for free mouse steering (`Esc` unlocks), `F3` to toggle FPS.
- Touch / Phone: virtual joystick on the bottom-left (push to outer edge to run), drag screen to rotate camera, `FPS` button on top-right, `Settings` to toggle outlines off on weaker devices.
- Visual comparison lab: open `/lab` (`http://localhost:5173/lab`) to inspect the 4-side character, toon materials, hard shadows, procedural sky, Abeto color palette, and paper-sticker HUD button samples.

## Structure

- `packages/shared` types, protocol, constants, shared math (used by client and server)
- `packages/client` Vite + Three.js
- `packages/server` Node.js + Colyseus
- `content/` game data, `tools/` helper tools, `tests/` end-to-end and bot tests, `docs/` documentation
