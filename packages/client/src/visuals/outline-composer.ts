import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { ShaderPass } from "three/examples/jsm/postprocessing/ShaderPass.js";
import { CAMERA_CONFIG, VISUAL_CONFIG } from "@factory-simulator/shared";
import { ABETO_PALETTE } from "../theme/abeto-theme";

const EDGE_VERTEX_SHADER = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const EDGE_FRAGMENT_SHADER = /* glsl */ `
  uniform sampler2D tDiffuse;
  uniform sampler2D tNormal;
  uniform sampler2D tDepth;
  uniform vec2 uTexelSize;
  uniform vec3 uOutlineColor;
  uniform float uDepthThreshold;
  uniform float uNormalThreshold;
  uniform float uNear;
  uniform float uFar;
  varying vec2 vUv;

  float toLinearDepth(float rawDepth) {
    float z = rawDepth * 2.0 - 1.0;
    return (2.0 * uNear * uFar) / (uFar + uNear - z * (uFar - uNear));
  }

  vec3 decodeNormal(vec2 uv) {
    return normalize(texture2D(tNormal, uv).rgb * 2.0 - 1.0);
  }

  void main() {
    vec4 baseColor = texture2D(tDiffuse, vUv);

    // Half-texel Roberts Cross kernel keeps outlines crisp (~1-1.5px) even on thin limbs
    vec2 halfStep = uTexelSize * 0.5;
    vec2 offset0 = vec2(-halfStep.x, -halfStep.y);
    vec2 offset1 = vec2( halfStep.x,  halfStep.y);
    vec2 offset2 = vec2(-halfStep.x,  halfStep.y);
    vec2 offset3 = vec2( halfStep.x, -halfStep.y);

    float rawC = texture2D(tDepth, vUv).r;
    float raw0 = texture2D(tDepth, vUv + offset0).r;
    float raw1 = texture2D(tDepth, vUv + offset1).r;
    float raw2 = texture2D(tDepth, vUv + offset2).r;
    float raw3 = texture2D(tDepth, vUv + offset3).r;

    float dC = toLinearDepth(rawC);
    float d0 = toLinearDepth(raw0);
    float d1 = toLinearDepth(raw1);
    float d2 = toLinearDepth(raw2);
    float d3 = toLinearDepth(raw3);

    // Roberts Cross depth edge scaled by linear distance and grazing angle to avoid floor flicker
    vec3 nC = decodeNormal(vUv);
    float grazingFactor = 1.0 + (1.0 - clamp(abs(nC.z), 0.0, 1.0)) * 5.0;
    float depthDiagA = abs(d0 - d1);
    float depthDiagB = abs(d2 - d3);
    float depthEdge = sqrt(depthDiagA * depthDiagA + depthDiagB * depthDiagB);
    float scaledDepthThreshold = uDepthThreshold * max(dC, 1.0) * grazingFactor;
    float isDepthEdge = step(scaledDepthThreshold, depthEdge);

    // Angular crease test (1 - dot) triggers only on sharp corners (>~57 deg), keeping spheres & limbs clean
    float isForeground = step(rawC, 0.9995);
    vec3 n0 = decodeNormal(vUv + offset0);
    vec3 n1 = decodeNormal(vUv + offset1);
    vec3 n2 = decodeNormal(vUv + offset2);
    vec3 n3 = decodeNormal(vUv + offset3);
    float creaseA = 1.0 - clamp(dot(n0, n1), -1.0, 1.0);
    float creaseB = 1.0 - clamp(dot(n2, n3), -1.0, 1.0);
    float isNormalEdge = step(uNormalThreshold, max(creaseA, creaseB)) * isForeground;

    float edge = max(isDepthEdge, isNormalEdge);
    vec3 finalRgb = mix(baseColor.rgb, uOutlineColor, edge);
    gl_FragColor = vec4(finalRgb, baseColor.a);
  }
`;

/**
 * Post-processing renderer with depth + surface-normal Roberts Cross edge detection.
 * Can be disabled on weak phones to bypass post-processing completely.
 */
export class OutlineComposer {
  private readonly composer: EffectComposer;
  private readonly normalTarget: THREE.WebGLRenderTarget;
  private readonly normalMaterial = new THREE.MeshNormalMaterial();
  private readonly texelUniform = new THREE.Vector2(1 / 1280, 1 / 720);
  private readonly nearUniform: { value: number } = { value: CAMERA_CONFIG.NEAR_PLANE_M };
  private readonly farUniform: { value: number } = { value: CAMERA_CONFIG.FAR_PLANE_M };
  private outlinesEnabled = true;
  private thicknessPx: number = VISUAL_CONFIG.OUTLINE_THICKNESS_PX;
  private width = 1;
  private height = 1;
  private pixelRatio = 1;

  constructor(
    private readonly renderer: THREE.WebGLRenderer,
    private readonly scene: THREE.Scene,
    private readonly camera: THREE.PerspectiveCamera,
  ) {
    const depthTexture = new THREE.DepthTexture(1, 1);
    depthTexture.minFilter = THREE.NearestFilter;
    depthTexture.magFilter = THREE.NearestFilter;

    this.normalTarget = new THREE.WebGLRenderTarget(1, 1, {
      minFilter: THREE.NearestFilter,
      magFilter: THREE.NearestFilter,
      depthTexture,
    });

    const outlineMaterial = new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse: { value: null },
        tNormal: { value: this.normalTarget.texture },
        tDepth: { value: depthTexture },
        uTexelSize: { value: this.texelUniform },
        uOutlineColor: { value: new THREE.Color(ABETO_PALETTE.OUTLINE_INK) },
        uDepthThreshold: { value: VISUAL_CONFIG.OUTLINE_DEPTH_THRESHOLD },
        uNormalThreshold: { value: VISUAL_CONFIG.OUTLINE_NORMAL_THRESHOLD },
        uNear: this.nearUniform,
        uFar: this.farUniform,
      },
      vertexShader: EDGE_VERTEX_SHADER,
      fragmentShader: EDGE_FRAGMENT_SHADER,
    });

    this.composer = new EffectComposer(this.renderer);
    this.composer.addPass(new RenderPass(this.scene, this.camera));
    this.composer.addPass(new ShaderPass(outlineMaterial));
    this.composer.addPass(new OutputPass());
  }

  setOutlinesEnabled(enabled: boolean): void {
    this.outlinesEnabled = enabled;
  }

  isOutlinesEnabled(): boolean {
    return this.outlinesEnabled;
  }

  setThickness(thicknessPx: number): void {
    this.thicknessPx = Math.max(0.5, thicknessPx);
    this.updateTexelSize();
  }

  resize(width: number, height: number, pixelRatio: number): void {
    this.width = Math.max(1, Math.floor(width));
    this.height = Math.max(1, Math.floor(height));
    this.pixelRatio = Math.max(1, pixelRatio);

    this.composer.setPixelRatio(this.pixelRatio);
    this.composer.setSize(this.width, this.height);

    const bufferWidth = Math.max(1, Math.floor(this.width * this.pixelRatio));
    const bufferHeight = Math.max(1, Math.floor(this.height * this.pixelRatio));
    this.normalTarget.setSize(bufferWidth, bufferHeight);
    this.updateTexelSize();
  }

  render(): void {
    if (!this.outlinesEnabled) {
      this.renderer.render(this.scene, this.camera);
      return;
    }

    this.renderNormalAndDepthPass();
    this.nearUniform.value = this.camera.near;
    this.farUniform.value = this.camera.far;
    this.composer.render();
  }

  dispose(): void {
    this.normalTarget.dispose();
    this.normalMaterial.dispose();
    this.composer.dispose();
  }

  private renderNormalAndDepthPass(): void {
    const skippedObjects: THREE.Object3D[] = [];
    this.scene.traverse((obj) => {
      if ((obj.userData.isSky || obj.userData.skipOutline) && obj.visible) {
        obj.visible = false;
        skippedObjects.push(obj);
      }
    });

    const prevBackground = this.scene.background;
    const prevFog = this.scene.fog;
    const prevOverride = this.scene.overrideMaterial;
    const prevClearColor = new THREE.Color();
    this.renderer.getClearColor(prevClearColor);
    const prevClearAlpha = this.renderer.getClearAlpha();

    this.scene.background = null;
    this.scene.fog = null;
    this.scene.overrideMaterial = this.normalMaterial;

    this.renderer.setRenderTarget(this.normalTarget);
    this.renderer.setClearColor(0x8080ff, 1);
    this.renderer.clear(true, true, false);
    this.renderer.render(this.scene, this.camera);
    this.renderer.setRenderTarget(null);

    this.renderer.setClearColor(prevClearColor, prevClearAlpha);
    this.scene.overrideMaterial = prevOverride;
    this.scene.fog = prevFog;
    this.scene.background = prevBackground;

    for (const obj of skippedObjects) {
      obj.visible = true;
    }
  }

  private updateTexelSize(): void {
    const bufferWidth = Math.max(1, this.width * this.pixelRatio);
    const bufferHeight = Math.max(1, this.height * this.pixelRatio);
    const scale = this.thicknessPx * this.pixelRatio;
    this.texelUniform.set(scale / bufferWidth, scale / bufferHeight);
  }
}
