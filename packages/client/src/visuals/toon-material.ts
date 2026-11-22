import * as THREE from "three";
import { VISUAL_CONFIG } from "@factory-simulator/shared";

let cachedGradientMap: THREE.DataTexture | null = null;

/**
 * Generates discrete brightness levels (0..255) for stepped toon shading
 * without smooth gradients.
 */
export function buildToonGradientBytes(
  levels: number = VISUAL_CONFIG.TOON_LEVELS,
): Uint8Array<ArrayBuffer> {
  const safeLevels = Math.max(2, Math.floor(levels));
  const data = new Uint8Array(new ArrayBuffer(safeLevels));
  // Bright 2-tone Abeto cel-shading ramp: luminous base tone with crisp non-muddy shadow band
  const minLuminance = 196;
  const maxLuminance = 255;

  for (let i = 0; i < safeLevels; i += 1) {
    const t = i / (safeLevels - 1);
    data[i] = Math.round(minLuminance + t * (maxLuminance - minLuminance));
  }
  return data;
}

/** Returns the shared discrete toon gradient texture. */
export function getToonGradientMap(): THREE.DataTexture {
  if (cachedGradientMap) return cachedGradientMap;

  const bytes = buildToonGradientBytes(VISUAL_CONFIG.TOON_LEVELS);
  const texture = new THREE.DataTexture(bytes, bytes.length, 1, THREE.RedFormat);
  texture.minFilter = THREE.NearestFilter;
  texture.magFilter = THREE.NearestFilter;
  texture.generateMipmaps = false;
  texture.needsUpdate = true;
  cachedGradientMap = texture;
  return texture;
}

/** Creates a crisp flat-shaded cartoon material using the shared toon gradient map. */
export function createToonMaterial(color: number): THREE.MeshToonMaterial {
  return new THREE.MeshToonMaterial({
    color,
    gradientMap: getToonGradientMap(),
  });
}
