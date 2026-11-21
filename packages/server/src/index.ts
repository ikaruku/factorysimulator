import { Server } from "@colyseus/core";
import { WebSocketTransport } from "@colyseus/ws-transport";
import { GAME_CONFIG } from "@factory-simulator/shared";
import { WorldRoom } from "./rooms/world-room";
import { resolvePort } from "./config";

const port = resolvePort(process.env.PORT);

const gameServer = new Server({ transport: new WebSocketTransport() });
gameServer.define(GAME_CONFIG.WORLD_ROOM_NAME, WorldRoom);

await gameServer.listen(port);
console.log(`[server] Colyseus running at ws://localhost:${port}`);
