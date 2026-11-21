import { Client, Room } from "@colyseus/core";
import { GAME_CONFIG, checkProtocolVersion } from "@factory-simulator/shared";
import type { JoinOptions } from "@factory-simulator/shared";

/** Main world room. Stage 0: only accepts connections and checks the protocol version. */
export class WorldRoom extends Room {
  override maxClients = GAME_CONFIG.MAX_PLAYERS_PER_ROOM;

  override onJoin(client: Client, options: Partial<JoinOptions>): void {
    const error = checkProtocolVersion(options.protocolVersion);
    if (error) {
      client.leave(4000, error);
      return;
    }
    console.log(`[world] ${client.sessionId} joined`);
  }

  override onLeave(client: Client): void {
    console.log(`[world] ${client.sessionId} left`);
  }
}
