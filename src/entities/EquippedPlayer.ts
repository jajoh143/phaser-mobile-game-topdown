/**
 * EquippedPlayer — physics sprite + runtime weapon overlay.
 *
 * Architecture (Option B — runtime overlay):
 *   - `body`   : Phaser Arcade physics sprite for the character (scale 2 → 64×64 on screen)
 *   - `weapon` : plain Image sprite rendered on top each frame  (scale 1 → 32×32 on screen)
 *
 * The weapon is repositioned every frame using hand-anchor JSON exported by
 * tools/sprite-generator/export_for_game.py. No baked equipped spritesheets needed.
 *
 * Anchor formula (pixel space → screen space):
 *   weapon.x = body.x + (anchor.x - FRAME_HALF) * CHAR_SCALE
 *   weapon.y = body.y + (anchor.y - FRAME_HALF) * CHAR_SCALE
 *
 * where FRAME_HALF = 16 (half of the 32×32 frame), CHAR_SCALE = 2.
 */

import Phaser from 'phaser'
import { Inventory } from '@/systems/Inventory'

// Must match FRAME_W / FRAME_H in the Python generators
const FRAME_W     = 32
const FRAME_H     = 32
const FRAMES_PER_DIR = 4

const CHAR_SCALE  = 2   // body sprite scale → 64×64 on screen
const WEAPON_SCALE = 1  // weapon sprite scale → 32×32 on screen (= 50% of 64)
const FRAME_HALF  = FRAME_W / 2

const ANIMATIONS  = ['walk', 'jump', 'crouch', 'interact', 'slash'] as const
const DIRECTIONS  = ['down', 'left', 'right', 'up'] as const

type AnimName = typeof ANIMATIONS[number]
type DirName  = typeof DIRECTIONS[number]

export interface AnchorFrame {
  x: number
  y: number
  angle: number
  orient: string
}

export type AnchorData = Record<AnimName, Record<DirName, AnchorFrame[]>>

const ORIENT_TO_FRAME: Record<string, number> = {
  east:  0,
  south: 1,
  west:  2,
  north: 3,
}

const MOVE_SPEED = 160

export class EquippedPlayer {
  /** The physics-enabled character sprite. Add this to the physics group. */
  readonly body: Phaser.Physics.Arcade.Sprite

  /** The weapon overlay sprite. Add this to a display group above the character. */
  readonly weapon: Phaser.GameObjects.Image

  readonly inventory: Inventory

  private scene:       Phaser.Scene
  private anchors:     AnchorData | null = null
  private currentAnim: AnimName   = 'walk'
  private currentDir:  DirName    = 'down'
  private frameIdx:    number     = 0
  private isSlashing:  boolean    = false
  private slashTimer:  Phaser.Time.TimerEvent | null = null

  constructor(scene: Phaser.Scene, x: number, y: number, presetKey: string) {
    this.scene     = scene
    this.inventory = new Inventory()

    // ── Character sprite ───────────────────────────────────────────────────
    this.body = scene.physics.add.sprite(x, y, presetKey)
    this.body.setScale(CHAR_SCALE)
    this.body.setCollideWorldBounds(true)

    // ── Weapon overlay ─────────────────────────────────────────────────────
    this.weapon = scene.add.image(x, y, '__missing__')
    this.weapon.setScale(WEAPON_SCALE)
    this.weapon.setVisible(false)
  }

  /** Call after loading hand_anchors.json. */
  setAnchors(data: AnchorData): void {
    this.anchors = data
  }

  /** Register Phaser animations from the character spritesheet. */
  createAnimations(presetKey: string): void {
    const anims = this.scene.anims

    ANIMATIONS.forEach((anim, animIdx) => {
      DIRECTIONS.forEach((dir, dirIdx) => {
        const row   = animIdx * DIRECTIONS.length + dirIdx
        const key   = `${presetKey}_${anim}_${dir}`
        const start = row * FRAMES_PER_DIR
        const end   = start + FRAMES_PER_DIR - 1

        if (!anims.exists(key)) {
          anims.create({
            key,
            frames:    anims.generateFrameNumbers(presetKey, { start, end }),
            frameRate: anim === 'slash' ? 10 : 7,
            repeat:    anim === 'slash' ? 0  : -1,
          })
        }
      })
    })
  }

  /** Switch to a different weapon by name (must already be in inventory). */
  equipWeapon(weaponName: string | null): void {
    if (!weaponName) {
      this.weapon.setVisible(false)
      return
    }
    const key = `weapon_${weaponName}`
    if (!this.scene.textures.exists(key)) {
      this.weapon.setVisible(false)
      return
    }
    this.weapon.setTexture(key)
    this.weapon.setVisible(true)
    this._updateWeaponFrame()
  }

  /** Trigger a slash animation. Reverts to carry pose when done. */
  slash(): void {
    if (this.isSlashing) return
    if (this.inventory.active === null) return

    this.isSlashing = true
    const key = `${this.body.texture.key}_slash_${this.currentDir}`
    this.body.play(key)
    this.body.once(Phaser.Animations.Events.ANIMATION_COMPLETE, () => {
      this.isSlashing = false
      this._resumeMovementAnim()
    })
  }

  /**
   * Call every frame from the scene's update() with the current velocity
   * or movement state. Pass null velocity to play idle (frame 0).
   */
  update(vx: number, vy: number): void {
    if (!this.isSlashing) {
      this._updateDirection(vx, vy)
      this._updateMovementAnim(vx, vy)
    }
    this._updateWeaponFrame()
  }

  // ── private helpers ───────────────────────────────────────────────────────

  private _updateDirection(vx: number, vy: number): void {
    if (Math.abs(vx) > Math.abs(vy)) {
      this.currentDir = vx < 0 ? 'left' : 'right'
    } else if (vy !== 0) {
      this.currentDir = vy < 0 ? 'up' : 'down'
    }
  }

  private _updateMovementAnim(vx: number, vy: number): void {
    const isMoving = vx !== 0 || vy !== 0
    const key = `${this.body.texture.key}_walk_${this.currentDir}`

    if (isMoving) {
      if (this.body.anims.currentAnim?.key !== key) {
        this.body.play(key)
      }
    } else {
      // Idle — stop on frame 0 of the current direction's walk row
      this.body.anims.stop()
      const animIdx  = 0 // walk
      const dirIdx   = DIRECTIONS.indexOf(this.currentDir)
      const row      = animIdx * DIRECTIONS.length + dirIdx
      const frameNum = row * FRAMES_PER_DIR
      this.body.setFrame(frameNum)
    }
  }

  private _resumeMovementAnim(): void {
    const key = `${this.body.texture.key}_walk_${this.currentDir}`
    this.body.play(key)
  }

  private _updateWeaponFrame(): void {
    if (!this.anchors || this.inventory.active === null) {
      this.weapon.setVisible(false)
      return
    }

    const animFrames = this.anchors[this.currentAnim]?.[this.currentDir]
    if (!animFrames) return

    // Determine current frame index from the sprite's playing animation
    const currentFrame = this.body.anims.currentFrame
    const frameIdx     = currentFrame ? currentFrame.index % FRAMES_PER_DIR : 0
    const anchor       = animFrames[frameIdx] ?? animFrames[0]

    // Position weapon in screen space
    const ox = (anchor.x - FRAME_HALF) * CHAR_SCALE
    const oy = (anchor.y - FRAME_HALF) * CHAR_SCALE
    this.weapon.setPosition(this.body.x + ox, this.body.y + oy)
    this.weapon.setAngle(anchor.angle)

    // Select correct orientation frame from the weapon spritesheet
    const orientFrame = ORIENT_TO_FRAME[anchor.orient] ?? 0
    this.weapon.setFrame(orientFrame)
    this.weapon.setVisible(true)
  }
}
