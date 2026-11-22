import * as THREE from "three";
import { describe, expect, it } from "vitest";
import {
  ASSET_PATHS,
  CHARACTER_MESH_SLOTS,
  DEFAULT_CHARACTER_LOADOUTS,
  VISUAL_CONFIG,
  getDefaultLoadoutForGender,
} from "@factory-simulator/shared";
import {
  computeAnimationTimeScale,
  getCharacterGlbPath,
  selectAnimationClipName,
} from "../entities/character-avatar";
import { convertMaterialToToon } from "./glb-loader";

describe("convertMaterialToToon", () => {
  it("converts a MeshStandardMaterial to MeshToonMaterial preserving color", () => {
    const std = new THREE.MeshStandardMaterial({ color: 0x38acc9 });
    const converted = convertMaterialToToon(std);
    expect(converted).toBeInstanceOf(THREE.MeshToonMaterial);
    expect((converted as THREE.MeshToonMaterial).color.getHex()).toBe(0x38acc9);
  });
});

describe("selectAnimationClipName", () => {
  it("selects Idle, Walk, and Run when all clips exist", () => {
    const clips = ["Idle", "Walk", "Run"];
    expect(selectAnimationClipName(0, false, clips)).toBe("Idle");
    expect(selectAnimationClipName(0.8, false, clips)).toBe("Walk");
    expect(selectAnimationClipName(1.5, true, clips)).toBe("Run");
  });

  it("falls back cleanly to Idle when only Idle exists in early pipeline gates", () => {
    expect(selectAnimationClipName(1.2, true, ["Idle"])).toBe("Idle");
  });

  it("ignores rig verification PoseTest clip during gameplay selection", () => {
    expect(selectAnimationClipName(0, false, ["PoseTest", "Idle"])).toBe("Idle");
    expect(selectAnimationClipName(1.2, true, ["PoseTest", "Idle"])).toBe("Idle");
  });

  it("normalizes playback speed for Walk, Run, Idle, and forced /lab previews", () => {
    expect(computeAnimationTimeScale("Idle", 0, false)).toBe(1);
    expect(computeAnimationTimeScale("Walk", 1.0, false)).toBe(1);
    expect(computeAnimationTimeScale("Run", 1.75, false)).toBe(1);
    expect(computeAnimationTimeScale("Run", 0, true)).toBe(1);
    expect(computeAnimationTimeScale("Walk", 0, true)).toBe(1);
  });
});

describe("modular character gender & slot configuration", () => {
  it("defines distinct default designs for male and female with separated slots", () => {
    const male = getDefaultLoadoutForGender("male");
    const female = getDefaultLoadoutForGender("female");
    expect(male).toEqual(DEFAULT_CHARACTER_LOADOUTS.male);
    expect(female).toEqual(DEFAULT_CHARACTER_LOADOUTS.female);
    expect(male.top).toBe("orange-hoodie");
    expect(male.bag).toBe("red-backpack");
    expect(female.top).toBe("cyan-colorblock-tee");
    expect(female.bottom).toBe("charcoal-shorts");
    expect(female.shoes).toBe("white-strap-sneakers");
    expect(female.bag).toBe("yellow-crossbody");
    expect(getCharacterGlbPath("male")).toBe(ASSET_PATHS.MALE_CHARACTER_GLB);
    expect(getCharacterGlbPath("female")).toBe(ASSET_PATHS.FEMALE_CHARACTER_GLB);
    expect(CHARACTER_MESH_SLOTS.TOP).toBe("TopMesh");
    expect(CHARACTER_MESH_SLOTS.BOTTOM).toBe("BottomMesh");
    expect(CHARACTER_MESH_SLOTS.SHOES).toBe("ShoesMesh");
    expect(CHARACTER_MESH_SLOTS.BAG).toBe("BagMesh");
    expect(VISUAL_CONFIG.OUTLINE_THICKNESS_PX).toBe(1.0);
  });
});
