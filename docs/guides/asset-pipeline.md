# 3D Asset & Map Pipeline Guide

This guide defines the standard process for building **all** 3D assets in Factory Simulator: characters, props, buildings, factory machines, and modular map pieces.

## 1. Staged Asset Workflow

Every complex 3D asset or visual domain follows the same incremental gates so problems are caught early:

1. **K1 – Pipeline & Loader:** Verify the headless Blender script exports a valid `.glb` into `content/`, renders turnaround previews, and loads cleanly in the client (`/lab` and main world).
2. **K2 – Base Silhouette & Proportions:** Build a clean, continuous base mesh with accurate real-world meter scale and proportions before adding fine details. Review in `/lab`.
3. **K3 – Details, Materials, UV Textures & Modular Slots:** Add sculpted 3D contours, cloth folds, clean UV textures, `1.0px` outline tuning, and modular slot separation. Inspect 6-angle Blender turnaround renders (`front`, `right`, `back`, `left`, `three_quarter`, `head_closeup`) before user review in `/lab`.
4. **K4 – Rigging / Collision / Sockets:** Add humanoid armature + smooth skin weights (for characters) or collision bounds & attachment sockets (for buildings, props, and machines). Review poses/bounds in `/lab`.
5. **K5 – Animation & In-World Polish:** Author looping skeletal/object animations (`Idle`, `Walk`, `Run`, machine cycles), hook up smooth transitions in the client, and test in the live 3D world.

Do not skip a gate until the owner approves the current sub-stage.

## 2. Technical Asset Conventions

| Rule              | Requirement                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------- |
| Format            | glTF 2.0 binary (`.glb`)                                                                     |
| Coordinate        | Y-up, `1 unit = 1 meter`, front facing `-Z`, base resting on `y = 0`                         |
| Size limit        | Max `5 MB` per `.glb` file                                                                   |
| Textures          | Embedded PNG/WebP, max `2048 px` (`1024 px` recommended for mobile)                          |
| Shading           | 2-tone stepped Abeto `MeshToonMaterial` (`TOON_LEVELS = 2`, `minLuminance = 196`)            |
| Outline thickness | `1.0 px` default (`VISUAL_CONFIG.OUTLINE_THICKNESS_PX = 1.0`, crease threshold `0.36`)       |
| Previews          | Every build renders 6-angle preview PNGs into `tools/.cache/previews/` for visual inspection |

## 3. Standardized Modular Character & Gender Architecture

All player characters MUST follow the modular slot standard so gender presets and future cosmetic skins can be mixed and extended without altering the base character rig:

### A. Two Canonical Default Gender Designs

1. **Male Default (`male` — Default game skin):**
   - Output: `content/characters/male/character.glb` (also copied to `content/characters/default/character.glb`).
   - Design: Shaggy dark slate-teal hair (`#25323A`), oversized orange pullover hoodie (`#DE6F45`) with plump folded hood, V-collar, grey drawstrings, and sculpted long-sleeve elbow/forearm creases, crimson-red backpack (`#A83A3E`) with 3D white `"Hi"` + bars graphic and thick shoulder straps, baggy cropped charcoal joggers (`#22262B`), bare lower calves, off-white crew socks (`#DCE0D8`), and chunky high-top dark sneakers (`#1E2228`) with twin white stripes.
2. **Female Default (`female`):**
   - Output: `content/characters/female/character.glb`.
   - Design: Dark bob hair (`#1F242B`) with swept bangs and upper-back twin buns with golden-yellow hair ties (`#E9A82B`), A-line oversized cyan (`#2FA6CC`) / off-white (`#E4E8E0`) color-blocked short-sleeve T-shirt, golden-yellow crossbody sling bag (`#E9A82B`) at the front-left hip, baggy cropped charcoal joggers (`#22262B`), bare lower calves, off-white crew socks (`#DCE0D8`), and chunky high-top dark sneakers (`#1E2228`) with twin white stripes.

### B. Six Mandatory Separated SkinnedMesh Slots

Every character `.glb` must export **6 separate named mesh nodes** parented and skinned to the shared `CharacterRig` skeleton (and mirrored in modular Python files inside `tools/character-builder/`):

| glTF Node Name | Builder Module    | Role / Slot Description                                                       |
| -------------- | ----------------- | ----------------------------------------------------------------------------- |
| `BodyMesh`     | `body_mesh.py`    | Base human body, forearms, hands, bare lower calves, sculpted head & face UVs |
| `HairMesh`     | `hair_parts.py`   | Hair style mesh (`shaggy_male`, `twin_buns_female`, etc.)                     |
| `TopMesh`      | `top_parts.py`    | Upper garment / _Pakaian Atas_ (`orange-hoodie`, `cyan-colorblock-tee`, etc.) |
| `BottomMesh`   | `bottom_parts.py` | Lower garment / _Pakaian Bawah_ (`charcoal-joggers`, etc.)                    |
| `ShoesMesh`    | `shoe_parts.py`   | Footwear / _Sepatu_ (`high-top-sneakers`, etc.)                               |
| `BagMesh`      | `bag_parts.py`    | Backpack or sling bag / _Tas_ (`red-backpack`, `yellow-crossbody`, or hidden) |

### C. Sculpting Quality Standard

- Never use plain smooth circular lathes for garments or heads.
- Sculpt explicit 3D anatomical curves (V-oval front jawline, horizontal under-jaw plane, nasion notch, upturned nose tip, exposed ears, thumb + curled finger hands) and intentional 3D fabric fold ridges with sharp crease rings so the normal-crease outline shader draws crisp interior cloth fold lines.

## 4. Running the Pipeline

- Ensure portable Blender 4.2 LTS is cached locally (gitignored in `tools/.cache/blender/`):
  ```bash
  pnpm setup:blender
  ```
- Build both modular character presets (`male` and `female`) and their 6-angle previews:
  ```bash
  pnpm build:character
  ```
- Open `http://localhost:5173/lab` to inspect both `Male (Default)` and `Female (Default)` from four sides and test swapping `TopMesh`, `BottomMesh`, `ShoesMesh`, and `BagMesh` slots.
