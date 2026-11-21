/** Shows the connection status text on the page. */
export function setStatus(text: string): void {
  const element = document.getElementById("status");
  if (element) element.textContent = text;
}
