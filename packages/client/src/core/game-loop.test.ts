import { describe, expect, it } from "vitest";
import { FixedTimestepAccumulator } from "./game-loop";

describe("FixedTimestepAccumulator", () => {
  it("runs the exact number of fixed steps regardless of frame rate", () => {
    const acc = new FixedTimestepAccumulator(1 / 60, 0.1);
    let stepsAt120Hz = 0;
    for (let i = 0; i < 120; i += 1) {
      stepsAt120Hz += acc.advance(1 / 120, () => {});
    }

    const acc30 = new FixedTimestepAccumulator(1 / 60, 0.1);
    let stepsAt30Hz = 0;
    for (let i = 0; i < 30; i += 1) {
      stepsAt30Hz += acc30.advance(1 / 30, () => {});
    }

    expect(stepsAt120Hz).toBe(60);
    expect(stepsAt30Hz).toBe(60);
  });

  it("clamps large frame deltas to avoid spiral of death", () => {
    const acc = new FixedTimestepAccumulator(1 / 60, 0.1);
    const steps = acc.advance(5, () => {});
    expect(steps).toBe(6);
  });
});
