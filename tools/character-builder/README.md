# tools/character-builder

Headless Blender 4.2 LTS Python generator that builds:

- Base modular rigged Male & Female character GLBs (`content/characters/male/character.glb` and `content/characters/female/character.glb`) with 6 separated `SkinnedMesh` slots (`BodyMesh`, `HairMesh`, `TopMesh`, `BottomMesh`, `ShoesMesh`, `BagMesh`), the canonical 22-bone `CharacterRig` armature, and seamless looping `Idle`, `Walk`, and `Run` NLA clips.
- Standalone per-item outfit part GLBs (`content/characters/parts/{top,bottom,shoes,bag}/<id>.glb`) bound to `CharacterRig` for on-demand modular outfit loading and future skin expansion.
- Clean multi-angle turnaround + `Walk`/`Run` pose verification previews in `tools/.cache/previews/character/{male,female}/` (automatically purged of stale previews on each build).

Run from the repository root:

```bash
pnpm build:character
```
