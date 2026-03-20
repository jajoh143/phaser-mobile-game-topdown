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

    // If you add real assets later, load them here:
    // this.load.image('tileset', 'assets/tileset.png')
    // this.load.tilemapTiledJSON('map', 'assets/map.json')
    // this.load.atlas('player', 'assets/player.png', 'assets/player.json')
  }

  create() {
    this.scene.start('WeaponDemoScene')
  }
}
