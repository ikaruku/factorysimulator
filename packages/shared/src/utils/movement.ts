import { MOVEMENT_CONFIG } from "../constants/game-config";

/** Camera-relative movement input vector. */
export interface MovementInput {
  /** Strafe axis (-1 left, +1 right). */
  moveX: number;
  /** Forward/backward axis (+1 forward, -1 backward). */
  moveForward: number;
  /** Camera azimuth angle in radians (0 = looking along -Z). */
  cameraYaw: number;
  /** Whether sprint/run is active. */
  run: boolean;
}

/** Planar 2D velocity or position in meters. */
export interface PlanarVector {
  x: number;
  z: number;
}

/** Axis-aligned 2D collider box in the XZ plane. */
export interface ColliderBox {
  minX: number;
  maxX: number;
  minZ: number;
  maxZ: number;
}

/**
 * Computes world-space planar velocity from camera-relative input.
 * Camera yaw = 0 faces -Z; positive yaw rotates counter-clockwise around +Y.
 */
export function computeDesiredVelocity(input: MovementInput): PlanarVector {
  const length = Math.hypot(input.moveX, input.moveForward);
  if (length < 1e-5) {
    return { x: 0, z: 0 };
  }

  const scale = length > 1 ? 1 / length : 1;
  const localRight = input.moveX * scale;
  const localForward = input.moveForward * scale;

  const sinYaw = Math.sin(input.cameraYaw);
  const cosYaw = Math.cos(input.cameraYaw);

  // Forward direction in XZ when yaw rotates around +Y: (-sin(yaw), -cos(yaw)).
  // Right direction in XZ: (cos(yaw), -sin(yaw)).
  const dirX = localRight * cosYaw - localForward * sinYaw;
  const dirZ = -localRight * sinYaw - localForward * cosYaw;

  const speed = input.run ? MOVEMENT_CONFIG.RUN_SPEED_MPS : MOVEMENT_CONFIG.WALK_SPEED_MPS;
  return {
    x: dirX * speed,
    z: dirZ * speed,
  };
}

/** Advances planar position by dt and clamps it inside [-halfBound, halfBound]. */
export function stepPosition(
  position: PlanarVector,
  velocity: PlanarVector,
  dt: number,
  halfBound: number,
): PlanarVector {
  const nextX = clamp(position.x + velocity.x * dt, -halfBound, halfBound);
  const nextZ = clamp(position.z + velocity.z * dt, -halfBound, halfBound);
  return { x: nextX, z: nextZ };
}

/**
 * Resolves circle-vs-AABB collisions so the character slides smoothly
 * along blocks and walls instead of passing through them.
 */
export function resolveCircleBoxCollisions(
  position: PlanarVector,
  radius: number,
  boxes: readonly ColliderBox[],
  halfBound: number,
): PlanarVector {
  let x = position.x;
  let z = position.z;

  for (let pass = 0; pass < 2; pass += 1) {
    for (const box of boxes) {
      const closestX = clamp(x, box.minX, box.maxX);
      const closestZ = clamp(z, box.minZ, box.maxZ);
      const dx = x - closestX;
      const dz = z - closestZ;
      const distSq = dx * dx + dz * dz;

      if (distSq >= radius * radius) continue;

      if (distSq > 1e-8) {
        const dist = Math.sqrt(distSq);
        const overlap = radius - dist;
        x += (dx / dist) * overlap;
        z += (dz / dist) * overlap;
      } else {
        const dMinX = x - box.minX;
        const dMaxX = box.maxX - x;
        const dMinZ = z - box.minZ;
        const dMaxZ = box.maxZ - z;
        const minPen = Math.min(dMinX, dMaxX, dMinZ, dMaxZ);
        if (minPen === dMinX) x = box.minX - radius;
        else if (minPen === dMaxX) x = box.maxX + radius;
        else if (minPen === dMinZ) z = box.minZ - radius;
        else z = box.maxZ + radius;
      }
    }
  }

  return {
    x: clamp(x, -halfBound, halfBound),
    z: clamp(z, -halfBound, halfBound),
  };
}

/** Shortest-arc interpolation between two angles in radians. */
export function lerpAngle(current: number, target: number, alpha: number): number {
  const diff = normalizeAngle(target - current);
  return normalizeAngle(current + diff * clamp(alpha, 0, 1));
}

/** Wraps an angle in radians to [-PI, PI]. */
export function normalizeAngle(angle: number): number {
  let result = (angle + Math.PI) % (Math.PI * 2);
  if (result < 0) result += Math.PI * 2;
  return result - Math.PI;
}

/** Clamps a number between min and max. */
export function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}
