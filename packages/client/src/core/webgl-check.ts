/** Checks whether the browser supports WebGL2 required by the renderer. */
export function isWebGl2Supported(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(window.WebGL2RenderingContext && canvas.getContext("webgl2"));
  } catch {
    return false;
  }
}

/** Shows a clear fallback message when WebGL2 is unavailable. */
export function showGraphicsError(message: string): void {
  const overlay = document.getElementById("error-overlay");
  const text = document.getElementById("error-message");
  if (text) text.textContent = message;
  if (overlay) overlay.classList.remove("hidden");
}
