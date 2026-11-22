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
const blenderExe = ensureBlender();

for (const gender of GENDERS) {
  const outputGlb = path.join(REPO_ROOT, "content", "characters", gender, "character.glb");
  const previewDir = path.join(REPO_ROOT, "tools", ".cache", "previews", "character", gender);
  fs.mkdirSync(path.dirname(outputGlb), { recursive: true });
  fs.mkdirSync(previewDir, { recursive: true });

  console.log(`[character-builder] Building modular '${gender}' character preset...`);
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

  // Copy approved 'male' default character to content/characters/default/character.glb
  if (gender === "male") {
    const defaultGlb = path.join(REPO_ROOT, "content", "characters", "default", "character.glb");
    fs.mkdirSync(path.dirname(defaultGlb), { recursive: true });
    fs.copyFileSync(outputGlb, defaultGlb);
    console.log(
      `[character-builder] Updated default character skin at ${path.relative(REPO_ROOT, defaultGlb)}`,
    );
  }
}
