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

    const colors = {
      down: 0x4a9ade,
      up: 0x3a7abf,
      left: 0x2a5a9f,
      right: 0x5ab0ee,
    }

    const rowColors = [colors.down, colors.up, colors.left, colors.right]

    for (let row = 0; row < ROWS; row++) {
      const color = rowColors[row]
      for (let col = 0; col < COLS; col++) {
        const x = col * FRAME_W
        const y = row * FRAME_H
        // Body
        playerGfx.fillStyle(color, 1)
        playerGfx.fillRect(x + 4, y + 5, 8, 9)
        // Head
        playerGfx.fillStyle(0xf4c2a1, 1)
        playerGfx.fillRect(x + 5, y + 1, 6, 5)
        // Legs animation offset
        const legOff = col === 1 ? -1 : col === 2 ? 1 : 0
        playerGfx.fillStyle(0x2d5a8e, 1)
        playerGfx.fillRect(x + 4, y + 12, 3, 3 + legOff)
        playerGfx.fillRect(x + 9, y + 12, 3, 3 - legOff)
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
