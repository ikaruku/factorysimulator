import { GAME_CONFIG } from "@factory-simulator/shared";

/** Reads the port from env; falls back to the default when empty or invalid. */
export function resolvePort(value: string | undefined): number {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 && parsed < 65536
    ? parsed
    : GAME_CONFIG.DEFAULT_SERVER_PORT;
}
