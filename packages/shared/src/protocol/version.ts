/** Network protocol version. Bump it whenever the message format changes. */
export const PROTOCOL_VERSION = 1;

/** Network message names (single source of truth). */
export const MESSAGE_TYPES = {
  PING: "ping",
  PONG: "pong",
} as const;

export type MessageType = (typeof MESSAGE_TYPES)[keyof typeof MESSAGE_TYPES];

/** Options sent by the client when joining a room. */
export interface JoinOptions {
  protocolVersion: number;
}
