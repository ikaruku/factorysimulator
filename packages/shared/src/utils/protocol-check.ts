import { PROTOCOL_VERSION } from "../protocol/version";

/** Returns an error message when the version does not match, or null when it does. */
export function checkProtocolVersion(clientVersion: unknown): string | null {
  if (clientVersion === PROTOCOL_VERSION) return null;
  return `Protocol version mismatch: client ${String(clientVersion)}, server ${PROTOCOL_VERSION}. Please reload the page.`;
}
