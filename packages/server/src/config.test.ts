import { describe, expect, it } from "vitest";
import { GAME_CONFIG } from "@factory-simulator/shared";
import { resolvePort } from "./config";

describe("resolvePort", () => {
  it("uses a valid env value", () => {
    expect(resolvePort("3000")).toBe(3000);
  });

  it("falls back to the default when empty or invalid", () => {
    expect(resolvePort(undefined)).toBe(GAME_CONFIG.DEFAULT_SERVER_PORT);
    expect(resolvePort("abc")).toBe(GAME_CONFIG.DEFAULT_SERVER_PORT);
    expect(resolvePort("99999")).toBe(GAME_CONFIG.DEFAULT_SERVER_PORT);
  });
});
