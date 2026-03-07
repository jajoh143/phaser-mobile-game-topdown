import Phaser from 'phaser'
import { JOYSTICK_RADIUS, JOYSTICK_THUMB_RADIUS } from '@/constants'

export class VirtualJoystick {
  private scene: Phaser.Scene
  private base!: Phaser.GameObjects.Arc
  private thumb!: Phaser.GameObjects.Arc
  private pointer: Phaser.Input.Pointer | null = null
  private originX = 0
  private originY = 0

  dx = 0
  dy = 0

  constructor(scene: Phaser.Scene, enabled: boolean) {
    this.scene = scene
    if (enabled) {
      this.build()
      this.setupInput()
    }
  }

  private build() {
    const { width, height } = this.scene.cameras.main
    const x = 80
    const y = height - 100

    this.base = this.scene.add
      .circle(x, y, JOYSTICK_RADIUS, 0xffffff, 0.15)
      .setDepth(50)
      .setScrollFactor(0)
      .setStrokeStyle(2, 0xffffff, 0.4)

    this.thumb = this.scene.add
      .circle(x, y, JOYSTICK_THUMB_RADIUS, 0xffffff, 0.4)
      .setDepth(51)
      .setScrollFactor(0)

    // Keep base at fixed screen coords — attach to camera
    void width // suppress unused warning
  }

  private setupInput() {
    this.scene.input.on('pointerdown', (p: Phaser.Input.Pointer) => {
      // Only claim pointer if it's in the left half of screen
      if (p.x < this.scene.cameras.main.width / 2 && !this.pointer) {
        this.pointer = p
        this.originX = p.x
        this.originY = p.y
        this.base.setPosition(p.x, p.y)
        this.thumb.setPosition(p.x, p.y)
      }
    })

    this.scene.input.on('pointermove', (p: Phaser.Input.Pointer) => {
      if (this.pointer?.id !== p.id) return
      const dx = p.x - this.originX
      const dy = p.y - this.originY
      const dist = Math.sqrt(dx * dx + dy * dy)
      const clamp = Math.min(dist, JOYSTICK_RADIUS)
      const angle = Math.atan2(dy, dx)

      const tx = this.originX + Math.cos(angle) * clamp
      const ty = this.originY + Math.sin(angle) * clamp
      this.thumb.setPosition(tx, ty)

      this.dx = dist > 8 ? Math.cos(angle) : 0
      this.dy = dist > 8 ? Math.sin(angle) : 0
    })

    const release = (p: Phaser.Input.Pointer) => {
      if (this.pointer?.id !== p.id) return
      this.pointer = null
      this.dx = 0
      this.dy = 0
      const { width, height } = this.scene.cameras.main
      void width
      this.base.setPosition(80, height - 100)
      this.thumb.setPosition(80, height - 100)
    }

    this.scene.input.on('pointerup', release)
    this.scene.input.on('pointerupoutside', release)
  }
}
