import * as THREE from "three";

const WALK_CYCLE_FREQ = 10;
const RUN_CYCLE_FREQ = 15;
const IDLE_BREATH_FREQ = 2.2;

/**
 * Procedural low-poly character with idle, walk, and run animations.
 * Faces local -Z when rotation.y is 0.
 */
export class LowPolyCharacter {
  readonly group = new THREE.Group();
  private readonly bodyPivot = new THREE.Group();
  private readonly head: THREE.Mesh;
  private readonly leftArmPivot = new THREE.Group();
  private readonly rightArmPivot = new THREE.Group();
  private readonly leftLegPivot = new THREE.Group();
  private readonly rightLegPivot = new THREE.Group();
  private animTime = 0;

  constructor() {
    const skinMat = new THREE.MeshStandardMaterial({ color: 0xf6c7a6, roughness: 0.75 });
    const shirtMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.7 });
    const pantsMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
    const shoeMat = new THREE.MeshStandardMaterial({ color: 0xef4444, roughness: 0.65 });
    const packMat = new THREE.MeshStandardMaterial({ color: 0x2dd4bf, roughness: 0.7 });
    const hairMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.85 });

    this.group.add(this.bodyPivot);

    // Legs (origin at hip y = 0.62)
    this.leftLegPivot.position.set(-0.14, 0.62, 0);
    this.rightLegPivot.position.set(0.14, 0.62, 0);
    this.leftLegPivot.add(this.createLegMesh(pantsMat, shoeMat));
    this.rightLegPivot.add(this.createLegMesh(pantsMat, shoeMat));
    this.bodyPivot.add(this.leftLegPivot, this.rightLegPivot);

    // Torso
    const torso = new THREE.Mesh(new THREE.BoxGeometry(0.52, 0.62, 0.28), shirtMat);
    torso.position.y = 0.93;
    torso.castShadow = true;
    this.bodyPivot.add(torso);

    // Backpack on +Z (character's back)
    const backpack = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.44, 0.18), packMat);
    backpack.position.set(0, 0.95, 0.21);
    backpack.castShadow = true;
    this.bodyPivot.add(backpack);

    // Arms (origin at shoulder y = 1.18)
    this.leftArmPivot.position.set(-0.35, 1.18, 0);
    this.rightArmPivot.position.set(0.35, 1.18, 0);
    this.leftArmPivot.add(this.createArmMesh(shirtMat, skinMat));
    this.rightArmPivot.add(this.createArmMesh(shirtMat, skinMat));
    this.bodyPivot.add(this.leftArmPivot, this.rightArmPivot);

    // Head + hair cap
    this.head = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.42, 0.42), skinMat);
    this.head.position.y = 1.48;
    this.head.castShadow = true;

    const hair = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.18, 0.45), hairMat);
    hair.position.y = 0.16;
    hair.castShadow = true;
    this.head.add(hair);

    this.bodyPivot.add(this.head);
  }

  /** Updates procedural limb swing and breathing bob based on planar speed ratio (0..1+). */
  updateAnimation(speedRatio: number, isRunning: boolean, dt: number): void {
    const moving = speedRatio > 0.05;
    if (!moving) {
      this.animTime += dt * IDLE_BREATH_FREQ;
      const breath = Math.sin(this.animTime) * 0.015;
      this.bodyPivot.position.y = breath;
      this.leftLegPivot.rotation.x = THREE.MathUtils.lerp(this.leftLegPivot.rotation.x, 0, 0.2);
      this.rightLegPivot.rotation.x = THREE.MathUtils.lerp(this.rightLegPivot.rotation.x, 0, 0.2);
      this.leftArmPivot.rotation.x = THREE.MathUtils.lerp(this.leftArmPivot.rotation.x, 0, 0.2);
      this.rightArmPivot.rotation.x = THREE.MathUtils.lerp(this.rightArmPivot.rotation.x, 0, 0.2);
      return;
    }

    const freq = isRunning ? RUN_CYCLE_FREQ : WALK_CYCLE_FREQ;
    this.animTime += dt * freq * Math.min(speedRatio, 1.4);

    const swingAmp = isRunning ? 0.8 : 0.55;
    const swing = Math.sin(this.animTime) * swingAmp;
    this.leftLegPivot.rotation.x = swing;
    this.rightLegPivot.rotation.x = -swing;
    this.leftArmPivot.rotation.x = -swing * 0.8;
    this.rightArmPivot.rotation.x = swing * 0.8;
    this.bodyPivot.position.y = Math.abs(Math.sin(this.animTime)) * (isRunning ? 0.08 : 0.04);
  }

  private createLegMesh(pantsMat: THREE.Material, shoeMat: THREE.Material): THREE.Group {
    const legGroup = new THREE.Group();
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.48, 0.22), pantsMat);
    leg.position.y = -0.24;
    leg.castShadow = true;

    const shoe = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.14, 0.3), shoeMat);
    shoe.position.set(0, -0.55, -0.04);
    shoe.castShadow = true;

    legGroup.add(leg, shoe);
    return legGroup;
  }

  private createArmMesh(shirtMat: THREE.Material, skinMat: THREE.Material): THREE.Group {
    const armGroup = new THREE.Group();
    const sleeve = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.26, 0.18), shirtMat);
    sleeve.position.y = -0.13;
    sleeve.castShadow = true;

    const hand = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.26, 0.14), skinMat);
    hand.position.y = -0.38;
    hand.castShadow = true;

    armGroup.add(sleeve, hand);
    return armGroup;
  }
}
