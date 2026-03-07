/**
 * Returns true if the device has touch input (phone/tablet).
 * Uses maxTouchPoints which is reliable across modern browsers.
 */
export function isMobile(): boolean {
  return navigator.maxTouchPoints > 0
}
