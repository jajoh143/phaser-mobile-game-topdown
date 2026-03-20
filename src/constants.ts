export const TILE_SIZE = 32
export const SCALE = 2

// Responsive canvas: wider on desktop, portrait on mobile
const _w = typeof window !== 'undefined' ? window.innerWidth  : 360
const _h = typeof window !== 'undefined' ? window.innerHeight : 640
const _mobile = _w < 768
export const GAME_WIDTH  = _mobile ? 360 : Math.min(_w, 1280)
export const GAME_HEIGHT = _mobile ? 640 : Math.min(_h, 800)

export const PLAYER_SPEED = 120

// Joystick
export const JOYSTICK_RADIUS = 50
export const JOYSTICK_THUMB_RADIUS = 22
