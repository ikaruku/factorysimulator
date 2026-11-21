import { Client } from "colyseus.js";
import { GAME_CONFIG, PROTOCOL_VERSION } from "@factory-simulator/shared";
import type { JoinOptions } from "@factory-simulator/shared";

function resolveDefaultServerUrl(): string {
  if (typeof window === "undefined") {
    return `ws://localhost:${GAME_CONFIG.DEFAULT_SERVER_PORT}`;
  }
  if (import.meta.env.DEV) {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}/colyseus`;
  }
  return `ws://${window.location.hostname}:${GAME_CONFIG.DEFAULT_SERVER_PORT}`;
}

const SERVER_URL: string = import.meta.env.VITE_SERVER_URL ?? resolveDefaultServerUrl();

/** Connection check: join the world room, then leave immediately. */
export async function checkServerConnection(): Promise<void> {
  const client = new Client(SERVER_URL);
  const options: JoinOptions = { protocolVersion: PROTOCOL_VERSION };
  const room = await client.joinOrCreate(GAME_CONFIG.WORLD_ROOM_NAME, options);
  await room.leave();
}
