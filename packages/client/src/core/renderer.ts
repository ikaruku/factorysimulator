import * as THREE from "three";
import { RENDER_CONFIG } from "@factory-simulator/shared";

/** Creates and manages the WebGL2 renderer and responsive viewport sizing. */
export class WorldRenderer {
  readonly renderer: THREE.WebGLRenderer;

  constructor(
    private readonly container: HTMLElement,
    private readonly onResizeCallback: (aspect: number) => void,
  ) {
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: "high-performance",
    });
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;

    this.applySize();
    this.container.appendChild(this.renderer.domElement);
    window.addEventListener("resize", this.handleResize);
  }

  setTouchMode(isTouch: boolean): void {
    const cap = isTouch ? RENDER_CONFIG.MOBILE_PIXEL_RATIO : RENDER_CONFIG.MAX_PIXEL_RATIO;
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, cap));
  }

  render(scene: THREE.Scene, camera: THREE.Camera): void {
    this.renderer.render(scene, camera);
  }

  dispose(): void {
    window.removeEventListener("resize", this.handleResize);
    this.renderer.dispose();
  }

  private readonly handleResize = (): void => {
    this.applySize();
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;
    this.onResizeCallback(width / Math.max(height, 1));
  };

  private applySize(): void {
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;
    const isCoarsePointer = window.matchMedia("(pointer: coarse)").matches;
    this.setTouchMode(isCoarsePointer);
    this.renderer.setSize(width, height, false);
  }
}
