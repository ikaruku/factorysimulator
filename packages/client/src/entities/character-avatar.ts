import * as THREE from "three";
import {
  ASSET_PATHS,
  CHARACTER_MESH_SLOTS,
  DEFAULT_CHARACTER_LOADOUTS,
  MOVEMENT_CONFIG,
  OUTFIT_SLOT_KEYS,
  getDefaultLoadoutForGender,
  getOutfitSkinOption,
  type CharacterGender,
  type CharacterLoadout,
} from "@factory-simulator/shared";
import { loadToonGlb } from "../assets/glb-loader";

export type CharacterAnimState = "Idle" | "Walk" | "Run";

const RUN_TO_WALK_SPEED_RATIO = MOVEMENT_CONFIG.RUN_SPEED_MPS / MOVEMENT_CONFIG.WALK_SPEED_MPS;

/** Selects the best available skeletal gameplay clip name for the current movement state. */
export function selectAnimationClipName(
  speedRatio: number,
  isRunning: boolean,
  availableNames: readonly string[],
): string | null {
  const gameplayClips = availableNames.filter((name) => name !== "PoseTest");
  const desired: CharacterAnimState = speedRatio <= 0.05 ? "Idle" : isRunning ? "Run" : "Walk";

  if (gameplayClips.includes(desired)) return desired;
  if (desired === "Run" && gameplayClips.includes("Walk")) return "Walk";
  if (gameplayClips.includes("Idle")) return "Idle";
  return gameplayClips[0] ?? availableNames[0] ?? null;
}

/**
 * Computes the AnimationAction playback speed scale so Walk matches walk speed, Run plays
 * at its authored cadence at full sprint (7 m/s), and forced /lab preview clips play at 1.0x.
 */
export function computeAnimationTimeScale(
  clipName: string | null,
  speedRatio: number,
  isForced: boolean,
): number {
  if (isForced || !clipName || clipName === "Idle") return 1;
  if (clipName === "Run") {
    return THREE.MathUtils.clamp(speedRatio / RUN_TO_WALK_SPEED_RATIO, 0.8, 1.25);
  }
  if (clipName === "Walk") {
    return THREE.MathUtils.clamp(speedRatio, 0.65, 1.35);
  }
  return 1;
}

/** Resolves the GLB asset path for a given character gender preset. */
export function getCharacterGlbPath(gender: CharacterGender): string {
  return gender === "female" ? ASSET_PATHS.FEMALE_CHARACTER_GLB : ASSET_PATHS.MALE_CHARACTER_GLB;
}

/**
 * Rebinds a donor `SkinnedMesh` onto the live bone hierarchy of `baseScene` by matching
 * every bone's canonical name (immune to glTF bone-subset or bone-index ordering differences).
 */
export function rebindSkinnedMeshByBoneName(
  donorMesh: THREE.SkinnedMesh,
  baseScene: THREE.Object3D,
): void {
  const baseBoneByName = new Map<string, THREE.Bone>();
  baseScene.traverse((node) => {
    if (node instanceof THREE.Bone) {
      baseBoneByName.set(node.name, node);
    }
  });

  const remappedBones = donorMesh.skeleton.bones.map(
    (bone) => baseBoneByName.get(bone.name) ?? bone,
  );
  const clonedInverses = donorMesh.skeleton.boneInverses.map((mat) => mat.clone());
  const nextSkeleton = new THREE.Skeleton(remappedBones, clonedInverses);
  donorMesh.bind(nextSkeleton, donorMesh.bindMatrix);
}

const SLOT_NODE_BY_KEY = {
  top: CHARACTER_MESH_SLOTS.TOP,
  bottom: CHARACTER_MESH_SLOTS.BOTTOM,
  shoes: CHARACTER_MESH_SLOTS.SHOES,
  bag: CHARACTER_MESH_SLOTS.BAG,
} as const;

/**
 * Loads and animates a modular rigged glTF/GLB character from content/characters/.
 * Supports switching gender presets (Male / Female), independently swapping modular outfit
 * slots (`TopMesh`, `BottomMesh`, `ShoesMesh`, `BagMesh`) via bone-name skeleton rebinding,
 * and forcing preview clips (e.g. `PoseTest`) in `/lab`.
 */
export class CharacterAvatar {
  readonly group = new THREE.Group();
  private readonly visualRoot = new THREE.Group();
  private mixer: THREE.AnimationMixer | null = null;
  private readonly actions = new Map<string, THREE.AnimationAction>();
  private activeClipName: string | null = null;
  private forcedClipName: string | null = null;
  private fallbackTime = 0;
  private loaded = false;
  private loadout: CharacterLoadout;
  private loadSequence = 0;

  constructor(initial?: CharacterLoadout | CharacterGender | string) {
    this.group.add(this.visualRoot);
    if (typeof initial === "object" && initial !== null) {
      this.loadout = { ...initial };
      void this.applyLoadout(this.loadout);
    } else if (initial === "male" || initial === "female") {
      this.loadout = getDefaultLoadoutForGender(initial);
      void this.applyLoadout(this.loadout);
    } else {
      this.loadout = { ...DEFAULT_CHARACTER_LOADOUTS.male };
      const customUrl = typeof initial === "string" ? initial : undefined;
      void this.applyLoadout(this.loadout, customUrl);
    }
  }

  isLoaded(): boolean {
    return this.loaded;
  }

  getLoadout(): CharacterLoadout {
    return { ...this.loadout };
  }

  /** Forces a specific clip name (e.g. `"PoseTest"` in `/lab`), or `null` for automatic gameplay selection. */
  setForcedClipName(clipName: string | null): void {
    this.forcedClipName = clipName;
    if (clipName && this.actions.has(clipName) && clipName !== this.activeClipName) {
      this.transitionTo(clipName);
    }
  }

  /** Switches to the default design for the selected gender ('male' or 'female'). */
  async setGender(gender: CharacterGender): Promise<void> {
    await this.setLoadout(getDefaultLoadoutForGender(gender));
  }

  /** Updates the character's gender and modular outfit slots (Top, Bottom, Shoes, Bag). */
  async setLoadout(nextLoadout: CharacterLoadout): Promise<void> {
    this.loadout = { ...nextLoadout };
    await this.applyLoadout(this.loadout);
  }

  updateAnimation(speedRatio: number, isRunning: boolean, dt: number): void {
    if (this.mixer) {
      const available = Array.from(this.actions.keys());
      const isForced = Boolean(this.forcedClipName && this.actions.has(this.forcedClipName));
      const clipName = isForced
        ? this.forcedClipName
        : selectAnimationClipName(speedRatio, isRunning, available);
      if (clipName && clipName !== this.activeClipName) {
        this.transitionTo(clipName);
      }

      const playbackRate = computeAnimationTimeScale(this.activeClipName, speedRatio, isForced);
      const activeAction = this.activeClipName ? this.actions.get(this.activeClipName) : null;
      if (activeAction) {
        activeAction.setEffectiveTimeScale(playbackRate);
      }
      this.mixer.update(dt);

      const hasMoveClip = this.actions.has("Walk") || this.actions.has("Run");
      if (!this.forcedClipName && !hasMoveClip && speedRatio > 0.05) {
        this.fallbackTime += dt * (isRunning ? 13 : 9);
        this.visualRoot.position.y =
          Math.abs(Math.sin(this.fallbackTime)) * (isRunning ? 0.06 : 0.03);
      } else {
        this.visualRoot.position.y = THREE.MathUtils.lerp(this.visualRoot.position.y, 0, 0.25);
      }
    }
  }

  private async applyLoadout(loadout: CharacterLoadout, overrideUrl?: string): Promise<void> {
    const seq = ++this.loadSequence;
    try {
      const baseUrl = overrideUrl ?? getCharacterGlbPath(loadout.gender);
      const { scene, animations } = await loadToonGlb(baseUrl);
      if (seq !== this.loadSequence) return;

      await this.configureModularSlots(scene, loadout);
      if (seq !== this.loadSequence) return;

      this.visualRoot.clear();
      this.visualRoot.add(scene);
      this.actions.clear();
      this.activeClipName = null;

      if (animations.length > 0) {
        this.mixer = new THREE.AnimationMixer(scene);
        for (const clip of animations) {
          this.actions.set(clip.name, this.mixer.clipAction(clip));
        }
        const available = Array.from(this.actions.keys());
        const initial =
          this.forcedClipName && this.actions.has(this.forcedClipName)
            ? this.forcedClipName
            : selectAnimationClipName(0, false, available);
        if (initial) {
          const action = this.actions.get(initial);
          action?.reset().play();
          this.activeClipName = initial;
        }
      }
      this.loaded = true;
    } catch (error) {
      console.error("[character-avatar] Failed to load modular character GLB:", error);
    }
  }

  private async configureModularSlots(
    baseScene: THREE.Object3D,
    loadout: CharacterLoadout,
  ): Promise<void> {
    for (const slotKey of OUTFIT_SLOT_KEYS) {
      const nodeName = SLOT_NODE_BY_KEY[slotKey];
      const existingNode = baseScene.getObjectByName(nodeName);
      const option = getOutfitSkinOption(slotKey, loadout[slotKey]);

      if (!option || option.assetPath === null) {
        if (existingNode) existingNode.visible = false;
        continue;
      }

      // Default slot for this gender is already embedded inside the base character GLB
      if (option.sourceGender === loadout.gender) {
        if (existingNode) existingNode.visible = true;
        continue;
      }

      // Otherwise load the standalone modular part GLB from /content/characters/parts/<slot>/<id>.glb
      const partGlb = await loadToonGlb(option.assetPath);
      const donorNode = partGlb.scene.getObjectByName(nodeName);
      if (!donorNode || !existingNode || !existingNode.parent) continue;

      const parent = existingNode.parent;
      parent.remove(existingNode);
      donorNode.parent?.remove(donorNode);
      donorNode.visible = true;

      donorNode.traverse((child) => {
        if (child instanceof THREE.SkinnedMesh) {
          rebindSkinnedMeshByBoneName(child, baseScene);
        }
      });
      parent.add(donorNode);
    }
  }

  private transitionTo(nextClip: string): void {
    const nextAction = this.actions.get(nextClip);
    if (!nextAction) return;

    const prevAction = this.activeClipName ? this.actions.get(this.activeClipName) : null;
    nextAction.reset().setEffectiveWeight(1).play();
    if (prevAction && prevAction !== nextAction) {
      prevAction.crossFadeTo(nextAction, 0.18, true);
    }
    this.activeClipName = nextClip;
  }
}
