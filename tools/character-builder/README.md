# tools/character-builder

Headless Blender 4.2 LTS Python generator that builds the modular rigged Male & Female character GLBs (`content/characters/male/character.glb`, `content/characters/default/character.glb`, and `content/characters/female/character.glb`) with 6 separated `SkinnedMesh` slots (`BodyMesh`, `HairMesh`, `TopMesh`, `BottomMesh`, `ShoesMesh`, `BagMesh`), the canonical 22-bone `CharacterRig` armature, seamless looping `Idle`, `Walk`, and `Run` NLA clips, and multi-angle turnaround + pose verification previews in `tools/.cache/previews/character/`.

Run from the repository root:

```bash
pnpm build:character
```
