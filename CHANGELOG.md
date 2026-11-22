# Changelog

Follows Keep a Changelog and SemVer.

## [0.1.0] - Unreleased

### Added

- Stage 0: pnpm monorepo structure, strict TypeScript, ESLint, Prettier, Vitest, CI.
- Colyseus server with `WorldRoom` and protocol version check.
- Vite client showing "Server: connected".
- Stage 1A: single-player Three.js 200x200m test world with solid marker block collisions, procedural low-poly character with idle/walk/run animations, third-person orbit camera with gentle auto-follow when Mouse Look is off, fixed-timestep loop, WASD/Shift/left-or-right mouse drag and optional pointer-lock (`L`) desktop controls, multi-touch virtual joystick, auto desktop/touch switching, F3/tap FPS counter, WebGL2 fallback, and movement/collision/camera/loop unit tests.
- Stage 1B (K1): standardized headless Blender 4.2 LTS -> `.glb` asset pipeline (`tools/asset-pipeline/`, `tools/character-builder/`, `docs/guides/asset-pipeline.md`, `docs/decisions/0002-blender-glb-asset-pipeline.md`), Vite `/content` serving & bundling, shared Three.js `GLTFLoader` + Abeto toon material converter + `AnimationMixer` (`CharacterAvatar`), and K1 pipeline verification character GLB.
- Stage 1B (K2): continuous all-quad sculpted human base mesh (`tools/character-builder/body_mesh.py`) with ~5.5-head Abeto proportions, seamless neck/ears/hands/flat soles, tuned angular crease outline shader (`1.2 px` half-step Roberts Cross), and improved `/lab` 4-side facing order and framing.
- Stage 1B (K3): modular Abeto character & gender system (`tools/character-builder/body_mesh.py`, `hair_parts.py`, `top_parts.py`, `bottom_parts.py`, `shoe_parts.py`, `bag_parts.py`, `textures.py`, `build_character.py`, `packages/shared/src/constants/character-skins.ts`, `packages/client/src/entities/character-avatar.ts`) with 2 default gender designs—**Male (default skin)** (shaggy slate-teal hair, oversized orange pullover hoodie with folded hood & grey drawstrings, crimson-red `"Hi"` backpack, cropped charcoal joggers, white crew socks, chunky dark high-top sneakers) and **Female (default skin)** (dark bob hair with swept bangs, curved sideburns, exposed ears, compact nape bob, and coaxially-tied upper-back twin buns, A-line cyan/off-white color-blocked T-shirt, golden-yellow crossbody sling bag, charcoal shorts `celana pendek`, white crew socks, and chunky off-white high-top velcro-strap sneakers); separated modular `SkinnedMesh` slots (`BodyMesh`, `HairMesh`, `TopMesh`, `BottomMesh`, `ShoesMesh`, `BagMesh`) for live outfit skin swapping in the world Settings panel and `/lab`; 2-tone Abeto cel shading (`TOON_LEVELS = 2`); `1.0px` default outline thickness (`OUTLINE_THICKNESS_PX = 1.0`); and closer third-person world camera (`DISTANCE_M = 3.2`, `TARGET_HEIGHT_M = 1.05`, `FOV_DEG = 64`).
