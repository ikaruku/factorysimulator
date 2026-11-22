# Project Progress Tracker

Single at-a-glance status tracker for **Factory Simulator** from **Stage 0** through **Stage 8**, including every sub-stage and deliverable defined in [docs/game-plan.md](docs/game-plan.md).

- **Current Stage:** **Stage 1B – Sub-stage 1B-K5** (built, standardized & verified; awaiting owner final sign-off for **Stage 1B Pass**)
- **Next Stage:** **Stage 2A – Map from PNG**
- **Overall Stage Completion:** **2.9 / 11 stages** (Stage 0 Passed, Stage 1A Passed, Stage 1B 1B-Core + K1–K5 built / K5 pending owner playtest approval)

---

## Master Stage Overview

| Stage  | Name                                     | Scope Summary                                                                                                        | Status                          | Progress | Key Artifacts / Files                                                                                                                                                                                                                                                    |
| :----: | :--------------------------------------- | :------------------------------------------------------------------------------------------------------------------- | :------------------------------ | :------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **0**  | Project Setup & Standards                | Monorepo, strict TS/ESLint/Prettier/Vitest, CI, Colyseus ping, docs                                                  | Done (Passed)                   |   100%   | [package.json](package.json), [packages/server/src/rooms/world-room.ts](packages/server/src/rooms/world-room.ts), [.github/workflows/ci.yml](.github/workflows/ci.yml)                                                                                                   |
| **1A** | Movement Foundation                      | 200x200 m world, fixed 60 Hz physics, orbit camera, WASD/Shift + mobile joystick, FPS                                | Done (Passed)                   |   100%   | [packages/shared/src/utils/movement.ts](packages/shared/src/utils/movement.ts), [packages/client/src/core/camera-controller.ts](packages/client/src/core/camera-controller.ts), [packages/client/src/ui/virtual-joystick.ts](packages/client/src/ui/virtual-joystick.ts) |
| **1B** | Abeto-Style Visuals & Character Pipeline | Cel shading, 1.0 px outlines, sky, `/lab`, Male/Female modular GLB characters (`K1`–`K5`)                            | Ready for Final Sign-Off (`K5`) |   95%    | [packages/client/src/visuals/outline-composer.ts](packages/client/src/visuals/outline-composer.ts), [tools/character-builder/](tools/character-builder/build_character.py), [content/characters/](content/characters/male/character.glb)                                 |
| **2A** | Map from PNG                             | `tools/map-builder` (`source.png` -> 3D map + collision + spawn + `F4` debug), client map loader                     | Not Started                     |    0%    | `tools/map-builder/`, `content/maps/`                                                                                                                                                                                                                                    |
| **2B** | Abeto-Style Environment                  | `height.png` slopes, `props.json`, procedural/Blender props library, instancing, roofs/windows, `/lab` props gallery | Not Started                     |    0%    | `content/props/`, `content/buildings/`                                                                                                                                                                                                                                   |
| **3**  | Core Multiplayer                         | Authoritative 30-player `WorldRoom`, guest login, prediction + 100 ms interpolation, auto-reconnect, `pnpm bots`     | Not Started                     |    0%    | `packages/shared/src/protocol/`, `packages/server/src/`, `tests/`                                                                                                                                                                                                        |
| **4**  | Social Interaction                       | Chat box + 5 s bubbles, XSS + profanity filter, 6 emotes (`content/emotes.json`), player list & mute                 | Not Started                     |    0%    | `content/emotes.json`, chat & emote UI/server systems                                                                                                                                                                                                                    |
| **5**  | Abeto-Style UI & Feel                    | Loading screen, start onboarding UI, HUD & Settings, Web Audio ambient + footsteps, mobile layout/safe-areas         | Not Started                     |    0%    | `packages/client/src/ui/`, audio & theme modules                                                                                                                                                                                                                         |
| **6**  | Optimization & Resilience                | Compression/instancing/LOD, `pnpm perf` 30-bot report (`docs/perf-report.md`), leak check, auto quality presets      | Not Started                     |    0%    | `docs/perf-report.md`, `tests/`                                                                                                                                                                                                                                          |
| **7**  | Deploy                                   | Server Dockerfile, production `wss://` config, auto-deploy CI/CD on `main`, `/health`, `docs/guides/deploy.md`       | Not Started                     |    0%    | `docs/guides/deploy.md`, deployment configs                                                                                                                                                                                                                              |
| **8**  | Factory Foundation                       | Data-driven Entity-Component world objects, server 10 Hz tick skeleton, sample machine, factory design template      | Not Started                     |    0%    | `packages/shared/`, `content/`, `docs/decisions/`                                                                                                                                                                                                                        |

---

## Detailed Breakdown by Stage & Sub-Stage

### Stage 0 – Project Setup & Standards `[Done - Passed]`

| Sub-Stage | Description                                                                                        | Status | Notes / Verification                                                  |
| :-------: | :------------------------------------------------------------------------------------------------- | :----- | :-------------------------------------------------------------------- |
|  **0.1**  | pnpm monorepo (`shared`, `client`, `server`, `content`, `tools`, `tests`, `docs`)                  | Done   | Dependency boundary enforced (`client`/`server` only import `shared`) |
|  **0.2**  | Strict TypeScript (`no any`), ESLint, Prettier, Vitest                                             | Done   | `pnpm lint` & `pnpm test` configured                                  |
|  **0.3**  | Core documentation (`README.md`, `CLAUDE.md`, `docs/standards.md`, `CHANGELOG.md`, `.env.example`) | Done   | Updated continuously per stage                                        |
|  **0.4**  | CI workflow (`.github/workflows/ci.yml`) & Windows launcher (`start-dev.bat`)                      | Done   | Supports localhost and Wi-Fi/LAN mobile testing via `/colyseus` proxy |
|  **0.5**  | Colyseus `WorldRoom` + client `"Server: connected"` check + protocol version test                  | Done   | Verified passing (`packages/shared` + `packages/server` unit tests)   |

### Stage 1A – Movement Foundation (Single Player) `[Done - Passed]`

| Sub-Stage | Description                                                                       | Status | Notes / Verification                                                                                                         |
| :-------: | :-------------------------------------------------------------------------------- | :----- | :--------------------------------------------------------------------------------------------------------------------------- |
| **1A.1**  | 200x200 m Three.js scene, lighting, fog, marker boxes & colliders                 | Done   | [packages/client/src/world/test-world.ts](packages/client/src/world/test-world.ts)                                           |
| **1A.2**  | Fixed 60 Hz game loop (`FIXED_TIMESTEP_SEC = 1/60`)                               | Done   | [packages/client/src/core/game-loop.ts](packages/client/src/core/game-loop.ts)                                               |
| **1A.3**  | Circle-vs-AABB collision sliding, walk (`4 m/s`) & run (`7 m/s`) config           | Done   | 10 unit tests in [movement.test.ts](packages/shared/src/utils/movement.test.ts)                                              |
| **1A.4**  | Third-person orbit camera + gentle auto-follow + mouse drag / `[L]` pointer lock  | Done   | Distance revised closer (`3.2 m`, `FOV 64°`) per owner review                                                                |
| **1A.5**  | Mobile touch virtual joystick, auto desktop/touch switch, WebGL2 check, Wake Lock | Done   | [virtual-joystick.ts](packages/client/src/ui/virtual-joystick.ts), [webgl-check.ts](packages/client/src/core/webgl-check.ts) |
| **1A.6**  | FPS counter (`F3` / HUD tap toggle) & camera/loop unit tests                      | Done   | 8 client unit tests passing                                                                                                  |

### Stage 1B – Abeto-Style Visuals & Modular Character Pipeline `[95% - Ready for K5 Final Pass]`

|  Sub-Stage  | Description                                                                                                                                                                                                                                                                                                                                       | Status                                         | Notes / Verification                                                                                                                                                                                                                                                                                                                       |
| :---------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :--------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1B-Core** | 2-tone Abeto toon shader (`TOON_LEVELS = 2`), `1.0 px` outline composer (depth + normal crease), crisp hard shadows, procedural turquoise sky, Abeto theme palette, Settings outline toggle, `/lab` comparison page & paper-sticker HUD samples                                                                                                   | Done (Passed)                                  | [toon-material.ts](packages/client/src/visuals/toon-material.ts), [outline-composer.ts](packages/client/src/visuals/outline-composer.ts), [procedural-sky.ts](packages/client/src/visuals/procedural-sky.ts)                                                                                                                               |
|  **1B-K1**  | Headless **Blender 4.2 LTS** -> `.glb` asset pipeline (`tools/asset-pipeline/`), Vite `/content` static serving & build copy, shared Three.js `GLTFLoader` + toon converter (`CharacterAvatar`), multi-angle preview renderer                                                                                                                     | Done (Passed)                                  | [0002-blender-glb-asset-pipeline.md](docs/decisions/0002-blender-glb-asset-pipeline.md), [glb-loader.ts](packages/client/src/assets/glb-loader.ts)                                                                                                                                                                                         |
|  **1B-K2**  | Continuous ~5.8-head sculpted low-poly anime human `BodyMesh` with seamless neck, V-oval jawline, ears, hands, knees/calves & grounded `y = 0` feet                                                                                                                                                                                               | Done (Passed)                                  | [body_mesh.py](tools/character-builder/body_mesh.py)                                                                                                                                                                                                                                                                                       |
|  **1B-K3**  | Two default gender presets (`male` & `female`), 1024 px face & clothing textures, Nike Heritage Coral-Red Backpack (`red-backpack`), Female twin buns + cyan/white tee + charcoal shorts + white strap sneakers + yellow sling bag, and 6 separated `SkinnedMesh` slots (`BodyMesh`, `HairMesh`, `TopMesh`, `BottomMesh`, `ShoesMesh`, `BagMesh`) | Done (Passed)                                  | [hair_parts.py](tools/character-builder/hair_parts.py), [top_parts.py](tools/character-builder/top_parts.py), [bottom_parts.py](tools/character-builder/bottom_parts.py), [shoe_parts.py](tools/character-builder/shoe_parts.py), [bag_parts.py](tools/character-builder/bag_parts.py), [textures.py](tools/character-builder/textures.py) |
|  **1B-K4**  | Canonical 22-bone `CharacterRig` humanoid armature (`align_roll` axis alignment), slot-aware normalized smooth skin weights, cross-gender bone-name rebinding (`rebindSkinnedMeshByBoneName`), and `/lab` pose test verification                                                                                                                  | Done (Passed)                                  | [rig_builder.py](tools/character-builder/rig_builder.py), [character-avatar.ts](packages/client/src/entities/character-avatar.ts)                                                                                                                                                                                                          |
|  **1B-K5**  | Looping `Idle` (2.0 s), `Walk` (1.0 s), `Run` (0.67 s) skeletal animations with `0.18 s` crossfades, speed normalization (`computeAnimationTimeScale`), `/lab` `Anim: Idle/Walk/Run` switcher, standalone per-item `.glb` exports (`content/characters/parts/{top,bottom,shoes,bag}/<id>.glb`), stale file cleanup & full standardization audit   | Built & Verified — **Awaiting Owner Sign-Off** | [anim_clips.py](tools/character-builder/anim_clips.py), [character-skins.ts](packages/shared/src/constants/character-skins.ts), 31/31 tests + lint + build passing                                                                                                                                                                         |

### Stage 2A – Map from PNG `[Not Started]`

| Sub-Stage | Description                                                                                            | Status      | Notes                                          |
| :-------: | :----------------------------------------------------------------------------------------------------- | :---------- | :--------------------------------------------- |
| **2A.1**  | `tools/map-builder` CLI reading `source.png`, `legend.json`, `map.config.json` + unknown-color warning | Not Started | `pnpm build:map <name>`                        |
| **2A.2**  | Generate floor, water, building walls, and simple trees from map color rules                           | Not Started | Sample map in `content/maps/sample/` first     |
| **2A.3**  | Collision map + world edge boundary + spawn point markers from PNG                                     | Not Started | Matches `packages/shared` collision logic      |
| **2A.4**  | Data-driven client map loader (swap map via `content/maps/` folder only) + `F4` collision debug view   | Not Started | Needs owner map PNG & scale confirmation later |

### Stage 2B – Abeto-Style Environment `[Not Started]`

| Sub-Stage | Description                                                                                                                                                            | Status      | Notes                                             |
| :-------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------- | :------------------------------------------------ |
| **2B.1**  | Optional grayscale `height.png` sloped terrain & terrace support (character + camera surface follow)                                                                   | Not Started | Includes smooth height sampling                   |
| **2B.2**  | Modular Blender-generated `.glb` prop library (`content/props/`: concrete walls, power poles/cables, cones, buoys, fences, stairs, trees, planters, signs, wall lamps) | Not Started | Built via `tools/` pipeline (`K1`–`K5` standards) |
| **2B.3**  | `props.json` placement layer (position/rotation/scale + per-prop collision & climbable stairs) + instancing                                                            | Not Started | Data-driven without code changes                  |
| **2B.4**  | Building roofs, square windows, balconies, road decals, and `/lab` object gallery                                                                                      | Not Started | Extended `/lab` inspection view                   |

### Stage 3 – Core Multiplayer `[Not Started]`

| Sub-Stage | Description                                                                                    | Status      | Notes                                                             |
| :-------: | :--------------------------------------------------------------------------------------------- | :---------- | :---------------------------------------------------------------- |
|  **3.1**  | Versioned `shared/protocol` messages + guest name entry (3–16 chars server-validated)          | Not Started | Enforces room capacity (30 players) & clear full message          |
|  **3.2**  | Authoritative server movement & map collision validation (anti-cheat speed/bounds checks)      | Not Started | Server owns true state                                            |
|  **3.3**  | 15–20 Hz state sync, client-side prediction + ~100 ms remote player interpolation + nameplates | Not Started | Syncs modular loadout (`gender`, `top`, `bottom`, `shoes`, `bag`) |
|  **3.4**  | Auto-reconnect on transient disconnect + `pnpm bots <count>` load test script                  | Not Started | Tested up to 31 bots                                              |

### Stage 4 – Social Interaction `[Not Started]`

| Sub-Stage | Description                                                                                           | Status      | Notes                                      |
| :-------: | :---------------------------------------------------------------------------------------------------- | :---------- | :----------------------------------------- |
|  **4.1**  | Chat box UI, 5-second overhead chat bubbles, XSS sanitization, 120-char & 1 msg/sec rate limit        | Not Started | Room-wide default                          |
|  **4.2**  | Data-driven ID/EN profanity filter (`content/` word list)                                             | Not Started | Editable without code changes              |
|  **4.3**  | 6 skeletal emotes (`wave`, `clap`, `laugh`, `dance`, `agree`, `shake head`) via `content/emotes.json` | Not Started | Authored cleanly on 22-bone `CharacterRig` |
|  **4.4**  | Online player list (`Tab`) with client-side per-player mute                                           | Not Started | Syncs live join/leave                      |

### Stage 5 – Abeto-Style UI & Feel `[Not Started]`

| Sub-Stage | Description                                                                                                                 | Status      | Notes                                              |
| :-------: | :-------------------------------------------------------------------------------------------------------------------------- | :---------- | :------------------------------------------------- |
|  **5.1**  | Loading progress screen & guest/character onboarding start screen                                                           | Not Started | Syncs selections with multiplayer state            |
|  **5.2**  | Complete paper-sticker HUD (Menu, Music, Outfit, Emote SVG icons + Settings menu)                                           | Not Started | Follows Abeto paper-sticker CSS & theme tokens     |
|  **5.3**  | Procedural Web Audio ambient sound + footsteps (no large audio downloads)                                                   | Not Started | Music & SFX volume sliders saved in `localStorage` |
|  **5.4**  | Graphics quality presets (`low`/`medium`/`high`), camera sensitivity, responsive portrait/landscape safe-areas & PWA polish | Not Started | Tested on desktop + Android tablet/phone           |

### Stage 6 – Optimization & Resilience `[Not Started]`

| Sub-Stage | Description                                                                                                    | Status      | Notes                                           |
| :-------: | :------------------------------------------------------------------------------------------------------------- | :---------- | :---------------------------------------------- |
|  **6.1**  | Texture/mesh compression, instancing for repeated props/buildings, frustum culling, simple LOD, mobile DPR cap | Not Started | Target < 10 MB initial load                     |
|  **6.2**  | Auto quality preset + adaptive FPS scaling on low-spec devices + friendly error overlays                       | Not Started | Clear error UI for WebGL/network/version errors |
|  **6.3**  | `pnpm perf` 30-bot 10-minute benchmark + client memory leak verification + `docs/perf-report.md`               | Not Started | Multi-device test matrix (Windows + Android)    |

### Stage 7 – Deploy `[Not Started]`

| Sub-Stage | Description                                                                                            | Status      | Notes                                    |
| :-------: | :----------------------------------------------------------------------------------------------------- | :---------- | :--------------------------------------- |
|  **7.1**  | Server `Dockerfile`, `/health` endpoint, structured logging, & production `wss://` client build config | Not Started | Environment-variable driven              |
|  **7.2**  | Automatic CI/CD deploy workflow on `main`                                                              | Not Started | Runs lint, test, and build before deploy |
|  **7.3**  | Step-by-step `docs/guides/deploy.md` for Cloudflare / Fly.io (or VPS) & HTTPS public verification      | Not Started | Tested across separate networks          |

### Stage 8 – Factory Foundation `[Not Started]`

| Sub-Stage | Description                                                                                 | Status      | Notes                                             |
| :-------: | :------------------------------------------------------------------------------------------ | :---------- | :------------------------------------------------ |
|  **8.1**  | Entity-Component schema in `packages/shared` for data-driven world objects (`content/`)     | Not Started | Modular extension without rewriting world systems |
|  **8.2**  | Server 10 Hz factory tick skeleton & object broadcast to all connected clients              | Not Started | Verified identical across multiple tabs           |
|  **8.3**  | Sample factory machine box GLB + factory feature design template & ADRs (`docs/decisions/`) | Not Started | Ready for Stage 8+ factory gameplay decisions     |
