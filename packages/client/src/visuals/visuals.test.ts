import { describe, expect, it } from "vitest";
import { ABETO_PALETTE, ABETO_SWATCHES } from "../theme/abeto-theme";
import { buildToonGradientBytes } from "./toon-material";

describe("buildToonGradientBytes", () => {
  it("produces discrete ascending steps matching the requested band count", () => {
    const bytes = buildToonGradientBytes(4);
    expect(bytes.length).toBe(4);
    expect(bytes[0]).toBeLessThan(bytes[1]!);
    expect(bytes[1]).toBeLessThan(bytes[2]!);
    expect(bytes[2]).toBeLessThan(bytes[3]!);
    expect(bytes[3]).toBe(255);
  });
});

describe("ABETO_PALETTE", () => {
  it("exposes swatches and key character colors", () => {
    expect(ABETO_SWATCHES.length).toBeGreaterThanOrEqual(6);
    expect(ABETO_PALETTE.CHAR_BAG).toBe(0xe6a832);
    expect(ABETO_PALETTE.CHAR_SHIRT_CYAN).toBe(0x38acc9);
  });
});
