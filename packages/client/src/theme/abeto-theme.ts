/**
 * Unified Abeto-inspired color palette used across 3D materials, sky, outlines, and HUD.
 */
export const ABETO_PALETTE = {
  SKY_ZENITH: 0x3db8c9,
  SKY_HORIZON: 0x8be2df,
  SKY_CLOUD_LIGHT: 0xf4fbf9,
  SKY_CLOUD_MID: 0xbaeae6,

  GRASS_LIGHT: 0x9cd984,
  CONCRETE_LIGHT: 0xbac7d1,
  CONCRETE_MID: 0x8c9dab,
  FOLIAGE_DARK: 0x266d5a,
  TURQUOISE_ACCENT: 0x2ec4b6,
  ORANGE_ACCENT: 0xf97316,
  YELLOW_ACCENT: 0xfacc15,

  OUTLINE_INK: 0x1a2634,
  HEMI_SKY: 0xe6fbfb,
  HEMI_GROUND: 0x52757a,
  SUN_LIGHT: 0xfff8e6,

  CHAR_SKIN: 0xf2c8b0,
  CHAR_HAIR: 0x191d24,
  CHAR_HAIR_TIE: 0xe6a832,
  CHAR_SHIRT_CYAN: 0x38acc9,
  CHAR_SHIRT_WHITE: 0xe8ece8,
  CHAR_BAG: 0xe6a832,
  CHAR_PANTS: 0x1b1e24,
  CHAR_SOCKS: 0xe8ece8,
  CHAR_SHOES: 0x1e222a,
  CHAR_SHOE_ACCENT: 0xf1f5f9,
  CHAR_BACKPACK: 0x2ec4b6,
  CHAR_BACKPACK_STRAP: 0x1e8f85,
  CHAR_SHIRT: 0xe8ece8,
  CHAR_SHOE_SOLE: 0x14181f,

  HUD_PAPER: "#ffffff",
  HUD_INK: "#4a737a",
  HUD_SHADOW: "#1a2634",
} as const;

export interface PaletteSwatch {
  name: string;
  hex: string;
  role: string;
}

/** Palette swatches shown in the /lab comparison view. */
export const ABETO_SWATCHES: readonly PaletteSwatch[] = [
  { name: "Sky Zenith", hex: "#3DB8C9", role: "Upper sky gradient" },
  { name: "Sky Horizon", hex: "#8BE2DF", role: "Lower sky & light fog" },
  { name: "Turquoise", hex: "#2EC4B6", role: "Backpack & primary accent" },
  { name: "Dark Foliage", hex: "#266D5A", role: "Trees & deep greens" },
  { name: "Grass", hex: "#9CD984", role: "Ground & park terrain" },
  { name: "Blue-Gray", hex: "#8C9DAB", role: "Concrete walls & roads" },
  { name: "Orange Accent", hex: "#F97316", role: "Cones & props" },
  { name: "Outline Ink", hex: "#1A2634", role: "Outlines, hair & shadows" },
];
