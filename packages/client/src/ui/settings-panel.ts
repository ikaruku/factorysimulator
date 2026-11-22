import {
  BAG_SKIN_OPTIONS,
  DEFAULT_CHARACTER_LOADOUTS,
  TOP_SKIN_OPTIONS,
  getDefaultLoadoutForGender,
  type BagSkinId,
  type CharacterGender,
  type CharacterLoadout,
  type TopSkinId,
} from "@factory-simulator/shared";

const STORAGE_KEY_OUTLINES = "factory-simulator:outlines-enabled";
const STORAGE_KEY_CHARACTER_LOADOUT = "factory-simulator:character-loadout";

export interface SettingsCallbacks {
  onOutlinesChange: (enabled: boolean) => void;
  onCharacterLoadoutChange?: (loadout: CharacterLoadout) => void;
}

/** Reads saved outline preference (defaults to true). */
export function loadOutlinesPreference(): boolean {
  try {
    const saved = localStorage.getItem(STORAGE_KEY_OUTLINES);
    return saved === null ? true : saved === "true";
  } catch {
    return true;
  }
}

/** Saves outline preference to localStorage. */
export function saveOutlinesPreference(enabled: boolean): void {
  try {
    localStorage.setItem(STORAGE_KEY_OUTLINES, String(enabled));
  } catch {
    // Ignore storage errors in restricted browsing modes.
  }
}

/** Reads saved modular character loadout (defaults to Male Orange-Hoodie + Red-Backpack skin). */
export function loadCharacterLoadoutPreference(): CharacterLoadout {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_CHARACTER_LOADOUT);
    if (!raw) return { ...DEFAULT_CHARACTER_LOADOUTS.male };
    const parsed = JSON.parse(raw) as Partial<CharacterLoadout>;
    const gender: CharacterGender = parsed.gender === "female" ? "female" : "male";
    const def = DEFAULT_CHARACTER_LOADOUTS[gender];
    const topValid = TOP_SKIN_OPTIONS.some((o) => o.id === parsed.top);
    const bagValid = BAG_SKIN_OPTIONS.some((o) => o.id === parsed.bag);
    return {
      gender,
      top: topValid && parsed.top ? parsed.top : def.top,
      bottom: def.bottom,
      shoes: def.shoes,
      bag: bagValid && parsed.bag ? parsed.bag : def.bag,
    };
  } catch {
    return { ...DEFAULT_CHARACTER_LOADOUTS.male };
  }
}

/** Saves modular character loadout to localStorage. */
export function saveCharacterLoadoutPreference(loadout: CharacterLoadout): void {
  try {
    localStorage.setItem(STORAGE_KEY_CHARACTER_LOADOUT, JSON.stringify(loadout));
  } catch {
    // Ignore storage errors in restricted browsing modes.
  }
}

/**
 * Manages the graphics & character customization popover
 * (Gender selector, modular Top/Bag skin selectors, Outlines toggle, and /lab link).
 */
export class SettingsPanel {
  private readonly toggleBtn: HTMLElement | null;
  private readonly panel: HTMLElement | null;
  private readonly outlinesBtn: HTMLElement | null;
  private readonly genderBtn: HTMLElement | null;
  private readonly topBtn: HTMLElement | null;
  private readonly bagBtn: HTMLElement | null;
  private outlinesEnabled: boolean;
  private loadout: CharacterLoadout;

  constructor(private readonly callbacks: SettingsCallbacks) {
    this.toggleBtn = document.getElementById("settings-toggle");
    this.panel = document.getElementById("settings-panel");
    this.outlinesBtn = document.getElementById("outlines-toggle");
    this.genderBtn = document.getElementById("gender-toggle");
    this.topBtn = document.getElementById("top-skin-toggle");
    this.bagBtn = document.getElementById("bag-skin-toggle");

    this.outlinesEnabled = loadOutlinesPreference();
    this.loadout = loadCharacterLoadoutPreference();
    this.syncUi();

    this.toggleBtn?.addEventListener("click", this.togglePanel);
    this.outlinesBtn?.addEventListener("click", this.toggleOutlines);
    this.genderBtn?.addEventListener("click", this.cycleGender);
    this.topBtn?.addEventListener("click", this.cycleTopSkin);
    this.bagBtn?.addEventListener("click", this.cycleBagSkin);
  }

  isOutlinesEnabled(): boolean {
    return this.outlinesEnabled;
  }

  getCharacterLoadout(): CharacterLoadout {
    return { ...this.loadout };
  }

  dispose(): void {
    this.toggleBtn?.removeEventListener("click", this.togglePanel);
    this.outlinesBtn?.removeEventListener("click", this.toggleOutlines);
    this.genderBtn?.removeEventListener("click", this.cycleGender);
    this.topBtn?.removeEventListener("click", this.cycleTopSkin);
    this.bagBtn?.removeEventListener("click", this.cycleBagSkin);
  }

  private readonly togglePanel = (): void => {
    this.panel?.classList.toggle("hidden");
  };

  private readonly toggleOutlines = (): void => {
    this.outlinesEnabled = !this.outlinesEnabled;
    saveOutlinesPreference(this.outlinesEnabled);
    this.syncUi();
    this.callbacks.onOutlinesChange(this.outlinesEnabled);
  };

  private readonly cycleGender = (): void => {
    const nextGender: CharacterGender = this.loadout.gender === "male" ? "female" : "male";
    this.loadout = getDefaultLoadoutForGender(nextGender);
    this.persistAndNotifyLoadout();
  };

  private readonly cycleTopSkin = (): void => {
    const idx = TOP_SKIN_OPTIONS.findIndex((o) => o.id === this.loadout.top);
    const next = TOP_SKIN_OPTIONS[(idx + 1) % TOP_SKIN_OPTIONS.length];
    if (!next) return;
    this.loadout = { ...this.loadout, top: next.id as TopSkinId };
    this.persistAndNotifyLoadout();
  };

  private readonly cycleBagSkin = (): void => {
    const idx = BAG_SKIN_OPTIONS.findIndex((o) => o.id === this.loadout.bag);
    const next = BAG_SKIN_OPTIONS[(idx + 1) % BAG_SKIN_OPTIONS.length];
    if (!next) return;
    this.loadout = { ...this.loadout, bag: next.id as BagSkinId };
    this.persistAndNotifyLoadout();
  };

  private persistAndNotifyLoadout(): void {
    saveCharacterLoadoutPreference(this.loadout);
    this.syncUi();
    this.callbacks.onCharacterLoadoutChange?.({ ...this.loadout });
  }

  private syncUi(): void {
    if (this.outlinesBtn) {
      this.outlinesBtn.textContent = this.outlinesEnabled ? "Outlines: ON" : "Outlines: OFF";
      this.outlinesBtn.setAttribute("aria-pressed", String(this.outlinesEnabled));
    }
    if (this.genderBtn) {
      const label = this.loadout.gender === "male" ? "Male (Default)" : "Female (Default)";
      this.genderBtn.textContent = `Gender: ${label}`;
    }
    if (this.topBtn) {
      const opt = TOP_SKIN_OPTIONS.find((o) => o.id === this.loadout.top);
      this.topBtn.textContent = `Top: ${opt?.label ?? this.loadout.top}`;
    }
    if (this.bagBtn) {
      const opt = BAG_SKIN_OPTIONS.find((o) => o.id === this.loadout.bag);
      this.bagBtn.textContent = `Bag: ${opt?.label ?? this.loadout.bag}`;
    }
  }
}
