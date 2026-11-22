import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "../..");
const BLENDER_VERSION = "4.2.16";
const BLENDER_DIR_NAME = `blender-${BLENDER_VERSION}-windows-x64`;
const BLENDER_URL = `https://download.blender.org/release/Blender4.2/${BLENDER_DIR_NAME}.zip`;
const CACHE_DIR = path.join(REPO_ROOT, "tools", ".cache", "blender");
const ZIP_PATH = path.join(CACHE_DIR, `${BLENDER_DIR_NAME}.zip`);
const PORTABLE_EXE = path.join(CACHE_DIR, BLENDER_DIR_NAME, "blender.exe");

/**
 * Resolves an installed Blender executable, downloading Blender 4.2 LTS portable
 * into tools/.cache/blender/ on Windows if not already present.
 */
export function ensureBlender() {
  if (process.env.BLENDER_PATH && fs.existsSync(process.env.BLENDER_PATH)) {
    return process.env.BLENDER_PATH;
  }

  try {
    execFileSync("blender", ["--version"], { stdio: "ignore" });
    return "blender";
  } catch {
    // System blender not on PATH; fall through to portable cache.
  }

  if (fs.existsSync(PORTABLE_EXE)) {
    return PORTABLE_EXE;
  }

  if (process.platform !== "win32") {
    throw new Error(
      "Blender not found on PATH. Install Blender 4.2 LTS or set BLENDER_PATH to the binary.",
    );
  }

  fs.mkdirSync(CACHE_DIR, { recursive: true });

  if (!fs.existsSync(ZIP_PATH)) {
    console.log(`[asset-pipeline] Downloading Blender ${BLENDER_VERSION} LTS portable...`);
    execFileSync("curl.exe", ["-L", "--fail", "--progress-bar", "-o", ZIP_PATH, BLENDER_URL], {
      stdio: "inherit",
    });
  }

  console.log(`[asset-pipeline] Extracting Blender ${BLENDER_VERSION} to ${CACHE_DIR}...`);
  execFileSync(
    "powershell.exe",
    [
      "-NoProfile",
      "-Command",
      `Expand-Archive -Path '${ZIP_PATH}' -DestinationPath '${CACHE_DIR}' -Force`,
    ],
    { stdio: "inherit" },
  );

  if (!fs.existsSync(PORTABLE_EXE)) {
    throw new Error(`Expected Blender executable not found at ${PORTABLE_EXE}`);
  }

  fs.rmSync(ZIP_PATH, { force: true });
  console.log(`[asset-pipeline] Blender ready at ${PORTABLE_EXE}`);
  return PORTABLE_EXE;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const exe = ensureBlender();
  const versionOut = execFileSync(exe, ["--version"], { encoding: "utf8" }).trim().split("\n")[0];
  console.log(`[asset-pipeline] Using ${exe} (${versionOut})`);
}
