/** Manages the F3 / tap-button FPS counter overlay. */
export class FpsCounter {
  private readonly counterEl: HTMLElement | null;
  private readonly toggleButton: HTMLElement | null;
  private visible = false;

  constructor() {
    this.counterEl = document.getElementById("fps-counter");
    this.toggleButton = document.getElementById("fps-toggle");
    this.toggleButton?.addEventListener("click", this.toggle);
  }

  readonly toggle = (): void => {
    this.visible = !this.visible;
    this.counterEl?.classList.toggle("hidden", !this.visible);
  };

  setFps(fps: number): void {
    if (!this.visible || !this.counterEl) return;
    this.counterEl.textContent = `FPS: ${fps}`;
  }

  dispose(): void {
    this.toggleButton?.removeEventListener("click", this.toggle);
  }
}
