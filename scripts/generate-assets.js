#!/usr/bin/env node
/**
 * scripts/generate-assets.js
 *
 * Generates the game's sprite PNGs from the same pixel data defined in the
 * Aseprite source scripts (scripts/aseprite/*.lua).
 *
 * Run:  node scripts/generate-assets.js
 *
 * No third-party dependencies — uses only built-in Node.js modules (zlib, fs).
 * Intended for CI / initial project setup when Aseprite is not available.
 * For day-to-day sprite editing, open the .lua scripts in Aseprite instead.
 */

import { deflateSync } from 'zlib'
import { writeFileSync, mkdirSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const OUT = join(__dirname, '..', 'public', 'assets')
mkdirSync(OUT, { recursive: true })

// ── Minimal PNG encoder ────────────────────────────────────────────────────────

const crcTable = new Uint32Array(256)
for (let i = 0; i < 256; i++) {
  let c = i
  for (let j = 0; j < 8; j++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1)
  crcTable[i] = c
}

function crc32(buf) {
  let c = 0xFFFFFFFF
  for (let i = 0; i < buf.length; i++) c = crcTable[(c ^ buf[i]) & 0xFF] ^ (c >>> 8)
  return (c ^ 0xFFFFFFFF) >>> 0
}

function buildPNG(width, height, pixels) {
  // Build scanlines: filter byte (0 = None) + RGBA pixels
  const rows = []
  for (let y = 0; y < height; y++) {
    const row = Buffer.alloc(1 + width * 4)
    row[0] = 0
    for (let x = 0; x < width; x++) {
      const s = (y * width + x) * 4
      row.set(pixels.subarray(s, s + 4), 1 + x * 4)
    }
    rows.push(row)
  }

  function chunk(type, data) {
    const typeBytes = Buffer.from(type, 'ascii')
    const len = Buffer.allocUnsafe(4)
    len.writeUInt32BE(data.length, 0)
    const crcBytes = Buffer.allocUnsafe(4)
    crcBytes.writeUInt32BE(crc32(Buffer.concat([typeBytes, data])), 0)
    return Buffer.concat([len, typeBytes, data, crcBytes])
  }

  const ihdr = Buffer.alloc(13)
  ihdr.writeUInt32BE(width, 0)
  ihdr.writeUInt32BE(height, 4)
  ihdr[8] = 8; ihdr[9] = 6  // bit-depth=8, colour-type=RGBA

  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),  // PNG signature
    chunk('IHDR', ihdr),
    chunk('IDAT', deflateSync(Buffer.concat(rows))),
    chunk('IEND', Buffer.alloc(0)),
  ])
}

// ── PixelCanvas ───────────────────────────────────────────────────────────────

class PixelCanvas {
  constructor(width, height) {
    this.width = width
    this.height = height
    this.pixels = new Uint8Array(width * height * 4)  // transparent by default
  }

  fillRect(x, y, w, h, r, g, b, a = 255) {
    for (let py = y; py < y + h; py++) {
      for (let px = x; px < x + w; px++) {
        if (px < 0 || py < 0 || px >= this.width || py >= this.height) continue
        const i = (py * this.width + px) * 4
        this.pixels[i] = r; this.pixels[i + 1] = g
        this.pixels[i + 2] = b; this.pixels[i + 3] = a
      }
    }
  }

  save(filename) {
    const buf = buildPNG(this.width, this.height, this.pixels)
    writeFileSync(join(OUT, filename), buf)
    console.log(`  wrote public/assets/${filename}  (${this.width}×${this.height})`)
  }
}

// ── Player sprite sheet (48×64) ───────────────────────────────────────────────
// 3 columns (idle, walk-1, walk-2) × 4 rows (down, up, left, right)
// Each cell 16×16 px — matches BootScene.ts frame registration.

const player = new PixelCanvas(48, 64)

const dirBodyColors = [
  [0x4a, 0x9a, 0xde],  // down
  [0x3a, 0x7a, 0xbf],  // up
  [0x2a, 0x5a, 0x9f],  // left
  [0x5a, 0xb0, 0xee],  // right
]

for (let row = 0; row < 4; row++) {
  const [br, bg, bb] = dirBodyColors[row]
  for (let col = 0; col < 3; col++) {
    const x = col * 16, y = row * 16

    // Body
    player.fillRect(x + 4, y + 5,  8, 9,  br, bg, bb)
    // Head
    player.fillRect(x + 5, y + 1,  6, 5,  0xf4, 0xc2, 0xa1)
    // Legs — col 0 = idle, col 1 = stride left, col 2 = stride right
    const legOff = col === 1 ? -1 : col === 2 ? 1 : 0
    player.fillRect(x + 4, y + 12, 3, 3 + legOff, 0x2d, 0x5a, 0x8e)
    player.fillRect(x + 9, y + 12, 3, 3 - legOff, 0x2d, 0x5a, 0x8e)
  }
}

player.save('player.png')

// ── NPC sprite (16×16) ────────────────────────────────────────────────────────

const npc = new PixelCanvas(16, 16)
npc.fillRect(4,  5, 8, 9, 0xe0, 0x7b, 0x3a)  // body
npc.fillRect(5,  1, 6, 5, 0xf4, 0xd0, 0xa1)  // head
npc.fillRect(4, 12, 3, 3, 0x8b, 0x45, 0x13)  // left leg
npc.fillRect(9, 12, 3, 3, 0x8b, 0x45, 0x13)  // right leg
// Indicator stem clips to y=0; dot at y=2-3 sits behind head — matches BootScene
npc.fillRect(7, -4, 2, 5, 0xff, 0xff, 0x00)
npc.fillRect(7,  2, 2, 2, 0xff, 0xff, 0x00)

npc.save('npc.png')

// ── World tiles (64×32) ───────────────────────────────────────────────────────
// Two 32×32 tiles side by side: x=0 grass, x=32 wall/stone.
// WorldScene crops to TILE_SIZE (32) per tile.

const tiles = new PixelCanvas(64, 32)

// Grass tile
tiles.fillRect( 0,  0, 32, 32, 0x4a, 0x7c, 0x59)
tiles.fillRect( 4,  8,  3,  3, 0x3d, 0x6b, 0x4a)
tiles.fillRect(18, 20,  4,  4, 0x3d, 0x6b, 0x4a)
tiles.fillRect(10, 25,  3,  2, 0x3d, 0x6b, 0x4a)

// Stone/wall tile
tiles.fillRect(32,  0, 32, 32, 0x7a, 0x7a, 0x7a)
tiles.fillRect(34,  2, 12, 12, 0x5a, 0x5a, 0x5a)
tiles.fillRect(48, 16, 12, 12, 0x5a, 0x5a, 0x5a)
tiles.fillRect(34, 18, 10, 10, 0x5a, 0x5a, 0x5a)

tiles.save('tiles.png')

console.log('\nDone. Open scripts/aseprite/*.lua in Aseprite to edit sprites visually.')
