# Project Rules for AI

Top reference: `docs/game-plan.md`. If anything conflicts with it, that document wins. Also read `docs/standards.md` and `docs/guides/asset-pipeline.md`.

- **Language: English everywhere** (code, comments, documentation, UI text, commit messages, error messages). Chat with the user may follow the user's language.
- Work through the stages in order (0, 1A, 1B, 2A, 2B, 3-8). Do not start the next stage (or sub-stage) until the user declares the current one passed.
- **3D Asset Standard (characters, props, buildings, maps, machines):** Do not stack crude Three.js primitives for hero/world assets. Build assets via reproducible headless Blender Python scripts in `tools/`, export `.glb` to `content/`, render multi-angle previews to inspect quality first, load via the shared Three.js GLB + toon material pipeline, and craft complex assets incrementally through gates K1 (pipeline) -> K2 (base silhouette/proportions) -> K3 (details/UV/materials) -> K4 (rigging/collision) -> K5 (animations/polish).
- **Character & Outfit Modularity Standard (Mandatory):**
  - Default outline thickness is `1.0px` (`VISUAL_CONFIG.OUTLINE_THICKNESS_PX = 1.0`), paired with 2-tone Abeto cel shading (`TOON_LEVELS = 2`).
  - Characters support gender selection (`male` and `female`) with 2 canonical default designs:
    - `male` (default skin): shaggy slate-teal hair, oversized orange pullover hoodie with folded hood & grey drawstrings, Nike Heritage coral-red backpack (`red-backpack`, `"Nike Red Backpack"`), cropped charcoal joggers, white crew socks, chunky high-top dark sneakers (`content/characters/male/character.glb` & `content/characters/default/character.glb`).
    - `female` (default skin): dark bob hair with twin buns & yellow ties, A-line cyan/off-white color-blocked T-shirt, golden-yellow crossbody sling bag, charcoal shorts (`celana pendek`), white crew socks, chunky off-white high-top strap sneakers (`content/characters/female/character.glb`).
  - Every character `.glb` and builder script MUST keep the 6 modular mesh slots separated (`BodyMesh`, `HairMesh`, `TopMesh` [pakaian atas], `BottomMesh` [pakaian bawah], `ShoesMesh` [sepatu], `BagMesh` [tas]) bound to the shared `CharacterRig` skeleton so outfit parts can always be swapped or extended with new skins independently.
- `client` and `server` may only import from `shared`, never from each other.
- Network message types and names live only in `packages/shared/src/protocol`.
- The server owns state; game data lives in `content/`; no magic numbers (use configuration).
- One file, one responsibility, at most ~300 lines.
- TypeScript strict, no `any`.
- Naming: files `kebab-case`, classes `PascalCase`, functions/variables `camelCase`, constants `UPPER_SNAKE_CASE`.
- Commands: `pnpm dev`, `pnpm test`, `pnpm lint`, `pnpm build`, `pnpm setup:blender`, `pnpm build:character`.
- Conventional Commits; update `CHANGELOG.md` and READMEs each stage.
- Done means: lint and tests pass, dev runs without errors, docs updated, user has tried it.
- Secrets and local caches (`tools/.cache/`) never go into git.
