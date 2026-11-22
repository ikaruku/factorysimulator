/** Centralized game configuration: no magic numbers elsewhere. */
export const GAME_CONFIG = {
  /** Name of the world room in Colyseus. */
  WORLD_ROOM_NAME: "world",
  /** Player capacity per room (assumption, adjustable). */
  MAX_PLAYERS_PER_ROOM: 30,
  /** Default server port. */
  DEFAULT_SERVER_PORT: 2567,
} as const;

/** Movement physics configuration (meters and seconds). */
export const MOVEMENT_CONFIG = {
  /** Walking speed in meters per second. */
  WALK_SPEED_MPS: 4,
  /** Running speed in meters per second. */
  RUN_SPEED_MPS: 7,
  /** Joystick deflection threshold (0..1) that engages running on touch devices. */
  TOUCH_RUN_THRESHOLD: 0.85,
  /** Fixed simulation timestep in seconds (60 Hz). */
  FIXED_TIMESTEP_SEC: 1 / 60,
  /** Maximum frame delta clamped to prevent spiral of death on tab switch. */
  MAX_FRAME_DELTA_SEC: 0.1,
  /** Character collision/boundary radius in meters. */
  CHARACTER_RADIUS_M: 0.45,
  /** Character facing turn rate in radians per second. */
  TURN_SPEED_RAD_PER_SEC: 12,
} as const;

/** Test world geometry configuration. */
export const WORLD_CONFIG = {
  /** Width and depth of the test floor in meters. */
  TEST_FLOOR_SIZE_M: 200,
  /** Grid line divisions across the test floor. */
  GRID_DIVISIONS: 40,
  /** Margin kept inside the floor edge in meters. */
  BOUNDARY_MARGIN_M: 0.5,
} as const;

/** Third-person camera configuration (Abeto-inspired close-medium wide perspective). */
export const CAMERA_CONFIG = {
  /** Wide vertical field of view in degrees. */
  FOV_DEG: 64,
  /** Near clipping plane in meters. */
  NEAR_PLANE_M: 0.1,
  /** Far clipping plane in meters. */
  FAR_PLANE_M: 350,
  /** Orbit distance from the character target in meters. */
  DISTANCE_M: 3.2,
  /** Look target height above the character feet in meters. */
  TARGET_HEIGHT_M: 1.05,
  /** Low default pitch angle in radians above horizontal. */
  DEFAULT_PITCH_RAD: 0.2,
  /** Minimum pitch angle in radians (keeps camera above the floor). */
  MIN_PITCH_RAD: 0.06,
  /** Maximum pitch angle in radians (near top-down limit). */
  MAX_PITCH_RAD: 1.25,
  /** Mouse orbit sensitivity in radians per pixel. */
  MOUSE_SENSITIVITY: 0.005,
  /** Touch orbit sensitivity in radians per pixel. */
  TOUCH_SENSITIVITY: 0.006,
  /** Minimum camera height above the floor in meters. */
  MIN_CAMERA_HEIGHT_M: 0.4,
  /** Exponential damping rate for gentle auto-follow behind the character. */
  AUTO_FOLLOW_RATE: 0.8,
  /** Maximum auto-follow rotation speed in radians per second (~57 deg/s). */
  AUTO_FOLLOW_MAX_SPEED_RAD: 1.0,
  /** Angle threshold beyond which auto-follow avoids whipping 180 degrees around. */
  AUTO_FOLLOW_MAX_ANGLE_RAD: 2.15,
  /** Cooldown in seconds before auto-follow resumes after manual camera drag. */
  AUTO_FOLLOW_DRAG_COOLDOWN_SEC: 0.8,
  /** Exponential damping rate for returning camera pitch to default. */
  PITCH_RESET_RATE: 1.5,
  /** Maximum pitch return speed in radians per second. */
  PITCH_RESET_MAX_SPEED_RAD: 0.7,
} as const;

/** Renderer and frame-rate configuration. */
export const RENDER_CONFIG = {
  /** Maximum device pixel ratio on desktop. */
  MAX_PIXEL_RATIO: 2,
  /** Maximum device pixel ratio on touch/mobile devices. */
  MOBILE_PIXEL_RATIO: 1.5,
  /** Power-saving frame rate cap in frames per second. */
  TARGET_MAX_FPS: 60,
} as const;

/** Standardized runtime paths for data-driven assets served from content/. */
export const ASSET_PATHS = {
  /** Default player character glTF binary asset (points to male default skin, zero duplicate file). */
  DEFAULT_CHARACTER_GLB: "/content/characters/male/character.glb",
  /** Male default character glTF binary asset. */
  MALE_CHARACTER_GLB: "/content/characters/male/character.glb",
  /** Female default character glTF binary asset. */
  FEMALE_CHARACTER_GLB: "/content/characters/female/character.glb",
  /** Root directory for standalone modular outfit part GLBs (`top`, `bottom`, `shoes`, `bag`). */
  CHARACTER_PARTS_DIR: "/content/characters/parts",
} as const;

/** Stage 1B toon shader, outline pass, and procedural sky configuration. */
export const VISUAL_CONFIG = {
  /** Discrete shading bands in the toon gradient map (2 for authentic 2-tone Abeto cel shading). */
  TOON_LEVELS: 2,
  /** Default screen-space outline thickness in logical pixels. */
  OUTLINE_THICKNESS_PX: 1.0,
  /** Depth edge sensitivity for exterior silhouette outline detection. */
  OUTLINE_DEPTH_THRESHOLD: 0.07,
  /** Angular normal crease threshold (1 - dot(nA, nB); 0.36 ~= 50 deg sculpted cloth crease). */
  OUTLINE_NORMAL_THRESHOLD: 0.36,
  /** Slow drift speed for procedural sky cloud strokes. */
  SKY_CLOUD_SPEED: 0.015,
} as const;
