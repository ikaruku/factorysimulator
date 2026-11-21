import { MOVEMENT_CONFIG } from "@factory-simulator/shared";

export interface JoystickVector {
  x: number;
  forward: number;
  run: boolean;
}

/**
 * Multi-touch virtual joystick in the bottom-left corner for phones and tablets.
 * Outer deflection beyond TOUCH_RUN_THRESHOLD automatically activates running.
 */
export class VirtualJoystick {
  private readonly zone: HTMLElement | null;
  private readonly base: HTMLElement | null;
  private readonly knob: HTMLElement | null;
  private activeTouchId: number | null = null;
  private maxRadiusPx = 42;

  constructor(private readonly onChange: (vec: JoystickVector) => void) {
    this.zone = document.getElementById("joystick-zone");
    this.base = document.getElementById("joystick-base");
    this.knob = document.getElementById("joystick-knob");

    this.zone?.addEventListener("touchstart", this.handleTouchStart, { passive: false });
    this.zone?.addEventListener("touchmove", this.handleTouchMove, { passive: false });
    this.zone?.addEventListener("touchend", this.handleTouchEnd);
    this.zone?.addEventListener("touchcancel", this.handleTouchEnd);
  }

  setVisible(visible: boolean): void {
    this.zone?.classList.toggle("hidden", !visible);
    this.zone?.setAttribute("aria-hidden", String(!visible));
    if (!visible) this.reset();
  }

  dispose(): void {
    this.zone?.removeEventListener("touchstart", this.handleTouchStart);
    this.zone?.removeEventListener("touchmove", this.handleTouchMove);
    this.zone?.removeEventListener("touchend", this.handleTouchEnd);
    this.zone?.removeEventListener("touchcancel", this.handleTouchEnd);
  }

  private readonly handleTouchStart = (event: TouchEvent): void => {
    event.preventDefault();
    event.stopPropagation();
    if (this.activeTouchId !== null) return;
    const touch = event.changedTouches[0];
    if (!touch) return;
    this.activeTouchId = touch.identifier;
    this.updateFromTouch(touch);
  };

  private readonly handleTouchMove = (event: TouchEvent): void => {
    if (this.activeTouchId === null) return;
    event.preventDefault();
    event.stopPropagation();

    for (const touch of Array.from(event.changedTouches)) {
      if (touch.identifier === this.activeTouchId) {
        this.updateFromTouch(touch);
        break;
      }
    }
  };

  private readonly handleTouchEnd = (event: TouchEvent): void => {
    if (this.activeTouchId === null) return;
    for (const touch of Array.from(event.changedTouches)) {
      if (touch.identifier === this.activeTouchId) {
        this.reset();
        break;
      }
    }
  };

  private updateFromTouch(touch: Touch): void {
    if (!this.base || !this.knob) return;
    const rect = this.base.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    this.maxRadiusPx = Math.max(rect.width * 0.36, 24);

    const dx = touch.clientX - centerX;
    const dy = touch.clientY - centerY;
    const distance = Math.hypot(dx, dy);
    const clamped = Math.min(distance, this.maxRadiusPx);
    const angle = Math.atan2(dy, dx);

    const offsetX = Math.cos(angle) * clamped;
    const offsetY = Math.sin(angle) * clamped;
    this.knob.style.transform = `translate(${offsetX}px, ${offsetY}px)`;

    const normX = offsetX / this.maxRadiusPx;
    const normForward = -offsetY / this.maxRadiusPx;
    const magnitude = Math.hypot(normX, normForward);
    const run = magnitude >= MOVEMENT_CONFIG.TOUCH_RUN_THRESHOLD;

    this.base.classList.toggle("running", run);
    this.onChange({ x: normX, forward: normForward, run });
  }

  private reset(): void {
    this.activeTouchId = null;
    if (this.knob) this.knob.style.transform = "translate(0px, 0px)";
    this.base?.classList.remove("running");
    this.onChange({ x: 0, forward: 0, run: false });
  }
}
