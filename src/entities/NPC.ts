import Phaser from 'phaser'
import { SCALE } from '@/constants'
import { DialogueLine } from '@/types'

export class NPC extends Phaser.Physics.Arcade.Sprite {
  readonly npcId: string
  readonly npcName: string
  readonly dialogue: DialogueLine[]

  private indicator!: Phaser.GameObjects.Text

  constructor(
    scene: Phaser.Scene,
    x: number,
    y: number,
    id: string,
    name: string,
    dialogue: DialogueLine[],
  ) {
    super(scene, x, y, 'npc')
    scene.add.existing(this)
    scene.physics.add.existing(this)

    this.npcId = id
    this.npcName = name
    this.dialogue = dialogue

    this.setScale(SCALE)
    this.setDepth(5)
    this.setImmovable(true)

    const body = this.body as Phaser.Physics.Arcade.Body
    body.setSize(10, 8)
    body.setOffset(3, 8)

    // Floating "!" indicator
    this.indicator = scene.add
      .text(x, y - 28, '!', {
        fontSize: '14px',
        color: '#ffff00',
        stroke: '#000000',
        strokeThickness: 3,
      })
      .setOrigin(0.5)
      .setDepth(10)

    scene.tweens.add({
      targets: this.indicator,
      y: y - 34,
      duration: 600,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut',
    })
  }

  showIndicator(visible: boolean) {
    this.indicator.setVisible(visible)
  }

  destroy(fromScene?: boolean) {
    this.indicator.destroy()
    super.destroy(fromScene)
  }
}
