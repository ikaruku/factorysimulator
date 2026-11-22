import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { ensureBlender } from "../asset-pipeline/ensure-blender.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "../..");
const SCRIPT_PATH = path.join(__dirname, "build_character.py");
const MAX_GLB_BYTES = 5 * 1024 * 1024;

const GENDERS = ["male", "female"];
const EXPECTED_PARTS_BY_GENDER = {
  male: [
    "top/orange-hoodie.glb",
    "bottom/charcoal-joggers.glb",
    "shoes/high-top-sneakers.glb",
    "bag/red-backpack.glb",
  ],
  female: [
    "top/cyan-colorblock-tee.glb",
    "bottom/charcoal-shorts.glb",
    "shoes/white-strap-sneakers.glb",
    "bag/yellow-crossbody.glb",
  ],
};

const blenderExe = ensureBlender();

const charactersDir = path.join(REPO_ROOT, "content", "characters");
const partsDir = path.join(charactersDir, "parts");
const previewRootDir = path.join(REPO_ROOT, "tools", ".cache", "previews", "character");

// Remove legacy duplicate 'content/characters/default' folder and stale preview files
const legacyDefaultDir = path.join(charactersDir, "default");
if (fs.existsSync(legacyDefaultDir)) {
  fs.rmSync(legacyDefaultDir, { recursive: true, force: true });
}
if (fs.existsSync(previewRootDir)) {
  fs.rmSync(previewRootDir, { recursive: true, force: true });
}
fs.mkdirSync(partsDir, { recursive: true });

for (const gender of GENDERS) {
  const outputGlb = path.join(charactersDir, gender, "character.glb");
  const previewDir = path.join(previewRootDir, gender);
  fs.mkdirSync(path.dirname(outputGlb), { recursive: true });
  fs.mkdirSync(previewDir, { recursive: true });

  console.log(`[character-builder] Building modular '${gender}' character & standalone parts...`);
  execFileSync(
    blenderExe,
    [
      "--background",
      "--factory-startup",
      "--python-exit-code",
      "1",
      "--python",
      SCRIPT_PATH,
      "--",
      "--gender",
      gender,
      "--output",
      outputGlb,
      "--preview-dir",
      previewDir,
      "--parts-dir",
      partsDir,
    ],
    { stdio: "inherit" },
  );

  if (!fs.existsSync(outputGlb)) {
    throw new Error(`Character GLB was not created at ${outputGlb}`);
  }

  const stat = fs.statSync(outputGlb);
  if (stat.size > MAX_GLB_BYTES) {
    throw new Error(
      `Character GLB (${gender}) exceeds 5 MB limit (${(stat.size / 1024 / 1024).toFixed(2)} MB)`,
    );
  }

  console.log(
    `[character-builder] Exported ${path.relative(REPO_ROOT, outputGlb)} (${(stat.size / 1024).toFixed(1)} KB)`,
  );

  for (const relPart of EXPECTED_PARTS_BY_GENDER[gender]) {
    const partGlb = path.join(partsDir, relPart);
    if (!fs.existsSync(partGlb)) {
      throw new Error(`Expected standalone modular part GLB was not created at ${partGlb}`);
    }
    const partStat = fs.statSync(partGlb);
    if (partStat.size > MAX_GLB_BYTES) {
      throw new Error(`Modular part GLB (${relPart}) exceeds 5 MB limit`);
    }
    console.log(
      `[character-builder] Exported part ${path.relative(REPO_ROOT, partGlb)} (${(partStat.size / 1024).toFixed(1)} KB)`,
    );
  }
}
