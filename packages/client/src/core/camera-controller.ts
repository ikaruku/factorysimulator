import * as THREE from "three";
import { CAMERA_CONFIG, clamp, normalizeAngle } from "@factory-simulator/shared";

export interface CameraPosition {
  x: number;
  y: number;
  z: number;
}

/**
 * Computes a gentle, rate-limited yaw delta so the camera slowly drifts
 * behind the moving character (or returns to default after Mouse Look turns off).
 */
export function computeAutoFollowDeltaYaw(
  cameraYaw: number,
  facingYaw: number,
  moveForward: number,
  speedRatio: number,
  forceReturnToDefault: boolean,
  dt: number,
): number {
  if (moveForward < -0.25) {
    return 0;
  }
  if (!forceReturnToDefault && speedRatio < 0.1) {
    return 0;
  }

  const diff = normalizeAngle(facingYaw - cameraYaw);
  if (Math.abs(diff) < 0.002) {
    return 0;
  }
  if (!forceReturnToDefault && Math.abs(diff) > CAMERA_CONFIG.AUTO_FOLLOW_MAX_ANGLE_RAD) {
    return 0;
  }

  const eased = diff * (1 - Math.exp(-CAMERA_CONFIG.AUTO_FOLLOW_RATE * dt));
  const maxStep = CAMERA_CONFIG.AUTO_FOLLOW_MAX_SPEED_RAD * dt;
  return clamp(eased, -maxStep, maxStep);
}

/**
 * Computes a gentle, rate-limited pitch delta so camera pitch smoothly
 * returns toward the default angle when Mouse Look is off.
 */
export function computeAutoFollowDeltaPitch(
  cameraPitch: number,
  targetPitch: number = CAMERA_CONFIG.DEFAULT_PITCH_RAD,
  dt: number = 1 / 60,
): number {
  const diff = targetPitch - cameraPitch;
  if (Math.abs(diff) < 0.002) {
    return 0;
  }
  const eased = diff * (1 - Math.exp(-CAMERA_CONFIG.PITCH_RESET_RATE * dt));
  const maxStep = CAMERA_CONFIG.PITCH_RESET_MAX_SPEED_RAD * dt;
  return clamp(eased, -maxStep, maxStep);
}

/**
 * Pure orbit position helper: computes camera coordinates behind the target
 * and guarantees the camera never drops below MIN_CAMERA_HEIGHT_M.
 */
export function computeCameraPosition(
  targetX: number,
  targetY: number,
  targetZ: number,
  yaw: number,
  pitch: number,
  distance: number = CAMERA_CONFIG.DISTANCE_M,
): CameraPosition {
  const safePitch = clamp(pitch, CAMERA_CONFIG.MIN_PITCH_RAD, CAMERA_CONFIG.MAX_PITCH_RAD);
  const horizontal = distance * Math.cos(safePitch);
  const vertical = distance * Math.sin(safePitch);

  return {
    x: targetX + horizontal * Math.sin(yaw),
    y: Math.max(CAMERA_CONFIG.MIN_CAMERA_HEIGHT_M, targetY + vertical),
    z: targetZ + horizontal * Math.cos(yaw),
  };
}

/** Third-person orbit camera that smoothly tracks the player. */
export class CameraController {
  readonly camera: THREE.PerspectiveCamera;
  yaw = 0;
  pitch: number = CAMERA_CONFIG.DEFAULT_PITCH_RAD;

  constructor(aspect: number) {
    this.camera = new THREE.PerspectiveCamera(
      CAMERA_CONFIG.FOV_DEG,
      aspect,
      CAMERA_CONFIG.NEAR_PLANE_M,
      CAMERA_CONFIG.FAR_PLANE_M,
    );
  }

  rotate(deltaYaw: number, deltaPitch: number): void {
    this.yaw = normalizeAngle(this.yaw + deltaYaw);
    this.pitch = clamp(
      this.pitch + deltaPitch,
      CAMERA_CONFIG.MIN_PITCH_RAD,
      CAMERA_CONFIG.MAX_PITCH_RAD,
    );
  }

  update(playerX: number, playerY: number, playerZ: number): void {
    const targetY = playerY + CAMERA_CONFIG.TARGET_HEIGHT_M;
    const pos = computeCameraPosition(playerX, targetY, playerZ, this.yaw, this.pitch);
    this.camera.position.set(pos.x, pos.y, pos.z);
    this.camera.lookAt(playerX, targetY, playerZ);
  }

  setAspect(aspect: number): void {
    this.camera.aspect = aspect;
    this.camera.updateProjectionMatrix();
  }
}
