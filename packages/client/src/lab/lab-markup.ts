import {
  BAG_SKIN_OPTIONS,
  BOTTOM_SKIN_OPTIONS,
  SHOES_SKIN_OPTIONS,
  TOP_SKIN_OPTIONS,
  VISUAL_CONFIG,
  type CharacterLoadout,
} from "@factory-simulator/shared";
import { ABETO_SWATCHES } from "../theme/abeto-theme";

const STICKER_ICONS: readonly { label: string; svg: string }[] = [
  {
    label: "Menu",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h12"/></svg>`,
  },
  {
    label: "Music",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/></svg>`,
  },
  {
    label: "Outfit",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 5l4 2 4-2 4 3-2 4-2-1v9H8v-9l-2 1-2-4 4-3z"/></svg>`,
  },
  {
    label: "Emote",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9 10h.01M15 10h.01M8.5 14.5c1 1.5 2.2 2 3.5 2s2.5-.5 3.5-2"/></svg>`,
  },
];

function buildSelectOptions<T extends { readonly id: string; readonly label: string }>(
  options: readonly T[],
  selectedId: string,
): string {
  return options
    .map(
      (o) => `<option value="${o.id}" ${o.id === selectedId ? "selected" : ""}>${o.label}</option>`,
    )
    .join("");
}

/** Builds the HTML shell for the Stage 1B /lab visual comparison page. */
export function buildLabMarkup(initialLoadout: CharacterLoadout): string {
  const swatchesHtml = ABETO_SWATCHES.map(
    (s) => `
      <div class="lab-swatch">
        <span class="lab-swatch-chip" style="background:${s.hex}"></span>
        <div>
          <div class="lab-swatch-name">${s.name} <code>${s.hex}</code></div>
          <div class="lab-swatch-role">${s.role}</div>
        </div>
      </div>`,
  ).join("");

  const stickersHtml = STICKER_ICONS.map(
    (item) => `
      <button class="sticker-btn" type="button" title="${item.label}">
        ${item.svg}
        <span>${item.label}</span>
      </button>`,
  ).join("");

  const topOptionsHtml = buildSelectOptions(TOP_SKIN_OPTIONS, initialLoadout.top);
  const bottomOptionsHtml = buildSelectOptions(BOTTOM_SKIN_OPTIONS, initialLoadout.bottom);
  const shoesOptionsHtml = buildSelectOptions(SHOES_SKIN_OPTIONS, initialLoadout.shoes);
  const bagOptionsHtml = buildSelectOptions(BAG_SKIN_OPTIONS, initialLoadout.bag);

  return `
    <div class="lab-shell">
      <div class="lab-viewport-wrap">
        <div id="lab-canvas" class="lab-canvas"></div>
        <div class="lab-toolbar">
          <a class="hud-button lab-link" href="/">Back to World</a>
          <button id="lab-gender-male" class="hud-button" type="button">
            Male (Default)
          </button>
          <button id="lab-gender-female" class="hud-button" type="button">
            Female (Default)
          </button>
          <button id="lab-anim-btn" class="hud-button" type="button" aria-pressed="false">
            Anim: Idle
          </button>
          <button id="lab-outline-btn" class="hud-button" type="button">Outlines: ON</button>
          <label class="hud-pill lab-slider-label">
            Thickness
            <input id="lab-thickness" type="range" min="0.5" max="3.0" step="0.1" value="${VISUAL_CONFIG.OUTLINE_THICKNESS_PX}" />
            <span id="lab-thickness-val">${VISUAL_CONFIG.OUTLINE_THICKNESS_PX.toFixed(1)}px</span>
          </label>
        </div>
        <div class="hud-pill lab-caption">
          4-side character (Front · Right · Back · Left), modular outfit slots &amp; 1.0px outlines · Drag to orbit
        </div>
      </div>

      <aside class="lab-sidebar">
        <section class="lab-card">
          <h2>Modular Character &amp; Outfit Slots</h2>
          <p class="lab-note">Switch gender default designs or mix modular Top, Bottom, Shoes, and Bag slots.</p>
          <div class="lab-swatches">
            <label class="lab-swatch">
              <div style="width:100%">
                <div class="lab-swatch-name">Top <code>TopMesh</code></div>
                <select id="lab-slot-top" class="settings-action" style="margin-top:4px;width:100%">${topOptionsHtml}</select>
              </div>
            </label>
            <label class="lab-swatch">
              <div style="width:100%">
                <div class="lab-swatch-name">Bottom <code>BottomMesh</code></div>
                <select id="lab-slot-bottom" class="settings-action" style="margin-top:4px;width:100%">${bottomOptionsHtml}</select>
              </div>
            </label>
            <label class="lab-swatch">
              <div style="width:100%">
                <div class="lab-swatch-name">Shoes <code>ShoesMesh</code></div>
                <select id="lab-slot-shoes" class="settings-action" style="margin-top:4px;width:100%">${shoesOptionsHtml}</select>
              </div>
            </label>
            <label class="lab-swatch">
              <div style="width:100%">
                <div class="lab-swatch-name">Bag <code>BagMesh</code></div>
                <select id="lab-slot-bag" class="settings-action" style="margin-top:4px;width:100%">${bagOptionsHtml}</select>
              </div>
            </label>
          </div>
        </section>
        <section class="lab-card">
          <h2>Abeto Color Palette</h2>
          <div class="lab-swatches">${swatchesHtml}</div>
        </section>
        <section class="lab-card">
          <h2>HUD Sticker Samples</h2>
          <p class="lab-note">Press buttons to preview paper-sticker tactile shift.</p>
          <div class="lab-stickers">${stickersHtml}</div>
        </section>
      </aside>
    </div>`;
}
