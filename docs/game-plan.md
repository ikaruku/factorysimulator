# Open World Multiplayer Game Plan (Factory Theme)

Nov 20, 2026 · @andikarukun (English translation of the original Indonesian plan; this is the project's reference standard)

## Summary

The AI can write almost all of the code and map processing itself; the owner only provides the PNG map, reviews the results, and holds the hosting accounts.

- **Game:** a 3D world explored together. Players appear as characters, walk around, meet other players, chat, and use emotes.
- **Current focus:** open world only. Factory simulator mechanics are not built yet, but the foundation is prepared.
- **Map:** 1 default map, generated from a PNG provided by the owner.
- **Style:** inspired by Messenger by Abeto: bright low-poly 3D, minimal UI, chat bubbles above characters. Based on a general impression of that site, so correct any element you specifically want.

## Division of work

The AI writes and assembles all code and assets; the owner decides direction, tries the results, and holds the hosting accounts.

| Work                                  | Done by | Notes                                          |
| ------------------------------------- | ------- | ---------------------------------------------- |
| Client code (3D, controls, UI)        | AI      | Delivered as a complete project                |
| Multiplayer server code               | AI      | Node.js + Colyseus                             |
| PNG to 3D map                         | AI      | Via color rules, see next section              |
| Low-poly characters and objects       | AI      | Built from basic shapes, no hand-made models   |
| Multiplayer logic tests with bots     | AI      | Simulates dozens of connections                |
| Feel testing in browser and real phones | Owner | The AI cannot feel controls on the owner's device |
| Design decisions and corrections      | Owner   | Via this document or chat                      |
| Hosting accounts, domain, deploy      | Owner   | AI prepares scripts and step-by-step guides    |

One limitation: in a plain chat session the AI cannot install packages or run public servers; the code is delivered as a project the owner runs with a few commands. When the AI runs, tests, and fixes directly on the owner's computer (as in a coding agent), that limitation is reduced.

## Map from PNG

A PNG is a 2D image, so it is converted into a 3D world with color rules: each color on the map becomes one type of surface or object. The result suits a simple block map, not detailed models.

Example color rules (editable):

| Color in PNG     | Result in the 3D world                  | Walkable? |
| ---------------- | --------------------------------------- | --------- |
| Light green      | Grass                                   | Yes       |
| Gray             | Road or floor                           | Yes       |
| Blue             | Water                                   | No        |
| Brown or black   | Building, standard height 6 m           | No        |
| Dark green       | Tree                                    | No        |
| Red dot          | Player spawn point                      | Yes       |

Processing steps:

1. Read the PNG and group pixels by color.
2. Set the scale (**assumption:** 1 pixel = 0.5 m).
3. Convert color areas into floor, building walls, and objects.
4. Build the collision map from non-walkable areas.
5. Save the result as map data that can be swapped at any time.

Ideal PNG: top-down view (not tilted or isometric), 1024 to 2048 pixels, flat colors without gradients or text, accompanied by a color legend. Illustrated maps with lots of detail or tilted perspective cannot be converted accurately. For such a PNG the AI interprets it roughly and asks for corrections.

## Technology

All choices are free or cheap and light enough for desktop and phone browsers.

| Part              | Choice                              | Reason                                |
| ----------------- | ----------------------------------- | ------------------------------------- |
| Client            | TypeScript + Vite + Three.js        | Light, 3D directly in the browser     |
| Multiplayer       | Node.js + Colyseus (WebSocket)      | Room synchronization already available |
| Collision         | Grid from PNG + three-mesh-bvh      | Fast, uses the same map data          |
| UI and HUD        | HTML/CSS over the canvas            | Easy to change and responsive         |
| Assets            | Built in code, then exported glTF/GLB | No dependency on external models    |
| Client hosting    | Cloudflare Pages                    | Free at hobby scale                   |
| Server hosting    | Small VPS or Fly.io/Railway         | About 5 to 10 USD per month (estimate) |

## Architecture and principles

The project is split into three separate packages (client, server, shared) so each part can change without breaking the others. Six principles apply to all code:

1. **Single source of truth:** network types and message names exist only in the `shared` package.
2. **The server is in control:** real position and state live on the server; the client only sends input and renders results.
3. **Data-driven:** maps, emotes, and configuration are loaded from the `content/` folder, not written in code. Changing a map means changing a folder.
4. **Small modules:** one file, one responsibility, maximum about 300 lines.
5. **Entity-component world objects:** factory features are later added as new components without tearing up the old ones.
6. **No magic numbers:** speeds, room capacity, building height, and similar values are stored in one configuration file.

## Folder structure

One repository (monorepo) with simple rules: code in `packages/`, game data in `content/`, documentation in `docs/`, helper tools in `tools/`.

```text
factory-simulator/
├── README.md                  # summary and how to run
├── CLAUDE.md                  # project rules for AI (see Standards)
├── CHANGELOG.md               # change log per version
├── package.json               # root workspace (pnpm)
├── pnpm-workspace.yaml
├── .editorconfig  .gitignore  .env.example
├── .github/workflows/         # CI: lint, test, build
├── docs/
│   ├── architecture.md        # system overview
│   ├── standards.md           # code and naming standards
│   ├── decisions/             # important decisions (0001-choose-threejs.md, ...)
│   └── guides/                # guides: add map, add emote, etc.
├── content/                   # all game data, no code
│   ├── maps/
│   │   └── default/
│   │       ├── source.png     # original PNG from the owner
│   │       ├── legend.json    # color rules to objects
│   │       └── map.config.json# scale, building height, spawn points
│   └── emotes.json
├── packages/
│   ├── shared/src/            # used by client and server
│   │   ├── protocol/          # network message types and names
│   │   ├── constants/         # game configuration
│   │   └── utils/
│   ├── client/
│   │   ├── index.html
│   │   ├── public/            # static assets: audio, fonts
│   │   └── src/
│   │       ├── core/          # game loop, renderer, input
│   │       ├── world/         # map loader, collision
│   │       ├── entities/      # local player and other players
│   │       ├── network/       # connection and interpolation
│   │       ├── ui/            # HUD, chat, loading, settings
│   │       └── main.ts
│   └── server/
│       └── src/
│           ├── rooms/         # WorldRoom
│           ├── systems/       # movement, chat, validation
│           └── index.ts
├── tools/
│   └── map-builder/           # converts PNG to map data
└── tests/                     # end-to-end and load tests (bots)
```

Dependency rule: `client` and `server` may use `shared`, but must not use each other. Code used by both always moves to `shared`.

## Permanent standards

These standards are copied to `docs/standards.md` and `CLAUDE.md` in the project so every later work session follows them. The AI cannot remember them between conversations; the files in the project keep them in force.

| Area             | Standard                                                                                                     |
| ---------------- | ------------------------------------------------------------------------------------------------------------ |
| Code language    | TypeScript strict mode, no `any`                                                                             |
| Naming           | Files and folders `kebab-case`, classes `PascalCase`, functions and variables `camelCase`, constants `UPPER_SNAKE_CASE` |
| Text language    | **English for everything** (code, comments, documentation, UI text, commits)                                 |
| Formatting       | Automatic Prettier and ESLint; one command `pnpm lint`                                                       |
| Standard commands | `pnpm dev` (run), `pnpm test`, `pnpm lint`, `pnpm build`                                                    |
| Git              | Branches `main` (stable), `dev` (work), `feature/<name>`; Conventional Commits (`feat:`, `fix:`, `docs:`)    |
| Versioning       | SemVer (e.g. 0.1.0) and `CHANGELOG.md` updated each release                                                  |
| Network protocol | Defined only in `shared/protocol`, has a version number; mismatched versions are rejected with a clear message |
| Tests            | Unit tests for core logic (collision, interpolation, protocol); 30-connection bot test before release        |
| Documentation    | Each main folder has a short `README.md`; major decisions recorded in `docs/decisions/`                      |
| Assets           | GLB models max 5 MB per object, textures max 2048 px, always compressed; located in `content/` or `public/`  |
| Configuration    | Via `.env` and config files; secrets never enter git                                                         |

**Definition of done** for every stage: `pnpm lint` and `pnpm test` pass, `pnpm dev` runs without errors, README and `CHANGELOG.md` are updated, and the owner has tried the result.

## Maintenance guide

The most frequent tasks have fixed paths, so small changes do not spread to many places.

| Task                | Steps                                                                                    | Parts touched                              |
| ------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------ |
| Change or add a map | Put PNG, legend, and config in `content/maps/<name>/`, then run `pnpm build:map <name>`  | Only `content/` and `tools/`               |
| Add an emote        | Add an entry in `content/emotes.json` and its animation                                  | Only `content/` and `client/ui`            |
| Add a message type  | Define in `shared/protocol`, then handle on server, then on client                       | `shared`, `server`, `client` (in this order) |
| Add a factory feature | New component in `shared`, system on `server`, display on `client`, record decision in `docs/decisions/` | Stage 8 onward              |
| Fix a bug           | Write a failing test first, then fix until it passes                                     | Related module and `tests/`                |
| Release a version   | Bump version, fill `CHANGELOG.md`, git tag, deploy                                       | Root and CI                                |

## Visual target (Abeto reference image)

The reference image sent by the owner is the visual benchmark. It is broken into elements that each have their own stage and test gate, so similarity can be judged gradually, not all at the end.

| Element in the reference image                        | How it is realized                                                   | Stage   | Estimated similarity       |
| ----------------------------------------------------- | -------------------------------------------------------------------- | ------- | -------------------------- |
| Layered flat colors and thick outlines on every object | Toon shader with 3 to 4 color levels and outlines in Three.js        | 1B      | High                       |
| Palette: turquoise, dark green, bluish gray, orange accents | A theme file and color grading                                  | 1B      | High                       |
| Flat shadows with hard edges                          | One-level hard dark shadow, no gradient                              | 1B      | High                       |
| Turquoise sky with painterly strokes                  | Procedural sky shader: turquoise gradient with textured cloud bands  | 1B      | Medium to high             |
| Low third-person camera with wide field of view       | Camera settings, tunable via configuration                           | 1B      | High                       |
| Character with backpack, dark hair, red shoes         | Procedural character with cartoon proportions, hair, backpack, shoes | 1B      | Medium (simple, less detailed than the image) |
| Sloped roads, stairs, bridges                         | Optional height map and modular object pieces                        | 2B      | Medium                     |
| Concrete walls, power poles, cables, cones, buoys, buildings | Procedural object library and object placement layer          | 2B      | Medium (simple shapes)     |
| Detailed textures: stains, cracks, wall patches       | Basic textures and simple decals                                     | 2B and 6 | Low to medium             |
| White paper-sticker style buttons with offset shadow  | HTML/CSS and SVG icons                                               | 5       | High                       |

**Limits to know:** a top-down PNG only holds a floor plan, not detailed shapes. Without a 3D artist, the environment will look clean and consistently cartoonish, but simpler than the reference image. The hardest parts to match are the character and building details. Artist-made GLB models (for example from Blender) can replace any object or character at any time via the `content/` folder, without changing code.

**How to judge similarity:** from Stage 1B a `/lab` page shows the character, objects, palette, and HUD side by side. Compare it with the reference image and write down the parts that still feel different.

**What to prepare before Stage 1B and 2A:**

- [ ] Node.js 20 LTS and pnpm installed (see Stage 0).
- [ ] Map PNG: top-down, 1024 to 2048 pixels, flat colors, with color legend and spawn points.
- [ ] Height map (grayscale PNG, optional) if there are sloped roads or stairs.
- [ ] Extra Abeto screenshots: start screen, clothing menu, emotes, day or night mood, if you want everything matched.
- [ ] Test devices: laptop and phone models.

## Device support

The game runs in the browser, so one codebase serves Windows laptops, Android tablets, and Android smartphones, with no app install. Each device gets suitable controls and quality level.

| Device             | Supported browsers                   | Controls                                           | Display                                   |
| ------------------ | ------------------------------------ | -------------------------------------------------- | ----------------------------------------- |
| Windows laptop     | Chrome, Edge, Firefox (latest)       | Keyboard WASD and mouse; touch screen also works   | Wide screen, high quality                 |
| Android tablet     | Chrome                               | Virtual joystick and drag to look, larger buttons  | Mainly landscape, medium quality          |
| Android smartphone | Chrome                               | Virtual joystick and on-screen buttons, chat via on-screen keyboard | Portrait and landscape, low to medium quality |

iPhone and iPad (Safari) essentially work because they use a browser, but are not the main test target (assumption, changeable).

**Technical rules that apply in all stages:**

- **WebGL2:** supported by all modern browsers. WebGPU is not used because it is not yet universal.
- **Automatic controls:** the game detects touch or mouse and keyboard, and can switch while playing (for example a touch-screen laptop).
- **Adaptive quality:** on first open the game measures FPS for a few seconds and picks a low, medium, or high preset. Presets control render resolution, outlines, shadows, and view distance. Players can change it manually in settings.
- **Responsive layout:** touch buttons at least 44 pixels, respect safe areas (notch), work in portrait and landscape.
- **Memory limits:** textures max 2048 px on laptops and 1024 px on phones, total initial load under 10 MB, so low-RAM phones do not crash.
- **Touch behavior:** pinch-zoom, pull-to-refresh, and text selection are disabled in the game area; the screen does not sleep while playing (Screen Wake Lock).
- **Power saving:** FPS capped at 60, automatically dropping to 30 if the device is slow or hot, and rendering stops when the tab is not visible.
- **Mobile networks:** small compressed messages, and automatic reconnect when the signal drops.
- **Installable (PWA):** can be added to the home screen with icon and fullscreen mode; done together with Stage 5 and 7.
- **Unsupported device message:** when WebGL2 is unavailable, the player sees a clear explanation, not a blank screen.

**Device testing rule:** from Stage 1A, every test gate is tried on at least a laptop and one phone or tablet, with results recorded per device. Stage 6 runs the full test on all the owner's devices.

**Honest limitation:** the AI has no access to Android devices for testing, so results on phones and tablets depend on the owner's tests. Very low-spec phones (RAM below about 3 GB) are likely comfortable only on the low quality preset.

## Build stages

Building is split into eleven test gates (Stage 0, 1A, 1B, 2A, 2B, and 3 to 8). Each stage ends at one test gate: the owner can run and try the result before the next stage starts.

**Flow of each gate:**

1. The AI hands over the code, a change summary, and the test steps for that stage.
2. The owner runs the test steps and ticks the pass criteria in that stage's section.
3. The owner gives the result: **Pass**, **Pass with notes**, or **Fail** (include the error message or screenshot if any).
4. The AI fixes until it passes. The next stage does not start until the owner declares a pass.

Honest note: in a plain chat session the AI cannot install packages or run a browser, so the code has never been run before handover, and errors on the first attempt are likely; the owner's test results are material for fixes. Pure logic tests (collision, interpolation, protocol) are still written as unit tests.

Everything the AI can prepare itself (characters, sample maps, test bots, sounds, scripts, configuration) it builds itself, so the owner does not need to provide any assets to test Stage 0, 1A, 1B, and 3 to 6. What must come from the owner is written under **Needed from the owner** in each stage.

| Stage                  | What you can test                                                          | Work size |
| ---------------------- | -------------------------------------------------------------------------- | --------- |
| 0. Project setup       | Project runs on your computer, page shows server connected                 | Small     |
| 1A. Movement foundation | Character walks in an empty world, on desktop and phone                   | Medium    |
| 1B. Abeto-style visuals | `/lab` page and test world with cartoon outlined look, compared with the reference image | Large |
| 2A. Map from PNG       | Your map appears as a 3D world with collision                              | Large     |
| 2B. Abeto-style environment | Sloped roads, stairs, and objects like cones, poles, and buoys on your map | Large |
| 3. Core multiplayer    | Several tabs see each other, plus 20 to 30 bots                            | Large     |
| 4. Social interaction  | Chat, bubbles, emotes, player list                                         | Medium    |
| 5. Abeto-style UI      | Full flow from link to entering the world, including on phone              | Large     |
| 6. Optimization and resilience | Performance report with 30 bots, stable FPS                        | Medium    |
| 7. Deploy              | Public link friends can open                                               | Medium    |
| 8. Factory foundation  | Sample object appears identically for all players                          | Medium    |

Stage 8 only prepares the foundation; factory mechanics are built after the owner decides the features. Each stage counts as finished only when it meets the Definition of done in the Standards section.

### Stage 0 – Project setup and standards

**Goal:** the repository is ready and all standard rules are installed before a single feature line is written.

**AI does:**

- Folder structure per the Folder structure section, with a pnpm workspace.
- Strict TypeScript, ESLint, Prettier, and Vitest.
- Standard scripts: `pnpm dev`, `pnpm test`, `pnpm lint`, `pnpm build`.
- Files `README.md`, `CLAUDE.md`, `docs/standards.md`, `CHANGELOG.md`, and `.env.example`.
- CI workflow (lint, test, build) in `.github/workflows/`.
- A client start page showing "Server: connected" from the Colyseus server (connection test).

**AI prepares itself:** all the configuration and scripts above; the owner creates no files.

**How you test:**

1. Install Node.js 20 LTS and pnpm (installation steps are written in `README.md`).
2. Open the project folder in a terminal, run `pnpm install`.
3. Run `pnpm dev`, then open `http://localhost:5173` in a browser.
4. Run `pnpm lint` and `pnpm test` in the terminal.

**Passes when:**

- [ ] The page opens and shows "Server: connected".
- [ ] `pnpm lint` and `pnpm test` finish without errors.
- [ ] The folder structure matches what is written in this document.

**Needed from the owner:** Node.js and pnpm installed on the computer; a GitHub account if CI should run (can be postponed until Stage 7).

### Stage 1A – Movement foundation (single player)

**Goal:** a simple 3D world with a character that is comfortable to move, on desktop and phone.

**AI does:**

- Three.js scene with lighting, a simple sky, and light fog.
- 200 × 200 m test floor with a few boxes as size markers.
- Low-poly character with idle and walk animations.
- Third-person camera that can rotate (hold right mouse button, or drag on phone).
- WASD controls, Shift to run, and a virtual joystick on phone.
- Game loop with a fixed time step, so movement is the same on all devices.
- FPS counter toggled with the F3 key.
- Walk and run speed in the config file (initial assumption: 4 m/s and 7 m/s).

**AI prepares itself:** the character and test floor are built in code, no assets from the owner.

**How you test:**

1. Run `pnpm dev`, open `http://localhost:5173`.
2. Move the character with WASD, try running with Shift, rotate the camera.
3. Press F3 and note the FPS.
4. On phone: run `pnpm dev --host`, open the laptop's IP address from the phone browser (same Wi-Fi), then try the joystick.

**Passes when:**

- [ ] The character moves smoothly in all directions and the animation switches with movement.
- [ ] The camera follows the character and does not go under the floor.
- [ ] FPS is 60 on laptop and about 30 or more on phone.
- [ ] The joystick works on phone and the screen does not scroll or zoom.
- [ ] Speed and camera distance feel right (if not, write the numbers you want).

**Needed from the owner:** judgment of movement and camera feel.

### Stage 1B – Abeto-style visuals

**Goal:** the test world and character already appear in the reference image style: flat cartoon colors, thick outlines, and turquoise sky, before the real map comes in.

**AI does:**

- Toon shader with 3 to 4 color levels per surface, no smooth gradients.
- Thick outlines on all objects and characters (edge detection pass based on depth and surface direction); thickness tunable in configuration.
- Hard one-level dark shadows with crisp edges.
- Procedural sky: turquoise gradient with textured cloud strokes, moving slowly.
- A color theme file whose palette is taken from the reference image, so the whole game uses the same colors.
- Low third-person camera with wide field of view like the reference image (values in configuration).
- New cartoon-proportioned character: dark hair with bangs, white T-shirt, wide black pants, turquoise backpack, red shoes; idle and walk animations.
- A `/lab` page showing the character from four sides, color palette, material samples, sky, and HUD button samples side by side for comparison with the reference image.
- The Stage 1A test world gets walls and colored boxes as material for judging outlines and shadows.
- An option to turn off outlines in settings, for weak phones.

**AI prepares itself:** everything is built in code, no assets from the owner.

**How you test:**

1. Run `pnpm dev` and open `http://localhost:5173/lab`.
2. Place the reference image beside the screen, then compare color, line thickness, sky, shadows, and character.
3. Open the test world, walk and rotate the camera; outlines must be stable and not flicker.
4. On phone, check FPS (F3). If below 30, turn off outlines in settings and note the difference.
5. Give a similarity rating from 1 to 5 and write the parts that still differ.

**Passes when:**

- [ ] Outlines appear on all objects and the character, with thickness similar to the reference.
- [ ] Flat layered colors without smooth gradients, with hard shadows.
- [ ] The sky has a turquoise stroke style, not a plain color.
- [ ] The character is recognizable by its key features (backpack, hair, red shoes).
- [ ] FPS meets the target on laptop (60) and phone (about 30, outlines off allowed).
- [ ] Your similarity rating is 4 or more; if lower, the AI fixes for up to two rounds before continuing.

**Needed from the owner:** the similarity rating with a list of differing parts, and extra Abeto screenshots if any.

### Stage 2A – Map from PNG

**Goal:** your default map appears as a 3D world that can be explored and cannot be walked through.

**AI does:**

- A `tools/map-builder` tool that reads `source.png`, `legend.json`, and `map.config.json`, then produces map data.
- Creation of floor, water, building walls, and simple trees from each color.
- A collision map, so the character slides along walls and does not pass through buildings or water.
- Spawn points from markers in the PNG, and a world boundary at the map edge.
- A client map loader that can be swapped just by changing the folder in `content/maps/`.
- A clear warning when a color in the PNG is not in the legend.
- Debug mode: F4 shows collision areas.

**AI prepares itself:** a sample PNG with legend in `content/maps/sample/`, so the tool and collision are tested before your PNG comes in. If your PNG has no legend, the AI guesses color rules from the image and shows the guess for you to correct.

**How you test:**

1. Put your PNG as `content/maps/default/source.png` (and the legend if any).
2. Run `pnpm build:map default`, then `pnpm dev`.
3. Compare the world view with the PNG: location of roads, water, buildings, and trees.
4. Try walking into a building, into water, and to the map edge. Press F4 to see collision areas.

**Passes when:**

- [ ] The element placement in the world matches the PNG.
- [ ] The character cannot pass through buildings, trees, water, or the world edge.
- [ ] The character appears at the spawn point.
- [ ] World size and building height feel reasonable (if not, write the scale you want).
- [ ] Changing the map only requires changing a folder, no code changes.

**Needed from the owner:** the map PNG (top-down, 1024 to 2048 pixels, flat colors), the color legend if any, and scale confirmation.

### Stage 2B – Abeto-style environment

**Goal:** your map feels like a city corner in the reference image: sloped roads, walls, stairs, and small objects around.

**AI does:**

- Optional height map support (`height.png`, grayscale: dark low, bright high) for sloped roads and terraces; character and camera follow the surface.
- An object layer `props.json` to place objects with position, rotation, and scale, without touching code.
- A procedural object library in `content/props/`: concrete walls, power poles and cables, traffic cones, buoys, fences, stairs, trees, plant pots, signs, and wall lamps. Shapes are simple and uniform in cartoon style.
- Buildings from the PNG automatically get roofs, square windows, and simple balconies.
- Simple decals: white road markings, stains, and wall patches.
- Collision rules for each object (which can be passed through) and stairs that can be climbed smoothly.
- Instancing for repeated objects to keep FPS up.
- The `/lab` page extended into a gallery of all objects.

**AI prepares itself:** the object library above, plus a sample height map and `props.json` in `content/maps/sample/`, so it can be tested before your files come in.

**How you test:**

1. Open `/lab` and inspect each object; shapes must be recognizable.
2. Run `pnpm build:map default` (with your `height.png` or the sample), then walk on sloped roads and climb stairs.
3. Add one object via `props.json`, reload, and make sure it appears without code changes.
4. Compare the look of roads, walls, and objects with the reference image, then rate similarity 1 to 5.

**Passes when:**

- [ ] Cones, power poles, buoys, walls, and stairs are recognizable by shape.
- [ ] The character follows sloped surfaces without floating or sinking, and the camera does not go through the ground.
- [ ] Stairs can be climbed without getting stuck.
- [ ] Objects can be added and moved only via files in `content/`.
- [ ] FPS stays on target.
- [ ] Your environment similarity rating is 3 or more (realistic target without a 3D artist; see limits in the Visual target section).

**Needed from the owner:** a height map if your roads slope, a list of objects that must be on the map, and GLB models if you or an artist make them.

### Stage 3 – Core multiplayer

**Goal:** several players are in the same world and see each other move smoothly.

**AI does:**

- A Colyseus server with one world room of 30 players capacity (assumption, changeable in configuration).
- Network message protocol in `shared/protocol`, with a version number.
- Guest entry with a name (3 to 16 characters, validated on the server).
- The server checks movement: maximum speed and collision using the same map as the client, so players cannot cheat.
- Position and animation sync 15 to 20 times per second; the local player moves immediately (prediction), other players are smoothed with about 100 ms interpolation.
- Players joining and leaving, name above the character's head, a clear message when the room is full.
- Automatic reconnect if the connection drops briefly.
- Bot script: `pnpm bots <count>` to simulate many players.

**AI prepares itself:** the bot script with its random walk pattern; you do not need to invite other people to test this stage.

**How you test:**

1. Run `pnpm dev`, open two tabs (one normal window and one incognito) with different names.
2. Move the character in one tab, make sure it is seen moving in the other. Close one tab; its character must disappear in the other.
3. Run `pnpm bots 20`, then open one tab and watch 20 bots walk.
4. Stop the server (Ctrl+C) then run it again; the client must reconnect without reloading the page.
5. Run `pnpm bots 31` and make sure the 31st player gets a room full message.

**Passes when:**

- [ ] Two tabs see each other and other players' movement looks smooth, not choppy.
- [ ] A player who leaves disappears immediately from other tabs.
- [ ] 20 bots show without noticeable lag.
- [ ] The client reconnects after the server is restarted.
- [ ] The 31st player is rejected with a clear message.

**Needed from the owner:** confirmation of room capacity and entry method (guest with name). Testing with friends is optional and only practical after Stage 7.

### Stage 4 – Social interaction

**Goal:** players can communicate and express themselves.

**AI does:**

- Chat box and chat bubbles above characters' heads (shown for about 5 seconds).
- Chat rules: maximum 120 characters and one message per second per player; text is always sanitized to be safe from code injection (XSS).
- Profanity filter for Indonesian and English; the word list is in `content/` so it is easy to change.
- Emotes via menu or hotkey, initially six (wave, clap, laugh, dance, agree, shake head); list in `content/emotes.json`.
- Online player list (Tab key) with an option to mute specific players on the client side.
- Chat visible to the whole room (assumption; can be changed to distance-based).

**AI prepares itself:** the initial profanity word list and emote animations from simple shapes; you can add or change them yourself.

**How you test:**

1. Open two tabs with different names and send a message from one; it must appear in the other tab's chat box and bubble.
2. Try each emote and see the result in the other tab.
3. Send a profane word and a message longer than 120 characters; the result must be filtered or rejected.
4. Send messages in quick succession; the excess must be held back.
5. Press Tab and try muting another player.

**Passes when:**

- [ ] Messages reach other players in under about 1 second.
- [ ] Bubbles appear above the right character and disappear on their own.
- [ ] The six emotes work and are visible to other players.
- [ ] The filter and message limiter work.
- [ ] The player list is accurate and the mute feature works.

**Needed from the owner:** the list of emotes you want and the chat rule (whole room or distance-based).

### Stage 5 – Abeto-style UI and feel

**Goal:** the flow from opening the link to entering the world feels like a complete game, on desktop and phone.

**AI does:**

- Loading screen with a progress indicator.
- Start screen (onboarding): choose a name and simple character look (assumption: 8 color choices and 4 accessories).
- Minimal HUD with chat, emote, and settings buttons.
- Settings menu: music and effects volume, graphics quality (low, medium, high), and camera sensitivity; choices saved in the browser.
- Ambient sound and footstep effects generated via Web Audio, so no audio files are needed.
- Responsive layout for phones, including landscape and safe areas (notch).
- One theme file (colors, fonts, spacing) so the visual style can be changed from one place.

HUD style follows the reference image:

- White paper-sticker style buttons with slightly rounded corners, a thin outline, and a shadow offset to the bottom right.
- Simple hand-drawn style icons (menu, music, clothing, emote) in grayish turquoise, arranged in the right corner of the screen.
- Press effect: the button shifts slightly toward the shadow when touched.
- All icons are SVG, so they are sharp on any screen and their colors follow the theme file.

**AI prepares itself:** all the visual elements and sounds above; if you have your own music or font, just place them in `client/public/`.

**How you test:**

1. Open from the start on desktop: loading, start screen, entering the world. Repeat on phone.
2. Change sound and quality settings, then reload the page; choices must persist.
3. Rotate the phone to landscape and portrait, make sure buttons are not covered or cut off.
4. Compare the feel with the Abeto references you like.

**Passes when:**

- [ ] The flow from link to entering the world runs without blank pages or errors.
- [ ] Name, color, and accessory choices are visible to other players.
- [ ] Settings persist after reload.
- [ ] The look is comfortable on phone (portrait and landscape).
- [ ] The visual feel is close enough to what you want (write the parts still lacking).
- [ ] HUD buttons look like stickers as in the reference image and respond when pressed.

**Needed from the owner:** extra Abeto screenshots (start screen, clothing menu, emotes, settings menu), because the AI currently holds only one reference image; custom music or fonts if any.

### Stage 6 – Optimization and resilience

**Goal:** the game stays smooth and stable with many players, and does not break when problems occur.

**AI does:**

- Texture and mesh compression, and instancing for similar trees and buildings.
- Frustum culling and simple LOD; render resolution limit on phones.
- Error handling: clear messages when WebGL is unsupported, the connection fails, or the protocol version does not match.
- A `pnpm perf` script that runs 30 bots for 10 minutes and writes a report (CPU, memory, server bandwidth) to `docs/perf-report.md`.
- Memory leak checks on the client in long sessions.
- Targets (assumption): 60 FPS on a mid-range laptop, about 30 FPS on a mid-range phone, initial load under 10 MB, and server CPU under 50% with 30 bots on a small VPS.
- Device test matrix: Windows laptop, Android tablet, and Android smartphone (portrait and landscape), with per-device results in `docs/perf-report.md`.
- Automatic quality preset selection and adaptive FPS limit, tested on weak devices.

**AI prepares itself:** the load test script and its report format.

**How you test:**

1. Run `pnpm perf` and read the generated `docs/perf-report.md`.
2. Run `pnpm bots 30`, open one tab, press F3, and note FPS on laptop and phone.
3. Leave one tab open for about 15 minutes; FPS and memory must not get worse.
4. Try opening in an old browser or with WebGL disabled to see the error message.

**Passes when:**

- [ ] FPS meets the target on your devices with 30 bots.
- [ ] The performance report exists and its numbers are within target.
- [ ] No performance drop or memory spike after 15 minutes.
- [ ] Error messages show neatly, not as a blank screen.
- [ ] The game runs and is comfortably controlled on a Windows laptop, Android tablet, and Android smartphone, each per the Device support table.

**Needed from the owner:** the list of benchmark devices (laptop and phone models), because FPS targets are adjusted to them.

### Stage 7 – Deploy

**Goal:** the game can be opened via a public link by other people.

**AI does:**

- Dockerfile for the server and build configuration for the client.
- Production configuration (secure `wss://` WebSocket address, environment variables, connection limits).
- CI/CD workflow: every change to `main` passes tests and is deployed automatically.
- Health check endpoint and basic logging.
- A complete guide `docs/guides/deploy.md` with step-by-step instructions and screenshots for you to match.

**AI prepares itself:** all configuration files and the guide. The AI cannot create accounts, pay, or set up domains on your behalf, so you do those steps following the guide.

**How you test:**

1. Follow `docs/guides/deploy.md` to the end.
2. Open the public link on laptop and on phone with mobile data.
3. Invite one or two friends to open the same link, then make sure you see each other and can chat.
4. Reload the page and try joining again.

**Passes when:**

- [ ] The public link opens over HTTPS without security warnings.
- [ ] Players on different devices and networks see each other and can chat.
- [ ] Changes to `main` are deployed to production automatically.
- [ ] The health endpoint responds and server logs are readable.

**Needed from the owner:** Cloudflare and Fly.io accounts (or a VPS), a payment method if hosting is paid, a free domain or subdomain, and the game name.

### Stage 8 – Factory foundation

**Goal:** the open world is ready to grow into a factory simulator without tearing down what exists.

**AI does:**

- An entity-component system in `shared` for world objects.
- The server reads world objects from `content/` and broadcasts them to all players.
- One sample object (a marker machine box) that looks the same to all players.
- A server tick skeleton (about 10 times per second) for future production logic.
- Decision records in `docs/decisions/` and a factory design document template (resources, machines, conveyors) for you to fill in.

**AI prepares itself:** the sample object and the design document template.

**How you test:**

1. Run `pnpm dev`, open two tabs, and make sure the sample object appears at the same position.
2. Change the object's position in `content/`, restart the server, and see the object move without code changes.
3. Add a second sample object only via a file in `content/`.

**Passes when:**

- [ ] The sample object appears the same in all tabs.
- [ ] Objects can be added and moved via `content/` alone.
- [ ] All tests and the Definition of done are met.

**Needed from the owner:** the decision on the first factory feature (which resource, which machine, and how players interact) after this stage passes; that is where the factory phase begins.

## Assumptions and open questions

Tick the ones you have agreed to, and change the text if needed. Unticked items are treated as undecided.

- [ ] The game is 3D using Three.js, not 2D.
- [ ] Phone players must also be able to play (WASD on desktop, virtual joystick on phone).
- [ ] A capacity of 30 players per room is enough.
- [ ] Entry as a guest with a name is enough, no login.
- [ ] The character is simple low-poly made by the AI, not the owner's model.
- [ ] Map scale 1 pixel = 0.5 m and standard building height 6 m.
- [ ] Hobby hosting budget (free up to about 10 USD per month).
- [ ] Game name and branding: none yet; the working name is Factory Simulator.
- [ ] Factory mechanics postponed until the open world is finished.
- [ ] Visual style: flat cartoon with outlines like the reference image; the environment is a simplified version, and artist-made models are optional.
- [ ] Target devices: Windows laptop (Chrome, Edge, Firefox), Android tablet and smartphone (Chrome); iPhone and iPad are not specifically tested.

## How to make corrections

You can edit this document directly, then tell the AI; your changes are always treated as authoritative.

1. **Edit directly:** change the text, tables, or ticks above as you wish.
2. **Comment:** highlight the part to correct and write a comment, and the AI replies in the same comment.
3. **Chat:** reply in chat, for example "continue" or "change stage 4".
4. **Send the map PNG:** attach it in chat with the color legend and scale if any. After that the AI starts from Stage 1 and 2.
