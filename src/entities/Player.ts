import Phaser from 'phaser'
import { PLAYER_SPEED, TILE_SIZE, SCALE } from '@/constants'

type Direction = 'down' | 'up' | 'left' | 'right'

export class Player extends Phaser.Physics.Arcade.Sprite {
  private facing: Direction = 'down'
  private isMoving = false

  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y, 'player')
    scene.add.existing(this)
    scene.physics.add.existing(this)

    this.setScale(SCALE)
    this.setDepth(5)

    const body = this.body as Phaser.Physics.Arcade.Body
    // Shrink physics body to ~feet area
    body.setSize(10, 8)
    body.setOffset(3, 8)

    this.setupAnimations()
  }

  private setupAnimations() {
    const anims = this.scene.anims

    const dirs: Direction[] = ['down', 'up', 'left', 'right']
    dirs.forEach((dir, row) => {
      const frameStart = row * 3

      if (!anims.exists(`player-idle-${dir}`)) {
        anims.create({
          key: `player-idle-${dir}`,
          frames: [{ key: 'player', frame: frameStart }],
          frameRate: 1,
        })
      }
      if (!anims.exists(`player-walk-${dir}`)) {
        // Classic RPG 4-frame walk cycle: step-left → neutral → step-right → neutral
        // Using the idle frame as the passing position prevents visual "popping"
        anims.create({
          key: `player-walk-${dir}`,
          frames: [
            { key: 'player', frame: frameStart + 1 },
            { key: 'player', frame: frameStart },
            { key: 'player', frame: frameStart + 2 },
            { key: 'player', frame: frameStart },
          ],
          frameRate: 8,
          repeat: -1,
        })
      }
    })

    this.play('player-idle-down')
  }

  move(vx: number, vy: number) {
    const body = this.body as Phaser.Physics.Arcade.Body
    const speed = PLAYER_SPEED

    if (vx === 0 && vy === 0) {
      body.setVelocity(0, 0)
      if (this.isMoving) {
        this.isMoving = false
        this.play(`player-idle-${this.facing}`, true)
      }
      return
    }

    body.setVelocity(vx * speed, vy * speed)
    this.isMoving = true

    // Determine facing direction (prefer horizontal if roughly equal)
    if (Math.abs(vx) >= Math.abs(vy)) {
      this.facing = vx > 0 ? 'right' : 'left'
    } else {
      this.facing = vy > 0 ? 'down' : 'up'
    }

    this.play(`player-walk-${this.facing}`, true)
  }

  halt() {
    this.move(0, 0)
  }

  getFacing(): Direction {
    return this.facing
  }

  getInteractPoint(): { x: number; y: number } {
    const offset = TILE_SIZE * SCALE * 0.6
    const offsets: Record<Direction, { x: number; y: number }> = {
      down:  { x: 0,      y: offset  },
      up:    { x: 0,      y: -offset },
      left:  { x: -offset, y: 0     },
      right: { x: offset,  y: 0     },
    }
    const d = offsets[this.facing]
    return { x: this.x + d.x, y: this.y + d.y }
  }
}
