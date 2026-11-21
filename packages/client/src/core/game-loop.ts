import { MOVEMENT_CONFIG } from "@factory-simulator/shared";

/**
 * Pure fixed-timestep accumulator so simulation speed stays identical
 * across 30 Hz, 60 Hz, 120 Hz and 144 Hz displays.
 */
export class FixedTimestepAccumulator {
  private accumulatorSec = 0;

  constructor(
    private readonly stepSec: number = MOVEMENT_CONFIG.FIXED_TIMESTEP_SEC,
    private readonly maxDeltaSec: number = MOVEMENT_CONFIG.MAX_FRAME_DELTA_SEC,
  ) {}

  /** Feeds frame delta and invokes onStep for each fixed tick. */
  advance(rawDeltaSec: number, onStep: (dt: number) => void): number {
    const clampedDelta = Math.min(Math.max(rawDeltaSec, 0), this.maxDeltaSec);
    this.accumulatorSec += clampedDelta;

    let steps = 0;
    while (this.accumulatorSec >= this.stepSec) {
      onStep(this.stepSec);
      this.accumulatorSec -= this.stepSec;
      steps += 1;
    }
    return steps;
  }

  /** Resets accumulated time (used after tab pause). */
  reset(): void {
    this.accumulatorSec = 0;
  }
}

export interface GameLoopCallbacks {
  onFixedUpdate: (dt: number) => void;
  onRender: (dt: number) => void;
  onFpsSample?: (fps: number) => void;
}

/**
 * Main client loop with fixed simulation steps, 60 FPS cap,
 * and automatic pause when the browser tab is hidden.
 */
export class GameLoop {
  private readonly accumulator = new FixedTimestepAccumulator();
  private rafId: number | null = null;
  private lastTimestampMs = 0;
  private fpsFrames = 0;
  private fpsWindowMs = 0;

  constructor(
    private readonly callbacks: GameLoopCallbacks,
    private readonly maxFps: number,
  ) {}

  start(): void {
    if (this.rafId !== null) return;
    document.addEventListener("visibilitychange", this.handleVisibilityChange);
    this.lastTimestampMs = performance.now();
    this.rafId = requestAnimationFrame(this.tick);
  }

  stop(): void {
    if (this.rafId !== null) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
    document.removeEventListener("visibilitychange", this.handleVisibilityChange);
  }

  private readonly handleVisibilityChange = (): void => {
    if (!document.hidden) {
      this.lastTimestampMs = performance.now();
      this.accumulator.reset();
    }
  };

  private readonly tick = (nowMs: number): void => {
    this.rafId = requestAnimationFrame(this.tick);
    if (document.hidden) return;

    const minFrameMs = 1000 / this.maxFps;
    const elapsedMs = nowMs - this.lastTimestampMs;
    if (elapsedMs < minFrameMs * 0.92) return;

    this.lastTimestampMs = nowMs;
    const dt = elapsedMs / 1000;

    this.accumulator.advance(dt, this.callbacks.onFixedUpdate);
    this.callbacks.onRender(dt);

    this.fpsFrames += 1;
    this.fpsWindowMs += elapsedMs;
    if (this.fpsWindowMs >= 500) {
      const fps = Math.round((this.fpsFrames * 1000) / this.fpsWindowMs);
      this.callbacks.onFpsSample?.(fps);
      this.fpsFrames = 0;
      this.fpsWindowMs = 0;
    }
  };
}
