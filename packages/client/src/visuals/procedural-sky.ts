import * as THREE from "three";
import { VISUAL_CONFIG } from "@factory-simulator/shared";
import { ABETO_PALETTE } from "../theme/abeto-theme";

export interface ProceduralSky {
  mesh: THREE.Mesh;
  update: (dt: number) => void;
}

const SKY_VERTEX_SHADER = /* glsl */ `
  varying vec3 vWorldDir;
  void main() {
    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vWorldDir = normalize(position);
    gl_Position = projectionMatrix * viewMatrix * worldPosition;
  }
`;

const SKY_FRAGMENT_SHADER = /* glsl */ `
  uniform vec3 uZenithColor;
  uniform vec3 uHorizonColor;
  uniform vec3 uCloudLightColor;
  uniform vec3 uCloudMidColor;
  uniform float uTime;
  varying vec3 vWorldDir;

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
  }

  float fbm(vec2 p) {
    float v = 0.0;
    float amp = 0.5;
    for (int i = 0; i < 4; i++) {
      v += amp * noise(p);
      p = p * 2.02 + vec2(13.1, 7.7);
      amp *= 0.5;
    }
    return v;
  }

  void main() {
    float h = clamp(vWorldDir.y, 0.0, 1.0);
    vec3 sky = mix(uHorizonColor, uZenithColor, pow(h, 0.65));

    // Painterly horizontal cloud strokes across the sky dome
    float angle = atan(vWorldDir.z, vWorldDir.x);
    vec2 strokeUv = vec2(angle * 2.4 + uTime, h * 7.5);
    float brush = fbm(strokeUv * vec2(1.4, 2.8));
    float detail = fbm(strokeUv * vec2(4.2, 6.0) + vec2(uTime * 1.4, 0.0));
    float bandMask = smoothstep(0.06, 0.25, h) * (1.0 - smoothstep(0.62, 0.95, h));

    float cloudShape = (brush * 0.68 + detail * 0.32) * bandMask;
    float midBand = step(0.36, cloudShape);
    float lightBand = step(0.47, cloudShape);

    sky = mix(sky, uCloudMidColor, midBand * 0.55);
    sky = mix(sky, uCloudLightColor, lightBand * 0.85);

    gl_FragColor = vec4(sky, 1.0);
  }
`;

/** Creates a procedural turquoise sky dome with slow-moving painterly cloud strokes. */
export function createProceduralSky(radius: number = 260): ProceduralSky {
  const geometry = new THREE.SphereGeometry(radius, 32, 20);
  const uniforms = {
    uZenithColor: { value: new THREE.Color(ABETO_PALETTE.SKY_ZENITH) },
    uHorizonColor: { value: new THREE.Color(ABETO_PALETTE.SKY_HORIZON) },
    uCloudLightColor: { value: new THREE.Color(ABETO_PALETTE.SKY_CLOUD_LIGHT) },
    uCloudMidColor: { value: new THREE.Color(ABETO_PALETTE.SKY_CLOUD_MID) },
    uTime: { value: 0 },
  };

  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: SKY_VERTEX_SHADER,
    fragmentShader: SKY_FRAGMENT_SHADER,
    side: THREE.BackSide,
    depthWrite: false,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.userData.isSky = true;
  mesh.frustumCulled = false;

  return {
    mesh,
    update: (dt: number) => {
      uniforms.uTime.value += dt * VISUAL_CONFIG.SKY_CLOUD_SPEED;
    },
  };
}
