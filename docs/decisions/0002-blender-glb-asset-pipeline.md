# 0002 - Blender Headless GLB Asset Pipeline

## Decision

All 3D assets (characters, props, buildings, factory machines, and modular map pieces) are built via reproducible Python scripts executed by headless **Blender 4.2 LTS (portable)** and exported as **glTF 2.0 binary (`.glb`)** files into `content/`.

The client loads `.glb` assets through a unified Three.js `GLTFLoader` + `AnimationMixer` pipeline (`packages/client/src/assets/`) and automatically applies the shared Abeto toon shading (`MeshToonMaterial` + stepped `gradientMap`) so every asset looks visually consistent with the procedural sky and outline pass.

## Rationale

- Stacking raw Three.js primitives in TypeScript causes disjointed joints, harsh outline seams between overlapping shapes, and rigid limb animations.
- Blender headless gives true continuous subdivision modeling, clean UV unwrapping, smooth armature skinning, and looping keyframe animation clips inside standard `.glb` files.
- Every asset generator script can also render automated multi-angle turnaround previews (`front`, `right`, `back`, `three-quarter`) so quality is verified before handing over to the user in `/lab`.
- Artists can replace any generated `.glb` in `content/` at any time without modifying client or server code.

## Asset Conventions (Mandatory)

- **Format:** glTF 2.0 `.glb` (binary), Y-up, scale `1 unit = 1 meter`.
- **Orientation:** Front faces `-Z`, origin `(0, 0, 0)` rests on the ground plane (`y = 0`).
- **Outlines & Shading:** `1.0 px` default outline thickness (`OUTLINE_THICKNESS_PX = 1.0`), 2-tone stepped cel shading (`TOON_LEVELS = 2`).
- **Modular Character Slots & Standalone Part GLBs:** Every character `.glb` exports 6 separate named `SkinnedMesh` nodes bound to the canonical 22-bone `CharacterRig`: `BodyMesh`, `HairMesh`, `TopMesh` (upper garment), `BottomMesh` (lower garment), `ShoesMesh` (footwear), and `BagMesh` (bag), with 2 default gender presets (`content/characters/male/character.glb` and `content/characters/female/character.glb`). Additionally, every outfit item is exported as its own standalone `.glb` file under `content/characters/parts/{top,bottom,shoes,bag}/<id>.glb` and loaded on demand via `assetPath` in `character-skins.ts`.
- **Budgets:** Max `5 MB` per `.glb`, textures max `2048 px` (`1024 px` target for mobile), compressed.
- **Storage:**
  - `content/characters/{male,female}/character.glb`
  - `content/characters/parts/{top,bottom,shoes,bag}/<id>.glb`
  - `content/props/<name>/<name>.glb`
  - `content/buildings/<name>/<name>.glb`
  - `content/maps/<name>/...`
- **Generator tools:** `tools/<domain>-builder/` (e.g. `tools/character-builder/`, `tools/map-builder/`).
- **Local tool cache:** `tools/.cache/` (gitignored; holds portable Blender binary and temporary preview renders).
