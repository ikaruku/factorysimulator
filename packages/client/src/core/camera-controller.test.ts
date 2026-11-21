import { describe, expect, it } from "vitest";
import { CAMERA_CONFIG } from "@factory-simulator/shared";
import {
  computeAutoFollowDeltaPitch,
  computeAutoFollowDeltaYaw,
  computeCameraPosition,
} from "./camera-controller";

describe("computeCameraPosition", () => {
  it("never places the camera below minimum height above the floor", () => {
    const lowPitch = computeCameraPosition(0, CAMERA_CONFIG.TARGET_HEIGHT_M, 0, 0, -2);
    expect(lowPitch.y).toBeGreaterThanOrEqual(CAMERA_CONFIG.MIN_CAMERA_HEIGHT_M);
  });

  it("places camera along +Z when yaw is 0", () => {
    const pos = computeCameraPosition(0, 1.35, 0, 0, CAMERA_CONFIG.DEFAULT_PITCH_RAD);
    expect(pos.x).toBeCloseTo(0, 5);
    expect(pos.z).toBeGreaterThan(0);
  });
});

describe("computeAutoFollowDeltaYaw", () => {
  it("gently rotates camera toward character facing when strafing left or right", () => {
    const dt = 1 / 60;
    const delta = computeAutoFollowDeltaYaw(0, -Math.PI / 2, 0, 1, false, dt);
    expect(delta).toBeLessThan(0);
    expect(Math.abs(delta)).toBeLessThanOrEqual(
      CAMERA_CONFIG.AUTO_FOLLOW_MAX_SPEED_RAD * dt + 1e-9,
    );
  });

  it("does not rotate when idle without return-to-default or when pressing S", () => {
    expect(computeAutoFollowDeltaYaw(0, -Math.PI / 2, 0, 0, false, 1 / 60)).toBe(0);
    expect(computeAutoFollowDeltaYaw(0, Math.PI, -1, 1, false, 1 / 60)).toBe(0);
    expect(computeAutoFollowDeltaYaw(0, Math.PI, -1, 1, true, 1 / 60)).toBe(0);
  });

  it("smoothly returns camera behind character when Mouse Look turns off even while idle", () => {
    const dt = 1 / 60;
    const delta = computeAutoFollowDeltaYaw(Math.PI * 0.75, 0, 0, 0, true, dt);
    expect(delta).not.toBe(0);
    expect(Math.abs(delta)).toBeLessThanOrEqual(
      CAMERA_CONFIG.AUTO_FOLLOW_MAX_SPEED_RAD * dt + 1e-9,
    );
  });
});

describe("computeAutoFollowDeltaPitch", () => {
  it("gently eases pitch back toward the default angle", () => {
    const dt = 1 / 60;
    const delta = computeAutoFollowDeltaPitch(1.0, CAMERA_CONFIG.DEFAULT_PITCH_RAD, dt);
    expect(delta).toBeLessThan(0);
    expect(Math.abs(delta)).toBeLessThanOrEqual(
      CAMERA_CONFIG.PITCH_RESET_MAX_SPEED_RAD * dt + 1e-9,
    );
  });
});
