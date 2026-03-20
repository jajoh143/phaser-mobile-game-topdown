import Phaser from 'phaser'

export class PreloadScene extends Phaser.Scene {
  constructor() {
    super({ key: 'PreloadScene' })
  }

  preload() {
    // Show a simple loading bar
    const { width, height } = this.cameras.main
    const bar = this.add.graphics()
    const border = this.add.graphics()

    border.lineStyle(2, 0xffffff, 1)
    border.strokeRect(width / 2 - 120, height / 2 - 10, 240, 20)

    this.load.on('progress', (value: number) => {
      bar.clear()
      bar.fillStyle(0x4a9ade, 1)
      bar.fillRect(width / 2 - 118, height / 2 - 8, 236 * value, 16)
    })

    // ── Bar scene tiles ───────────────────────────────────────────────────
    this.load.image('brick_wall',  'assets/sprites/brick_wall.png')
    this.load.image('wood_floor',  'assets/sprites/wood_floor.png')
    this.load.image('wooden_bar',  'assets/sprites/wooden_bar.png')
    this.load.image('dance_floor', 'assets/sprites/dance_floor.png')

    // ── Bar scene props / decorations ────────────────────────────────────
    this.load.image('led_sign',    'assets/sprites/led_sign.png')
    this.load.image('tom_poster',  'assets/sprites/tom_poster.png')

    // ── Bar scene props ───────────────────────────────────────────────────
    // alcohol_bottles.png: 128×32 sheet, 4 frames (whiskey/wine/gin/beer)
    this.load.spritesheet('alcohol_bottles', 'assets/sprites/alcohol_bottles.png', {
      frameWidth: 32, frameHeight: 32,
    })

    // ── Character & weapon ────────────────────────────────────────────────
    // char_0.png: 128×640 sheet, 32×32 frames (5 animations × 4 directions × 4 frames)
    this.load.spritesheet('char_0', 'assets/sprites/char_0.png', {
      frameWidth: 32, frameHeight: 32,
    })

    // demon_bartender.png: same layout as char_0.png
    this.load.spritesheet('demon_bartender', 'assets/sprites/demon_bartender.png', {
      frameWidth: 32, frameHeight: 32,
    })

    // weapon_bat.png: 128×32 sheet, 4 frames (E/S/W/N orientations)
    this.load.spritesheet('weapon_bat', 'assets/sprites/weapon_bat.png', {
      frameWidth: 32, frameHeight: 32,
    })

    // hand_anchors.json: per-animation, per-direction, per-frame weapon grip data
    this.load.json('hand_anchors', 'assets/sprites/hand_anchors.json')
  }

  create() {
    this.scene.start('BarScene')
  }
}
