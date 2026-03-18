import Phaser from 'phaser'

export class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: 'BootScene' })
  }

  create() {
    // Generate placeholder textures programmatically so the game
    // works without external asset files.
    this.generateTextures()
    this.scene.start('PreloadScene')
  }

  private generateTextures() {
    // Player sprite sheet: 4 directions × 3 frames (idle + 2 walk)
    // Each frame is 16×16 px
    const FRAME_W = 16
    const FRAME_H = 16
    const COLS = 3
    const ROWS = 4 // down, up, left, right

    const playerGfx = this.make.graphics({ x: 0, y: 0 })

    const bodyColors = {
      down: 0x4a9ade,
      up: 0x3a7abf,
      left: 0x2a5a9f,
      right: 0x5ab0ee,
    }

    const skin = 0xf4c2a1
    const skinShadow = 0xc49a7a // mid-tone for nose — between skin and outline
    const hairColor = 0x6b3a1a // dark brown hair
    const eyeColor = 0x1a1a2e // near-black eyes
    const legColor = 0x2d5a8e

    const directions = ['down', 'up', 'left', 'right'] as const
    const rowColors = [bodyColors.down, bodyColors.up, bodyColors.left, bodyColors.right]

    for (let row = 0; row < ROWS; row++) {
      const dir = directions[row]
      const color = rowColors[row]
      for (let col = 0; col < COLS; col++) {
        const x = col * FRAME_W
        const y = row * FRAME_H

        // --- Body (shortened by 1px so legs are more visible) ---
        playerGfx.fillStyle(color, 1)
        playerGfx.fillRect(x + 4, y + 6, 8, 7) // y+6 to y+12

        // --- Head base (skin) ---
        playerGfx.fillStyle(skin, 1)
        playerGfx.fillRect(x + 5, y + 2, 6, 4) // y+2 to y+5

        // --- Hair ---
        playerGfx.fillStyle(hairColor, 1)
        if (dir === 'up') {
          // Back of head: hair covers entire head area
          playerGfx.fillRect(x + 5, y + 1, 6, 5)
        } else {
          // Hair on top of head (2 rows)
          playerGfx.fillRect(x + 5, y + 1, 6, 2)
          if (dir === 'left') {
            // Side hair on right side of sprite (back of head)
            playerGfx.fillRect(x + 9, y + 2, 2, 2)
          } else if (dir === 'right') {
            // Side hair on left side of sprite (back of head)
            playerGfx.fillRect(x + 5, y + 2, 2, 2)
          }
        }

        // --- Facial features (direction-specific) ---
        if (dir === 'down') {
          // Front face: two eyes
          playerGfx.fillStyle(eyeColor, 1)
          playerGfx.fillRect(x + 6, y + 3, 1, 1) // left eye
          playerGfx.fillRect(x + 9, y + 3, 1, 1) // right eye
          // Nose: 1px mid-tone shadow dot centered below eyes
          playerGfx.fillStyle(skinShadow, 1)
          playerGfx.fillRect(x + 8, y + 4, 1, 1)
        } else if (dir === 'left') {
          // Side profile facing left: eye on left side
          playerGfx.fillStyle(eyeColor, 1)
          playerGfx.fillRect(x + 6, y + 3, 1, 1)
          // Nose: 1px bump on left edge (outline protrusion technique)
          playerGfx.fillStyle(skin, 1)
          playerGfx.fillRect(x + 4, y + 4, 1, 1)
        } else if (dir === 'right') {
          // Side profile facing right: eye on right side
          playerGfx.fillStyle(eyeColor, 1)
          playerGfx.fillRect(x + 9, y + 3, 1, 1)
          // Nose: 1px bump on right edge
          playerGfx.fillStyle(skin, 1)
          playerGfx.fillRect(x + 11, y + 4, 1, 1)
        }
        // 'up' direction: no facial features (back of head)

        // --- Legs (overlap body by 1 row to hide width transition) ---
        // Walk frames: stepping leg extends 1px downward
        const leftExtra = col === 1 ? 1 : 0
        const rightExtra = col === 2 ? 1 : 0
        playerGfx.fillStyle(legColor, 1)
        playerGfx.fillRect(x + 4, y + 12, 3, 3 + leftExtra)   // left leg
        playerGfx.fillRect(x + 9, y + 12, 3, 3 + rightExtra)  // right leg
      }
    }

    playerGfx.generateTexture('player', FRAME_W * COLS, FRAME_H * ROWS)
    playerGfx.destroy()

    // Register individual frames so generateFrameNumbers() can find them.
    // generateTexture() only creates a single '__BASE' frame covering the whole
    // image — animation playback needs each cell registered by numeric index.
    const playerTex = this.textures.get('player')
    for (let row = 0; row < ROWS; row++) {
      for (let col = 0; col < COLS; col++) {
        playerTex.add(
          row * COLS + col, // numeric frame index (0-based, left→right, top→bottom)
          0,                // source image index (always 0 for a single canvas)
          col * FRAME_W,    // x
          row * FRAME_H,    // y
          FRAME_W,          // width
          FRAME_H,          // height
        )
      }
    }

    // NPC sprite (16×16, single frame)
    const npcGfx = this.make.graphics({ x: 0, y: 0 })
    npcGfx.fillStyle(0xe07b3a, 1)
    npcGfx.fillRect(4, 5, 8, 9)
    npcGfx.fillStyle(0xf4d0a1, 1)
    npcGfx.fillRect(5, 1, 6, 5)
    npcGfx.fillStyle(0x8b4513, 1)
    npcGfx.fillRect(4, 12, 3, 3)
    npcGfx.fillRect(9, 12, 3, 3)
    // Exclamation mark indicator
    npcGfx.fillStyle(0xffff00, 1)
    npcGfx.fillRect(7, -4, 2, 5)
    npcGfx.fillRect(7, 2, 2, 2)
    npcGfx.generateTexture('npc', 16, 16)
    npcGfx.destroy()

    // World tiles (32×32 each, 2 tile types side by side)
    const tileGfx = this.make.graphics({ x: 0, y: 0 })
    // Grass tile
    tileGfx.fillStyle(0x4a7c59, 1)
    tileGfx.fillRect(0, 0, 32, 32)
    tileGfx.fillStyle(0x3d6b4a, 1)
    tileGfx.fillRect(4, 8, 3, 3)
    tileGfx.fillRect(18, 20, 4, 4)
    tileGfx.fillRect(10, 25, 3, 2)
    // Wall/stone tile
    tileGfx.fillStyle(0x7a7a7a, 1)
    tileGfx.fillRect(32, 0, 32, 32)
    tileGfx.fillStyle(0x5a5a5a, 1)
    tileGfx.fillRect(34, 2, 12, 12)
    tileGfx.fillRect(48, 16, 12, 12)
    tileGfx.fillRect(34, 18, 10, 10)
    tileGfx.generateTexture('tiles', 64, 32)
    tileGfx.destroy()
  }
}
