import "./styles/main.css";
import {
  CAMERA_CONFIG,
  MOVEMENT_CONFIG,
  RENDER_CONFIG,
  WORLD_CONFIG,
  computeDesiredVelocity,
  lerpAngle,
  resolveCircleBoxCollisions,
  stepPosition,
} from "@factory-simulator/shared";
import {
  CameraController,
  computeAutoFollowDeltaPitch,
  computeAutoFollowDeltaYaw,
} from "./core/camera-controller";
import { GameLoop } from "./core/game-loop";
import { InputManager, type InputMode } from "./core/input-manager";
import { WorldRenderer } from "./core/renderer";
import { ScreenWakeLock } from "./core/wake-lock";
import { isWebGl2Supported, showGraphicsError } from "./core/webgl-check";
import { CharacterAvatar } from "./entities/character-avatar";
import { startLabPage } from "./lab/lab-page";
import { checkServerConnection } from "./network/connection";
import { FpsCounter } from "./ui/fps-counter";
import { SettingsPanel } from "./ui/settings-panel";
import { setStatus } from "./ui/status";
import { VirtualJoystick } from "./ui/virtual-joystick";
import { OutlineComposer } from "./visuals/outline-composer";
import { createTestWorld } from "./world/test-world";

function updateControlsHint(mode: InputMode, pointerLocked: boolean): void {
  const hint = document.getElementById("controls-hint");
  if (!hint) return;
  if (mode === "touch") {
    hint.textContent = "Left stick move (push edge to run) · Drag screen to look";
    return;
  }
  hint.textContent = pointerLocked
    ? "WASD move · Shift run · Move mouse to look · Esc unlock"
    : "WASD move · Shift run · Drag mouse or [L] camera · F3 FPS";
}

function updateMouseLockButton(mode: InputMode, pointerLocked: boolean): void {
  const button = document.getElementById("mouse-lock-toggle");
  if (!button) return;
  button.classList.toggle("hidden", mode === "touch");
  button.textContent = pointerLocked ? "Mouse Look: ON" : "Mouse Look: OFF";
}

async function checkServerStatus(): Promise<void> {
  setStatus("Server: connecting...");
  try {
    await checkServerConnection();
    setStatus("Server: connected");
  } catch {
    setStatus("Server: offline (local mode)");
  }
}

function startWorldGame(): void {
  if (!isWebGl2Supported()) {
    showGraphicsError(
      "Your browser or device does not support WebGL2, which is required to run Factory Simulator.",
    );
    return;
  }

  const container = document.getElementById("canvas-container");
  if (!container) return;

  const { scene, colliders, sky } = createTestWorld();
  const settingsPanel = new SettingsPanel({
    onOutlinesChange: (enabled) => {
      composer?.setOutlinesEnabled(enabled);
    },
    onCharacterLoadoutChange: (nextLoadout) => {
      void character.setLoadout(nextLoadout);
    },
  });
  const character = new CharacterAvatar(settingsPanel.getCharacterLoadout());
  scene.add(character.group);

  const aspect = (container.clientWidth || window.innerWidth) / Math.max(window.innerHeight, 1);
  const cameraController = new CameraController(aspect);

  let composer: OutlineComposer | null = null;
  const worldRenderer = new WorldRenderer(container, (nextAspect, dims) => {
    cameraController.setAspect(nextAspect);
    composer?.resize(dims.width, dims.height, dims.pixelRatio);
  });

  composer = new OutlineComposer(worldRenderer.renderer, scene, cameraController.camera);
  const initialDims = worldRenderer.getDimensions();
  composer.resize(initialDims.width, initialDims.height, initialDims.pixelRatio);
  composer.setOutlinesEnabled(settingsPanel.isOutlinesEnabled());

  const fpsCounter = new FpsCounter();
  const wakeLock = new ScreenWakeLock();

  let playerX = 0;
  let playerZ = 0;
  let facingYaw = 0;
  let currentSpeedRatio = 0;
  let currentIsRunning = false;
  let manualCameraCooldownSec = 0;
  let returningToDefaultFromMouseLook = false;

  const halfBound =
    WORLD_CONFIG.TEST_FLOOR_SIZE_M / 2 -
    MOVEMENT_CONFIG.CHARACTER_RADIUS_M -
    WORLD_CONFIG.BOUNDARY_MARGIN_M;

  const joystickRef: { instance: VirtualJoystick | null } = { instance: null };
  const inputManager = new InputManager(container, {
    onToggleFps: fpsCounter.toggle,
    onUserInteraction: () => wakeLock.request(),
    onPointerLockChange: (locked) => {
      if (locked) {
        returningToDefaultFromMouseLook = false;
      } else {
        returningToDefaultFromMouseLook = true;
        manualCameraCooldownSec = 0;
      }
      updateMouseLockButton(inputManager.getMode(), locked);
      updateControlsHint(inputManager.getMode(), locked);
    },
    onModeChange: (mode) => {
      joystickRef.instance?.setVisible(mode === "touch");
      const dims = worldRenderer.setTouchMode(mode === "touch");
      composer?.resize(dims.width, dims.height, dims.pixelRatio);
      updateMouseLockButton(mode, inputManager.isPointerLocked());
      updateControlsHint(mode, inputManager.isPointerLocked());
    },
  });

  document.getElementById("mouse-lock-toggle")?.addEventListener("click", () => {
    inputManager.togglePointerLock();
  });

  const joystick = new VirtualJoystick((vec) => {
    inputManager.setJoystickInput(vec.x, vec.forward, vec.run);
    wakeLock.request();
  });
  joystickRef.instance = joystick;

  const initialMode = inputManager.getMode();
  joystick.setVisible(initialMode === "touch");
  updateMouseLockButton(initialMode, false);
  updateControlsHint(initialMode, false);

  const loop = new GameLoop(
    {
      onFixedUpdate: (dt) => {
        const input = inputManager.consumeSnapshot();
        cameraController.rotate(input.cameraDeltaYaw, input.cameraDeltaPitch);

        const velocity = computeDesiredVelocity({
          moveX: input.moveX,
          moveForward: input.moveForward,
          cameraYaw: cameraController.yaw,
          run: input.run,
        });

        const stepped = stepPosition({ x: playerX, z: playerZ }, velocity, dt, halfBound);
        const nextPos = resolveCircleBoxCollisions(
          stepped,
          MOVEMENT_CONFIG.CHARACTER_RADIUS_M,
          colliders,
          halfBound,
        );
        playerX = nextPos.x;
        playerZ = nextPos.z;

        const speed = Math.hypot(velocity.x, velocity.z);
        currentSpeedRatio = speed / MOVEMENT_CONFIG.WALK_SPEED_MPS;
        currentIsRunning = input.run && speed > 0.1;

        if (speed > 0.05) {
          // Character local forward is -Z, so atan2(-vx, -vz) aligns -Z with velocity.
          const targetYaw = Math.atan2(-velocity.x, -velocity.z);
          facingYaw = lerpAngle(facingYaw, targetYaw, MOVEMENT_CONFIG.TURN_SPEED_RAD_PER_SEC * dt);
        }

        const hasManualDelta =
          Math.abs(input.cameraDeltaYaw) > 1e-6 || Math.abs(input.cameraDeltaPitch) > 1e-6;
        if (inputManager.isManualCameraActive() || hasManualDelta) {
          manualCameraCooldownSec = CAMERA_CONFIG.AUTO_FOLLOW_DRAG_COOLDOWN_SEC;
          returningToDefaultFromMouseLook = false;
        } else if (manualCameraCooldownSec > 0) {
          manualCameraCooldownSec = Math.max(0, manualCameraCooldownSec - dt);
        } else {
          const autoYaw = computeAutoFollowDeltaYaw(
            cameraController.yaw,
            facingYaw,
            input.moveForward,
            currentSpeedRatio,
            returningToDefaultFromMouseLook,
            dt,
          );
          const autoPitch =
            returningToDefaultFromMouseLook || currentSpeedRatio >= 0.1
              ? computeAutoFollowDeltaPitch(
                  cameraController.pitch,
                  CAMERA_CONFIG.DEFAULT_PITCH_RAD,
                  dt,
                )
              : 0;
          if (autoYaw !== 0 || autoPitch !== 0) {
            cameraController.rotate(autoYaw, autoPitch);
          } else if (returningToDefaultFromMouseLook && input.moveForward >= -0.25) {
            returningToDefaultFromMouseLook = false;
          }
        }

        character.group.position.set(playerX, 0, playerZ);
        character.group.rotation.y = facingYaw;
      },
      onRender: (dt) => {
        sky.update(dt);
        character.updateAnimation(currentSpeedRatio, currentIsRunning, dt);
        cameraController.update(playerX, 0, playerZ);
        composer?.render();
      },
      onFpsSample: (fps) => {
        fpsCounter.setFps(fps);
      },
    },
    RENDER_CONFIG.TARGET_MAX_FPS,
  );

  loop.start();
  void checkServerStatus();
}

if (window.location.pathname === "/lab") {
  startLabPage();
} else {
  startWorldGame();
}
