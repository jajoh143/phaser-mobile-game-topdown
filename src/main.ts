import Phaser from 'phaser'
import { BootScene } from '@/scenes/BootScene'
import { PreloadScene } from '@/scenes/PreloadScene'
import { WorldScene } from '@/scenes/WorldScene'
import { UIScene } from '@/scenes/UIScene'
import { WeaponDemoScene } from '@/scenes/WeaponDemoScene'
import { BarScene } from '@/scenes/BarScene'
import { BattleScene } from '@/scenes/BattleScene'
import { GAME_WIDTH, GAME_HEIGHT } from '@/constants'

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: GAME_WIDTH,
  height: GAME_HEIGHT,
  backgroundColor: '#1a1a2e',
  parent: document.body,
  pixelArt: true,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { x: 0, y: 0 },
      debug: false,
    },
  },
  scene: [BootScene, PreloadScene, BarScene, BattleScene, WorldScene, UIScene, WeaponDemoScene],
}

new Phaser.Game(config)
