import { describe, expect, it } from "vitest";
import { PROTOCOL_VERSION } from "../protocol/version";
import { checkProtocolVersion } from "./protocol-check";

describe("checkProtocolVersion", () => {
  it("accepts a matching version", () => {
    expect(checkProtocolVersion(PROTOCOL_VERSION)).toBeNull();
  });

  it("rejects a different version with a clear message", () => {
    expect(checkProtocolVersion(PROTOCOL_VERSION + 1)).toContain("mismatch");
  });

  it("rejects a non-numeric value", () => {
    expect(checkProtocolVersion(undefined)).not.toBeNull();
  });
});
