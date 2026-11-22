import * as THREE from "three";
import {
  ASSET_PATHS,
  BAG_SKIN_OPTIONS,
  BOTTOM_SKIN_OPTIONS,
  CHARACTER_MESH_SLOTS,
  DEFAULT_CHARACTER_LOADOUTS,
  SHOES_SKIN_OPTIONS,
  TOP_SKIN_OPTIONS,
  getDefaultLoadoutForGender,
  type CharacterGender,
  type CharacterLoadout,
} from "@factory-simulator/shared";
import { loadToonGlb } from "../assets/glb-loader";

export type CharacterAnimState = "Idle" | "Walk" | "Run";

/** Selects the best available skeletal clip name for the current movement state. */
export function selectAnimationClipName(
  speedRatio: number,
  isRunning: boolean,
  availableNames: readonly string[],
): string | null {
  const desired: CharacterAnimState = speedRatio <= 0.05 ? "Idle" : isRunning ? "Run" : "Walk";

  if (availableNames.includes(desired)) return desired;
  if (desired === "Run" && availableNames.includes("Walk")) return "Walk";
  if (availableNames.includes("Idle")) return "Idle";
  return availableNames[0] ?? null;
}

/** Resolves the GLB asset path for a given character gender preset. */
export function getCharacterGlbPath(gender: CharacterGender): string {
  return gender === "female" ? ASSET_PATHS.FEMALE_CHARACTER_GLB : ASSET_PATHS.MALE_CHARACTER_GLB;
}

const SLOT_NODE_BY_KEY = {
  top: CHARACTER_MESH_SLOTS.TOP,
  bottom: CHARACTER_MESH_SLOTS.BOTTOM,
  shoes: CHARACTER_MESH_SLOTS.SHOES,
  bag: CHARACTER_MESH_SLOTS.BAG,
} as const;

/**
 * Loads and animates a modular rigged glTF/GLB character from content/characters/.
 * Supports switching gender presets (Male / Female) and independently swapping
 * modular outfit slots (`TopMesh`, `BottomMesh`, `ShoesMesh`, `BagMesh`).
 */
export class CharacterAvatar {
  readonly group = new THREE.Group();
  private readonly visualRoot = new THREE.Group();
  private mixer: THREE.AnimationMixer | null = null;
  private readonly actions = new Map<string, THREE.AnimationAction>();
  private activeClipName: string | null = null;
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
      const clipName = selectAnimationClipName(
        speedRatio,
        isRunning,
        Array.from(this.actions.keys()),
      );
      if (clipName && clipName !== this.activeClipName) {
        this.transitionTo(clipName);
      }

      const playbackRate =
        clipName === "Walk" || clipName === "Run" ? THREE.MathUtils.clamp(speedRatio, 0.6, 1.5) : 1;
      const activeAction = this.activeClipName ? this.actions.get(this.activeClipName) : null;
      if (activeAction) {
        activeAction.setEffectiveTimeScale(playbackRate);
      }
      this.mixer.update(dt);

      const hasMoveClip = this.actions.has("Walk") || this.actions.has("Run");
      if (!hasMoveClip && speedRatio > 0.05) {
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
        const initial = selectAnimationClipName(0, false, Array.from(this.actions.keys()));
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
    const slotSources: Record<"top" | "bottom" | "shoes" | "bag", CharacterGender | null> = {
      top: TOP_SKIN_OPTIONS.find((o) => o.id === loadout.top)?.sourceGender ?? loadout.gender,
      bottom:
        BOTTOM_SKIN_OPTIONS.find((o) => o.id === loadout.bottom)?.sourceGender ?? loadout.gender,
      shoes: SHOES_SKIN_OPTIONS.find((o) => o.id === loadout.shoes)?.sourceGender ?? loadout.gender,
      bag: BAG_SKIN_OPTIONS.find((o) => o.id === loadout.bag)?.sourceGender ?? null,
    };

    const needsOppositeGender = Object.values(slotSources).some(
      (src) => src !== null && src !== loadout.gender,
    );
    const oppositeGender: CharacterGender = loadout.gender === "male" ? "female" : "male";
    const donorScene = needsOppositeGender
      ? (await loadToonGlb(getCharacterGlbPath(oppositeGender))).scene
      : null;

    const baseSkinned = this.findFirstSkinnedMesh(baseScene);

    for (const slotKey of ["top", "bottom", "shoes", "bag"] as const) {
      const nodeName = SLOT_NODE_BY_KEY[slotKey];
      const existingNode = baseScene.getObjectByName(nodeName);
      const sourceGender = slotSources[slotKey];

      if (sourceGender === null) {
        if (existingNode) existingNode.visible = false;
        continue;
      }

      if (sourceGender === loadout.gender || !donorScene) {
        if (existingNode) existingNode.visible = true;
        continue;
      }

      const donorNode = donorScene.getObjectByName(nodeName);
      if (!donorNode || !existingNode || !existingNode.parent) continue;

      const parent = existingNode.parent;
      parent.remove(existingNode);
      donorNode.parent?.remove(donorNode);
      donorNode.visible = true;

      if (baseSkinned) {
        donorNode.traverse((child) => {
          if (child instanceof THREE.SkinnedMesh) {
            child.bind(baseSkinned.skeleton, baseSkinned.bindMatrix);
          }
        });
      }
      parent.add(donorNode);
    }
  }

  private findFirstSkinnedMesh(root: THREE.Object3D): THREE.SkinnedMesh | null {
    let found: THREE.SkinnedMesh | null = null;
    root.traverse((node) => {
      if (!found && node instanceof THREE.SkinnedMesh) {
        found = node;
      }
    });
    return found;
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
