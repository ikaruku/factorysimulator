import { CAMERA_CONFIG } from "@factory-simulator/shared";

export type InputMode = "desktop" | "touch";

export interface InputSnapshot {
  moveX: number;
  moveForward: number;
  run: boolean;
  cameraDeltaYaw: number;
  cameraDeltaPitch: number;
  mode: InputMode;
}

export interface InputManagerCallbacks {
  onModeChange?: (mode: InputMode) => void;
  onToggleFps?: () => void;
  onPointerLockChange?: (locked: boolean) => void;
  onUserInteraction?: () => void;
}

/**
 * Unifies keyboard, mouse camera orbit (left/right drag or optional pointer-lock free look),
 * touch camera drag, and virtual joystick while switching desktop/touch modes automatically.
 */
export class InputManager {
  private readonly pressedKeys = new Set<string>();
  private dragMouseDown = false;
  private lastMouseX = 0;
  private lastMouseY = 0;
  private cameraTouchId: number | null = null;
  private lastTouchX = 0;
  private lastTouchY = 0;
  private pendingYaw = 0;
  private pendingPitch = 0;
  private joystickX = 0;
  private joystickForward = 0;
  private joystickRun = false;
  private mode: InputMode;

  constructor(
    private readonly targetElement: HTMLElement,
    private readonly callbacks: InputManagerCallbacks = {},
  ) {
    this.mode = window.matchMedia("(pointer: coarse)").matches ? "touch" : "desktop";
    window.addEventListener("keydown", this.handleKeyDown);
    window.addEventListener("keyup", this.handleKeyUp);
    window.addEventListener("blur", this.handleBlur);
    document.addEventListener("pointerlockchange", this.handlePointerLockChange);
    this.targetElement.addEventListener("mousedown", this.handleMouseDown);
    window.addEventListener("mousemove", this.handleMouseMove);
    window.addEventListener("mouseup", this.handleMouseUp);
    this.targetElement.addEventListener("contextmenu", this.handleContextMenu);
    this.targetElement.addEventListener("touchstart", this.handleTouchStart, { passive: false });
    this.targetElement.addEventListener("touchmove", this.handleTouchMove, { passive: false });
    this.targetElement.addEventListener("touchend", this.handleTouchEnd);
    this.targetElement.addEventListener("touchcancel", this.handleTouchEnd);
  }

  getMode(): InputMode {
    return this.mode;
  }

  isPointerLocked(): boolean {
    return document.pointerLockElement === this.targetElement;
  }

  isManualCameraActive(): boolean {
    return this.isPointerLocked() || this.dragMouseDown || this.cameraTouchId !== null;
  }

  togglePointerLock(): void {
    if (this.isPointerLocked()) {
      document.exitPointerLock?.();
      return;
    }
    this.targetElement.requestPointerLock?.();
  }

  setJoystickInput(x: number, forward: number, run: boolean): void {
    this.joystickX = x;
    this.joystickForward = forward;
    this.joystickRun = run;
    if (Math.hypot(x, forward) > 0) {
      this.setMode("touch");
    }
  }

  consumeSnapshot(): InputSnapshot {
    let keyX = 0;
    let keyForward = 0;
    if (this.hasKey("KeyA", "ArrowLeft")) keyX -= 1;
    if (this.hasKey("KeyD", "ArrowRight")) keyX += 1;
    if (this.hasKey("KeyW", "ArrowUp")) keyForward += 1;
    if (this.hasKey("KeyS", "ArrowDown")) keyForward -= 1;

    const hasKeyboardMove = keyX !== 0 || keyForward !== 0;
    const moveX = hasKeyboardMove ? keyX : this.joystickX;
    const moveForward = hasKeyboardMove ? keyForward : this.joystickForward;
    const run = hasKeyboardMove
      ? this.hasKey("ShiftLeft", "ShiftRight")
      : this.joystickRun || this.hasKey("ShiftLeft", "ShiftRight");

    const snapshot: InputSnapshot = {
      moveX,
      moveForward,
      run,
      cameraDeltaYaw: this.pendingYaw,
      cameraDeltaPitch: this.pendingPitch,
      mode: this.mode,
    };

    this.pendingYaw = 0;
    this.pendingPitch = 0;
    return snapshot;
  }

  dispose(): void {
    window.removeEventListener("keydown", this.handleKeyDown);
    window.removeEventListener("keyup", this.handleKeyUp);
    window.removeEventListener("blur", this.handleBlur);
    document.removeEventListener("pointerlockchange", this.handlePointerLockChange);
    this.targetElement.removeEventListener("mousedown", this.handleMouseDown);
    window.removeEventListener("mousemove", this.handleMouseMove);
    window.removeEventListener("mouseup", this.handleMouseUp);
    this.targetElement.removeEventListener("contextmenu", this.handleContextMenu);
    this.targetElement.removeEventListener("touchstart", this.handleTouchStart);
    this.targetElement.removeEventListener("touchmove", this.handleTouchMove);
    this.targetElement.removeEventListener("touchend", this.handleTouchEnd);
    this.targetElement.removeEventListener("touchcancel", this.handleTouchEnd);
  }

  private hasKey(...codes: string[]): boolean {
    return codes.some((code) => this.pressedKeys.has(code));
  }

  private setMode(nextMode: InputMode): void {
    if (this.mode === nextMode) return;
    this.mode = nextMode;
    this.callbacks.onModeChange?.(nextMode);
  }

  private readonly handlePointerLockChange = (): void => {
    this.callbacks.onPointerLockChange?.(this.isPointerLocked());
  };

  private readonly handleKeyDown = (event: KeyboardEvent): void => {
    if (event.code === "F3") {
      event.preventDefault();
      this.callbacks.onToggleFps?.();
      return;
    }
    if (event.code === "KeyL" && !event.repeat) {
      event.preventDefault();
      this.togglePointerLock();
      return;
    }
    this.pressedKeys.add(event.code);
    this.setMode("desktop");
    this.callbacks.onUserInteraction?.();
  };

  private readonly handleKeyUp = (event: KeyboardEvent): void => {
    this.pressedKeys.delete(event.code);
  };

  private readonly handleBlur = (): void => {
    this.pressedKeys.clear();
    this.dragMouseDown = false;
  };

  private readonly handleContextMenu = (event: MouseEvent): void => {
    event.preventDefault();
  };

  private readonly handleMouseDown = (event: MouseEvent): void => {
    this.setMode("desktop");
    this.callbacks.onUserInteraction?.();
    if (event.button === 0 || event.button === 1 || event.button === 2) {
      this.dragMouseDown = true;
      this.lastMouseX = event.clientX;
      this.lastMouseY = event.clientY;
    }
  };

  private readonly handleMouseMove = (event: MouseEvent): void => {
    if (this.isPointerLocked()) {
      this.pendingYaw -= event.movementX * CAMERA_CONFIG.MOUSE_SENSITIVITY;
      this.pendingPitch += event.movementY * CAMERA_CONFIG.MOUSE_SENSITIVITY;
      return;
    }
    if (!this.dragMouseDown) return;
    const dx = event.clientX - this.lastMouseX;
    const dy = event.clientY - this.lastMouseY;
    this.lastMouseX = event.clientX;
    this.lastMouseY = event.clientY;

    this.pendingYaw -= dx * CAMERA_CONFIG.MOUSE_SENSITIVITY;
    this.pendingPitch += dy * CAMERA_CONFIG.MOUSE_SENSITIVITY;
  };

  private readonly handleMouseUp = (): void => {
    this.dragMouseDown = false;
  };

  private readonly handleTouchStart = (event: TouchEvent): void => {
    event.preventDefault();
    this.setMode("touch");
    this.callbacks.onUserInteraction?.();
    if (this.cameraTouchId !== null) return;

    const touch = event.changedTouches[0];
    if (!touch) return;
    this.cameraTouchId = touch.identifier;
    this.lastTouchX = touch.clientX;
    this.lastTouchY = touch.clientY;
  };

  private readonly handleTouchMove = (event: TouchEvent): void => {
    if (this.cameraTouchId === null) return;
    event.preventDefault();

    for (const touch of Array.from(event.changedTouches)) {
      if (touch.identifier !== this.cameraTouchId) continue;
      const dx = touch.clientX - this.lastTouchX;
      const dy = touch.clientY - this.lastTouchY;
      this.lastTouchX = touch.clientX;
      this.lastTouchY = touch.clientY;

      this.pendingYaw -= dx * CAMERA_CONFIG.TOUCH_SENSITIVITY;
      this.pendingPitch += dy * CAMERA_CONFIG.TOUCH_SENSITIVITY;
    }
  };

  private readonly handleTouchEnd = (event: TouchEvent): void => {
    if (this.cameraTouchId === null) return;
    for (const touch of Array.from(event.changedTouches)) {
      if (touch.identifier === this.cameraTouchId) {
        this.cameraTouchId = null;
        break;
      }
    }
  };
}
