import Phaser from 'phaser'

export class PreloadScene extends Phaser.Scene {
  constructor() {
    super({ key: 'PreloadScene' })
  }

  preload() {
    // Show a simple loading bar
    const { width, height } = this.cameras.main
    const bar    = this.add.graphics()
    const border = this.add.graphics()

    border.lineStyle(2, 0xffffff, 1)
    border.strokeRect(width / 2 - 120, height / 2 - 10, 240, 20)

    this.load.on('progress', (value: number) => {
      bar.clear()
      bar.fillStyle(0x4a9ade, 1)
      bar.fillRect(width / 2 - 118, height / 2 - 8, 236 * value, 16)
    })

    // Player sprite sheet — 3 cols (idle, walk-1, walk-2) × 4 rows (down, up, left, right)
    // Each frame is 16×16 px; Phaser numbers frames 0-11 in row-major order.
    this.load.spritesheet('player', 'assets/player.png', {
      frameWidth:  16,
      frameHeight: 16,
    })

    // NPC character sprite (16×16, single frame)
    this.load.image('npc', 'assets/npc.png')

    // World tile sheet — two 32×32 tiles side by side (grass at x=0, wall at x=32)
    this.load.image('tiles', 'assets/tiles.png')
  }

  create() {
    this.scene.start('WeaponDemoScene')
  }
}
