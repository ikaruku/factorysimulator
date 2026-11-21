import * as THREE from "three";
import { WORLD_CONFIG, type ColliderBox } from "@factory-simulator/shared";

interface MarkerBoxSpec {
  x: number;
  z: number;
  width: number;
  height: number;
  depth: number;
  color: number;
}

export interface TestWorld {
  scene: THREE.Scene;
  colliders: readonly ColliderBox[];
}

const SKY_COLOR = 0x87d8e8;
const FOG_NEAR_M = 45;
const FOG_FAR_M = 190;

const SIZE_MARKERS: readonly MarkerBoxSpec[] = [
  { x: 6, z: -6, width: 1, height: 1, depth: 1, color: 0xf97316 },
  { x: -8, z: -10, width: 2, height: 2, depth: 2, color: 0x38bdf8 },
  { x: 14, z: -16, width: 3, height: 4, depth: 3, color: 0x22c55e },
  { x: -18, z: 12, width: 4, height: 6, depth: 4, color: 0xeab308 },
  { x: 25, z: 20, width: 2, height: 3, depth: 5, color: 0xec4899 },
  { x: -30, z: -28, width: 5, height: 5, depth: 5, color: 0x6366f1 },
  { x: 0, z: -40, width: 6, height: 3, depth: 2, color: 0x14b8a6 },
];

/** Builds the Stage 1A test world: sky, fog, lighting, 200x200m floor, and solid size markers. */
export function createTestWorld(): TestWorld {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(SKY_COLOR);
  scene.fog = new THREE.Fog(SKY_COLOR, FOG_NEAR_M, FOG_FAR_M);

  const hemiLight = new THREE.HemisphereLight(0xf0f9ff, 0x475569, 0.85);
  scene.add(hemiLight);

  const sunLight = new THREE.DirectionalLight(0xfffbeb, 1.35);
  sunLight.position.set(35, 55, 25);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.set(1024, 1024);
  const shadowRange = 60;
  sunLight.shadow.camera.left = -shadowRange;
  sunLight.shadow.camera.right = shadowRange;
  sunLight.shadow.camera.top = shadowRange;
  sunLight.shadow.camera.bottom = -shadowRange;
  sunLight.shadow.camera.near = 5;
  sunLight.shadow.camera.far = 160;
  scene.add(sunLight);

  const size = WORLD_CONFIG.TEST_FLOOR_SIZE_M;
  const floorGeometry = new THREE.PlaneGeometry(size, size);
  floorGeometry.rotateX(-Math.PI / 2);
  const floorMaterial = new THREE.MeshStandardMaterial({
    color: 0xb7df9c,
    roughness: 0.9,
  });
  const floor = new THREE.Mesh(floorGeometry, floorMaterial);
  floor.receiveShadow = true;
  scene.add(floor);

  const grid = new THREE.GridHelper(size, WORLD_CONFIG.GRID_DIVISIONS, 0x64748b, 0x94a3b8);
  grid.position.y = 0.01;
  scene.add(grid);

  const colliders: ColliderBox[] = [];
  for (const spec of SIZE_MARKERS) {
    const geometry = new THREE.BoxGeometry(spec.width, spec.height, spec.depth);
    const material = new THREE.MeshStandardMaterial({ color: spec.color, roughness: 0.7 });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(spec.x, spec.height / 2, spec.z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    scene.add(mesh);

    colliders.push({
      minX: spec.x - spec.width / 2,
      maxX: spec.x + spec.width / 2,
      minZ: spec.z - spec.depth / 2,
      maxZ: spec.z + spec.depth / 2,
    });
  }

  return { scene, colliders };
}
