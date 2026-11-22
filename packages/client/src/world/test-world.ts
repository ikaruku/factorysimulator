import * as THREE from "three";
import { WORLD_CONFIG, type ColliderBox } from "@factory-simulator/shared";
import { ABETO_PALETTE } from "../theme/abeto-theme";
import { createProceduralSky, type ProceduralSky } from "../visuals/procedural-sky";
import { createToonMaterial } from "../visuals/toon-material";

interface BlockSpec {
  x: number;
  z: number;
  width: number;
  height: number;
  depth: number;
  color: number;
}

interface PillarSpec {
  x: number;
  z: number;
  radius: number;
  height: number;
  color: number;
}

export interface TestWorld {
  scene: THREE.Scene;
  colliders: readonly ColliderBox[];
  sky: ProceduralSky;
}

const FOG_NEAR_M = 55;
const FOG_FAR_M = 200;

const STAGE_BLOCKS: readonly BlockSpec[] = [
  // Original size markers upgraded to Abeto palette
  { x: 6, z: -6, width: 1, height: 1, depth: 1, color: ABETO_PALETTE.ORANGE_ACCENT },
  { x: -8, z: -10, width: 2, height: 2, depth: 2, color: ABETO_PALETTE.TURQUOISE_ACCENT },
  { x: 14, z: -16, width: 3, height: 4, depth: 3, color: ABETO_PALETTE.FOLIAGE_DARK },
  { x: -18, z: 12, width: 4, height: 6, depth: 4, color: ABETO_PALETTE.YELLOW_ACCENT },
  { x: 25, z: 20, width: 2, height: 3, depth: 5, color: ABETO_PALETTE.CHAR_SHOES },
  { x: -30, z: -28, width: 5, height: 5, depth: 5, color: ABETO_PALETTE.CONCRETE_MID },
  { x: 0, z: -40, width: 6, height: 3, depth: 2, color: ABETO_PALETTE.TURQUOISE_ACCENT },
  // Stage 1B walls & stepped structures for judging outlines and hard shadows
  { x: -5, z: -22, width: 10, height: 3.2, depth: 1.2, color: ABETO_PALETTE.CONCRETE_LIGHT },
  { x: 0, z: -17.5, width: 1.2, height: 3.2, depth: 8, color: ABETO_PALETTE.CONCRETE_LIGHT },
  { x: 10, z: 6, width: 6, height: 2.2, depth: 1.0, color: ABETO_PALETTE.CONCRETE_MID },
  { x: 12.5, z: 3, width: 2, height: 1.2, depth: 2, color: ABETO_PALETTE.ORANGE_ACCENT },
];

const STAGE_PILLARS: readonly PillarSpec[] = [
  { x: -3.5, z: -7, radius: 0.75, height: 3.5, color: ABETO_PALETTE.CONCRETE_LIGHT },
  { x: 4.5, z: 4, radius: 0.55, height: 2.4, color: ABETO_PALETTE.FOLIAGE_DARK },
  { x: -12, z: -16, radius: 1.1, height: 4.5, color: ABETO_PALETTE.TURQUOISE_ACCENT },
];

/** Builds the Stage 1B Abeto-styled test world with toon shading, hard shadows, walls, and sky. */
export function createTestWorld(): TestWorld {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(ABETO_PALETTE.SKY_HORIZON);
  scene.fog = new THREE.Fog(ABETO_PALETTE.SKY_HORIZON, FOG_NEAR_M, FOG_FAR_M);

  const sky = createProceduralSky();
  scene.add(sky.mesh);

  const hemiLight = new THREE.HemisphereLight(
    ABETO_PALETTE.HEMI_SKY,
    ABETO_PALETTE.HEMI_GROUND,
    0.72,
  );
  scene.add(hemiLight);

  const sunLight = new THREE.DirectionalLight(ABETO_PALETTE.SUN_LIGHT, 1.55);
  sunLight.position.set(28, 42, 22);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.set(2048, 2048);
  sunLight.shadow.bias = -0.0006;
  sunLight.shadow.normalBias = 0.06;
  const shadowRange = 55;
  sunLight.shadow.camera.left = -shadowRange;
  sunLight.shadow.camera.right = shadowRange;
  sunLight.shadow.camera.top = shadowRange;
  sunLight.shadow.camera.bottom = -shadowRange;
  sunLight.shadow.camera.near = 5;
  sunLight.shadow.camera.far = 150;
  scene.add(sunLight);

  const size = WORLD_CONFIG.TEST_FLOOR_SIZE_M;
  const floorGeometry = new THREE.PlaneGeometry(size, size);
  floorGeometry.rotateX(-Math.PI / 2);
  const floor = new THREE.Mesh(floorGeometry, createToonMaterial(ABETO_PALETTE.GRASS_LIGHT));
  floor.receiveShadow = true;
  scene.add(floor);

  const grid = new THREE.GridHelper(size, WORLD_CONFIG.GRID_DIVISIONS, 0x73a860, 0x88c273);
  grid.position.y = 0.015;
  grid.userData.skipOutline = true;
  scene.add(grid);

  const colliders: ColliderBox[] = [];
  for (const spec of STAGE_BLOCKS) {
    const geometry = new THREE.BoxGeometry(spec.width, spec.height, spec.depth);
    const mesh = new THREE.Mesh(geometry, createToonMaterial(spec.color));
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

  for (const pillar of STAGE_PILLARS) {
    const geometry = new THREE.CylinderGeometry(pillar.radius, pillar.radius, pillar.height, 14);
    const mesh = new THREE.Mesh(geometry, createToonMaterial(pillar.color));
    mesh.position.set(pillar.x, pillar.height / 2, pillar.z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    scene.add(mesh);

    colliders.push({
      minX: pillar.x - pillar.radius,
      maxX: pillar.x + pillar.radius,
      minZ: pillar.z - pillar.radius,
      maxZ: pillar.z + pillar.radius,
    });
  }

  return { scene, colliders, sky };
}
