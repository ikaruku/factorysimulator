import { describe, expect, it } from "vitest";
import { MOVEMENT_CONFIG } from "../constants/game-config";
import {
  computeDesiredVelocity,
  lerpAngle,
  resolveCircleBoxCollisions,
  stepPosition,
} from "./movement";

describe("computeDesiredVelocity", () => {
  it("returns zero velocity when input is idle", () => {
    expect(computeDesiredVelocity({ moveX: 0, moveForward: 0, cameraYaw: 0, run: false })).toEqual({
      x: 0,
      z: 0,
    });
  });

  it("moves forward along -Z at walk speed when yaw is 0", () => {
    const vel = computeDesiredVelocity({ moveX: 0, moveForward: 1, cameraYaw: 0, run: false });
    expect(vel.x).toBeCloseTo(0, 5);
    expect(vel.z).toBeCloseTo(-MOVEMENT_CONFIG.WALK_SPEED_MPS, 5);
  });

  it("moves at run speed when run is true", () => {
    const vel = computeDesiredVelocity({ moveX: 1, moveForward: 0, cameraYaw: 0, run: true });
    expect(vel.x).toBeCloseTo(MOVEMENT_CONFIG.RUN_SPEED_MPS, 5);
    expect(vel.z).toBeCloseTo(0, 5);
  });

  it("normalizes diagonal input so speed does not exceed walk speed", () => {
    const vel = computeDesiredVelocity({ moveX: 1, moveForward: 1, cameraYaw: 0, run: false });
    expect(Math.hypot(vel.x, vel.z)).toBeCloseTo(MOVEMENT_CONFIG.WALK_SPEED_MPS, 5);
  });

  it("rotates movement direction by cameraYaw", () => {
    const vel = computeDesiredVelocity({
      moveX: 0,
      moveForward: 1,
      cameraYaw: Math.PI / 2,
      run: false,
    });
    expect(vel.x).toBeCloseTo(-MOVEMENT_CONFIG.WALK_SPEED_MPS, 5);
    expect(vel.z).toBeCloseTo(0, 5);
  });
});

describe("stepPosition", () => {
  it("advances position and clamps to world bounds", () => {
    const next = stepPosition({ x: 98, z: -98 }, { x: 4, z: -4 }, 1, 99.5);
    expect(next.x).toBe(99.5);
    expect(next.z).toBe(-99.5);
  });
});

describe("resolveCircleBoxCollisions", () => {
  const box = { minX: 5.5, maxX: 6.5, minZ: -6.5, maxZ: -5.5 };

  it("pushes character out of a solid block without clipping", () => {
    const resolved = resolveCircleBoxCollisions({ x: 6, z: -5.3 }, 0.45, [box], 99);
    expect(resolved.x).toBeCloseTo(6, 5);
    expect(resolved.z).toBeCloseTo(-5.5 + 0.45, 5);
  });

  it("allows sliding along the side of a block", () => {
    const resolved = resolveCircleBoxCollisions({ x: 6.3, z: -5.2 }, 0.45, [box], 99);
    expect(resolved.x).toBeCloseTo(6.3, 5);
    expect(resolved.z).toBeCloseTo(-5.5 + 0.45, 5);
  });

  it("pushes out even when the center starts deep inside a block", () => {
    const resolved = resolveCircleBoxCollisions({ x: 6, z: -6 }, 0.45, [box], 99);
    const outsideX = resolved.x <= box.minX - 0.45 || resolved.x >= box.maxX + 0.45;
    const outsideZ = resolved.z <= box.minZ - 0.45 || resolved.z >= box.maxZ + 0.45;
    expect(outsideX || outsideZ).toBe(true);
  });
});

describe("lerpAngle", () => {
  it("takes the shortest path across the -PI / +PI wrap", () => {
    const result = lerpAngle(Math.PI - 0.1, -Math.PI + 0.1, 0.5);
    expect(Math.abs(Math.abs(result) - Math.PI)).toBeLessThan(0.01);
  });
});
