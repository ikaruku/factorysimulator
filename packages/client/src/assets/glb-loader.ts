import * as THREE from "three";
import { GLTFLoader, type GLTF } from "three/examples/jsm/loaders/GLTFLoader.js";
import * as SkeletonUtils from "three/examples/jsm/utils/SkeletonUtils.js";
import { getToonGradientMap } from "../visuals/toon-material";

export interface LoadedGlbAsset {
  scene: THREE.Object3D;
  animations: THREE.AnimationClip[];
}

const loader = new GLTFLoader();
const gltfCache = new Map<string, Promise<GLTF>>();

/** Converts a loaded glTF material to the shared Abeto MeshToonMaterial. */
export function convertMaterialToToon(material: THREE.Material): THREE.Material {
  if (material instanceof THREE.MeshToonMaterial) {
    material.gradientMap = getToonGradientMap();
    return material;
  }

  const std = material as THREE.MeshStandardMaterial;
  const toon = new THREE.MeshToonMaterial({
    color: std.color ? std.color.clone() : new THREE.Color(0xffffff),
    map: std.map ?? null,
    alphaMap: std.alphaMap ?? null,
    transparent: Boolean(std.transparent),
    opacity: typeof std.opacity === "number" ? std.opacity : 1,
    side: std.side ?? THREE.FrontSide,
    vertexColors: Boolean(std.vertexColors),
    gradientMap: getToonGradientMap(),
  });
  toon.name = material.name;
  return toon;
}

/** Applies toon shading and shadow flags to every mesh in an imported glTF hierarchy. */
export function applyToonStyleToObject(root: THREE.Object3D, receiveShadows = false): void {
  root.traverse((node) => {
    if (!(node instanceof THREE.Mesh)) return;
    node.castShadow = true;
    node.receiveShadow = receiveShadows;
    if (node instanceof THREE.SkinnedMesh) {
      node.frustumCulled = false;
    }

    if (Array.isArray(node.material)) {
      node.material = node.material.map((m) => convertMaterialToToon(m));
    } else if (node.material) {
      node.material = convertMaterialToToon(node.material);
    }
  });
}

/** Loads and caches a GLB asset, returning an independent skinned clone with toon materials. */
export async function loadToonGlb(url: string): Promise<LoadedGlbAsset> {
  let pending = gltfCache.get(url);
  if (!pending) {
    pending = loader.loadAsync(url);
    gltfCache.set(url, pending);
  }

  const gltf = await pending;
  const clonedScene = SkeletonUtils.clone(gltf.scene);
  applyToonStyleToObject(clonedScene);
  return {
    scene: clonedScene,
    animations: gltf.animations,
  };
}
