# tools/asset-pipeline

Shared headless Blender 4.2 LTS provisioning and multi-angle turnaround preview helpers used by all 3D asset builders (characters, props, buildings, machines, map pieces).

- `ensure-blender.mjs`: ensures portable Blender 4.2 LTS exists in `tools/.cache/blender/` (gitignored).
- `preview_render.py`: renders `front`, `right`, `back`, and `three_quarter` turnaround previews into `tools/.cache/previews/`.
