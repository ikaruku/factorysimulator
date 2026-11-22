import * as THREE from "three";
import {
  CAMERA_CONFIG,
  clamp,
  getDefaultLoadoutForGender,
  type BagSkinId,
  type BottomSkinId,
  type CharacterGender,
  type CharacterLoadout,
  type ShoesSkinId,
  type TopSkinId,
} from "@factory-simulator/shared";
import { WorldRenderer } from "../core/renderer";
import { isWebGl2Supported, showGraphicsError } from "../core/webgl-check";
import { CharacterAvatar } from "../entities/character-avatar";
import { ABETO_PALETTE } from "../theme/abeto-theme";
import {
  loadCharacterLoadoutPreference,
  saveCharacterLoadoutPreference,
} from "../ui/settings-panel";
import { OutlineComposer } from "../visuals/outline-composer";
import { createProceduralSky } from "../visuals/procedural-sky";
import { createToonMaterial } from "../visuals/toon-material";
import { buildLabMarkup } from "./lab-markup";

function populateLabScene(
  scene: THREE.Scene,
  initialLoadout: CharacterLoadout,
): {
  update: (dt: number) => void;
  setLoadout: (loadout: CharacterLoadout) => void;
  setForcedClip: (clipName: string | null) => void;
} {
  scene.background = new THREE.Color(ABETO_PALETTE.SKY_HORIZON);
  const sky = createProceduralSky(160);
  scene.add(sky.mesh);

  scene.add(new THREE.HemisphereLight(ABETO_PALETTE.HEMI_SKY, ABETO_PALETTE.HEMI_GROUND, 0.72));
  const sun = new THREE.DirectionalLight(ABETO_PALETTE.SUN_LIGHT, 1.55);
  sun.position.set(16, 24, 14);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.bias = -0.0006;
  sun.shadow.normalBias = 0.06;
  const r = 18;
  sun.shadow.camera.left = -r;
  sun.shadow.camera.right = r;
  sun.shadow.camera.top = r;
  sun.shadow.camera.bottom = -r;
  scene.add(sun);

  const ground = new THREE.Mesh(
    new THREE.BoxGeometry(22, 0.4, 14),
    createToonMaterial(ABETO_PALETTE.GRASS_LIGHT),
  );
  ground.position.set(0, -0.2, 0);
  ground.receiveShadow = true;
  scene.add(ground);

  const concretePad = new THREE.Mesh(
    new THREE.BoxGeometry(10.5, 0.08, 4.2),
    createToonMaterial(ABETO_PALETTE.CONCRETE_LIGHT),
  );
  concretePad.position.set(0, 0.04, 1.5);
  concretePad.receiveShadow = true;
  scene.add(concretePad);

  const rotations = [Math.PI, Math.PI / 2, 0, -Math.PI / 2];
  const characters: CharacterAvatar[] = [];
  rotations.forEach((rotY, idx) => {
    const char = new CharacterAvatar(initialLoadout);
    char.group.position.set(-3.0 + idx * 2.0, 0.08, 1.8);
    char.group.rotation.y = rotY;
    scene.add(char.group);
    characters.push(char);
  });

  const wall = new THREE.Mesh(
    new THREE.BoxGeometry(6, 2.8, 0.8),
    createToonMaterial(ABETO_PALETTE.CONCRETE_MID),
  );
  wall.position.set(-2.5, 1.4, -3.2);
  wall.castShadow = true;
  wall.receiveShadow = true;
  scene.add(wall);

  const sphere = new THREE.Mesh(
    new THREE.SphereGeometry(0.95, 20, 16),
    createToonMaterial(ABETO_PALETTE.FOLIAGE_DARK),
  );
  sphere.position.set(2.4, 0.95, -2.8);
  sphere.castShadow = true;
  sphere.receiveShadow = true;
  scene.add(sphere);

  const cylinder = new THREE.Mesh(
    new THREE.CylinderGeometry(0.65, 0.65, 2.2, 16),
    createToonMaterial(ABETO_PALETTE.TURQUOISE_ACCENT),
  );
  cylinder.position.set(4.8, 1.1, -2.5);
  cylinder.castShadow = true;
  cylinder.receiveShadow = true;
  scene.add(cylinder);

  const accentBox = new THREE.Mesh(
    new THREE.BoxGeometry(1.1, 1.1, 1.1),
    createToonMaterial(ABETO_PALETTE.ORANGE_ACCENT),
  );
  accentBox.position.set(6.8, 0.55, -2.0);
  accentBox.castShadow = true;
  accentBox.receiveShadow = true;
  scene.add(accentBox);

  return {
    update: (dt: number) => {
      sky.update(dt);
      for (const char of characters) {
        char.updateAnimation(0, false, dt);
      }
    },
    setLoadout: (loadout: CharacterLoadout) => {
      for (const char of characters) {
        void char.setLoadout(loadout);
      }
    },
    setForcedClip: (clipName: string | null) => {
      for (const char of characters) {
        char.setForcedClipName(clipName);
      }
    },
  };
}

/** Launches the Stage 1B /lab side-by-side visual comparison page. */
export function startLabPage(): void {
  if (!isWebGl2Supported()) {
    showGraphicsError("Your browser does not support WebGL2 required for the /lab preview.");
    return;
  }

  let currentLoadout = loadCharacterLoadoutPreference();

  document.getElementById("game-root")?.classList.add("hidden");
  const labRoot = document.getElementById("lab-root");
  if (!labRoot) return;
  labRoot.classList.remove("hidden");
  labRoot.innerHTML = buildLabMarkup(currentLoadout);

  const canvasWrap = document.getElementById("lab-canvas");
  if (!canvasWrap) return;

  const scene = new THREE.Scene();
  const content = populateLabScene(scene, currentLoadout);

  const aspect = (canvasWrap.clientWidth || 800) / Math.max(canvasWrap.clientHeight || 600, 1);
  const camera = new THREE.PerspectiveCamera(56, aspect, 0.1, CAMERA_CONFIG.FAR_PLANE_M);

  let composer: OutlineComposer | null = null;
  const worldRenderer = new WorldRenderer(canvasWrap, (nextAspect, dims) => {
    camera.aspect = nextAspect;
    camera.updateProjectionMatrix();
    composer?.resize(dims.width, dims.height, dims.pixelRatio);
  });

  composer = new OutlineComposer(worldRenderer.renderer, scene, camera);
  const initDims = worldRenderer.getDimensions();
  composer.resize(initDims.width, initDims.height, initDims.pixelRatio);

  const maleBtn = document.getElementById("lab-gender-male");
  const femaleBtn = document.getElementById("lab-gender-female");
  const topSelect = document.getElementById("lab-slot-top") as HTMLSelectElement | null;
  const bottomSelect = document.getElementById("lab-slot-bottom") as HTMLSelectElement | null;
  const shoesSelect = document.getElementById("lab-slot-shoes") as HTMLSelectElement | null;
  const bagSelect = document.getElementById("lab-slot-bag") as HTMLSelectElement | null;

  const syncControls = (): void => {
    maleBtn?.setAttribute("aria-pressed", String(currentLoadout.gender === "male"));
    femaleBtn?.setAttribute("aria-pressed", String(currentLoadout.gender === "female"));
    if (topSelect) topSelect.value = currentLoadout.top;
    if (bottomSelect) bottomSelect.value = currentLoadout.bottom;
    if (shoesSelect) shoesSelect.value = currentLoadout.shoes;
    if (bagSelect) bagSelect.value = currentLoadout.bag;
  };
  syncControls();

  const applyNewLoadout = (next: CharacterLoadout): void => {
    currentLoadout = next;
    saveCharacterLoadoutPreference(currentLoadout);
    syncControls();
    content.setLoadout(currentLoadout);
  };

  maleBtn?.addEventListener("click", () => {
    applyNewLoadout(getDefaultLoadoutForGender("male" satisfies CharacterGender));
  });
  femaleBtn?.addEventListener("click", () => {
    applyNewLoadout(getDefaultLoadoutForGender("female" satisfies CharacterGender));
  });
  topSelect?.addEventListener("change", () => {
    applyNewLoadout({ ...currentLoadout, top: topSelect.value as TopSkinId });
  });
  bottomSelect?.addEventListener("change", () => {
    applyNewLoadout({ ...currentLoadout, bottom: bottomSelect.value as BottomSkinId });
  });
  shoesSelect?.addEventListener("change", () => {
    applyNewLoadout({ ...currentLoadout, shoes: shoesSelect.value as ShoesSkinId });
  });
  bagSelect?.addEventListener("change", () => {
    applyNewLoadout({ ...currentLoadout, bag: bagSelect.value as BagSkinId });
  });

  let orbitYaw = 0.08;
  let orbitPitch = 0.24;
  let dragging = false;
  let lastX = 0;
  let lastY = 0;

  canvasWrap.addEventListener("pointerdown", (e) => {
    dragging = true;
    lastX = e.clientX;
    lastY = e.clientY;
  });
  window.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    orbitYaw -= (e.clientX - lastX) * 0.006;
    orbitPitch = clamp(orbitPitch + (e.clientY - lastY) * 0.006, 0.06, 1.15);
    lastX = e.clientX;
    lastY = e.clientY;
  });
  window.addEventListener("pointerup", () => {
    dragging = false;
  });

  const outlineBtn = document.getElementById("lab-outline-btn");
  outlineBtn?.addEventListener("click", () => {
    if (!composer) return;
    const next = !composer.isOutlinesEnabled();
    composer.setOutlinesEnabled(next);
    outlineBtn.textContent = next ? "Outlines: ON" : "Outlines: OFF";
  });

  const animOrder: readonly ("Idle" | "Walk" | "Run")[] = ["Idle", "Walk", "Run"];
  let animIndex = 0;
  const animBtn = document.getElementById("lab-anim-btn");
  animBtn?.addEventListener("click", () => {
    animIndex = (animIndex + 1) % animOrder.length;
    const nextAnim = animOrder[animIndex] ?? "Idle";
    animBtn.setAttribute("aria-pressed", String(nextAnim !== "Idle"));
    animBtn.textContent = `Anim: ${nextAnim}`;
    content.setForcedClip(nextAnim === "Idle" ? null : nextAnim);
  });

  const slider = document.getElementById("lab-thickness") as HTMLInputElement | null;
  const valLabel = document.getElementById("lab-thickness-val");
  slider?.addEventListener("input", () => {
    const px = Number(slider.value);
    composer?.setThickness(px);
    if (valLabel) valLabel.textContent = `${px.toFixed(1)}px`;
  });

  let lastTime = performance.now();
  const renderFrame = (now: number): void => {
    requestAnimationFrame(renderFrame);
    if (document.hidden) {
      lastTime = now;
      return;
    }
    const dt = Math.min((now - lastTime) / 1000, 0.1);
    lastTime = now;
    content.update(dt);

    const dist = 6.2;
    camera.position.set(
      Math.sin(orbitYaw) * Math.cos(orbitPitch) * dist,
      0.95 + Math.sin(orbitPitch) * dist,
      1.6 + Math.cos(orbitYaw) * Math.cos(orbitPitch) * dist,
    );
    camera.lookAt(0, 0.92, 1.6);
    composer?.render();
  };
  requestAnimationFrame(renderFrame);
}
