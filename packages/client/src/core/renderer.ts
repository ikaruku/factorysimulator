import * as THREE from "three";
import { RENDER_CONFIG } from "@factory-simulator/shared";

export interface ViewportDimensions {
  width: number;
  height: number;
  pixelRatio: number;
}

/** Creates and manages the WebGL2 renderer with crisp hard shadows and flat color fidelity. */
export class WorldRenderer {
  readonly renderer: THREE.WebGLRenderer;
  private pixelRatio = 1;

  constructor(
    private readonly container: HTMLElement,
    private readonly onResizeCallback: (aspect: number, dims: ViewportDimensions) => void,
  ) {
    this.renderer = new THREE.WebGLRenderer({
      antialias: false,
      powerPreference: "high-performance",
    });
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.BasicShadowMap;
    this.renderer.toneMapping = THREE.NoToneMapping;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;

    this.applySize();
    this.container.appendChild(this.renderer.domElement);
    window.addEventListener("resize", this.handleResize);
  }

  getDimensions(): ViewportDimensions {
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;
    return {
      width: Math.max(1, width),
      height: Math.max(1, height),
      pixelRatio: this.pixelRatio,
    };
  }

  setTouchMode(isTouch: boolean): ViewportDimensions {
    const cap = isTouch ? RENDER_CONFIG.MOBILE_PIXEL_RATIO : RENDER_CONFIG.MAX_PIXEL_RATIO;
    this.pixelRatio = Math.min(window.devicePixelRatio || 1, cap);
    this.renderer.setPixelRatio(this.pixelRatio);
    return this.getDimensions();
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
    const dims = this.getDimensions();
    this.onResizeCallback(dims.width / Math.max(dims.height, 1), dims);
  };

  private applySize(): void {
    const dims = this.getDimensions();
    const isCoarsePointer = window.matchMedia("(pointer: coarse)").matches;
    this.setTouchMode(isCoarsePointer);
    this.renderer.setSize(dims.width, dims.height, false);
  }
}
