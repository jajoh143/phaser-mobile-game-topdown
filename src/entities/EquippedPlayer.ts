/**
 * EquippedPlayer — physics sprite + runtime weapon overlay.
 *
 * Architecture:
 *   - `body`   : Phaser Arcade physics sprite for the character (scale 2 → 64×64 px)
 *   - `weapon` : Phaser Sprite overlay positioned each frame via hand-anchor data
 *
 * The weapon is repositioned every frame using hand_anchors.json:
 *   weapon.x = body.x + (anchor.x - FRAME_HALF) * CHAR_SCALE
 *   weapon.y = body.y + (anchor.y - FRAME_HALF) * CHAR_SCALE
 *
 * Melee  weapons (sword/axe/etc) → `attack()` plays the slash animation.
 * Ranged weapons (gun/bow/staff)  → `attack()` plays interact briefly, fires
 *   `onFire` callback so the scene can spawn the projectile.
 */

import Phaser from 'phaser'
import { Inventory } from '@/systems/Inventory'

const FRAME_W        = 32
const FRAMES_PER_DIR = 4
const CHAR_SCALE     = 2   // body sprite → 64×64 on screen
const FRAME_HALF     = FRAME_W / 2

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

// Weapons that fire projectiles instead of melee-slashing
const RANGED_WEAPONS = new Set([
  'pistol', 'shotgun', 'rifle', 'bow',
])
// Weapons that cast spells / area effects
const SPELL_WEAPONS = new Set([
  'staff',
])
// Thrown weapons
const THROWN_WEAPONS = new Set([
  'molotov',
])

export type AttackType = 'melee' | 'ranged' | 'spell' | 'thrown'

export interface FireEvent {
  x: number           // world-space muzzle position
  y: number
  dirX: number        // unit direction vector
  dirY: number
  weapon: string
  type: AttackType
}

export class EquippedPlayer {
  /** Physics-enabled character sprite. */
  readonly body: Phaser.Physics.Arcade.Sprite

  /** Weapon overlay sprite. Always rendered on top of the character. */
  readonly weapon: Phaser.GameObjects.Sprite

  readonly inventory: Inventory

  private scene:        Phaser.Scene
  private anchors:      AnchorData | null = null
  private currentAnim:  AnimName   = 'walk'
  private currentDir:   DirName    = 'down'
  private isAttacking:  boolean    = false

  /** Called when a ranged/spell/thrown weapon fires. */
  onFire: ((e: FireEvent) => void) | null = null

  constructor(scene: Phaser.Scene, x: number, y: number, presetKey: string) {
    this.scene     = scene
    this.inventory = new Inventory()

    this.body = scene.physics.add.sprite(x, y, presetKey)
    this.body.setScale(CHAR_SCALE)
    this.body.setCollideWorldBounds(true)

    // Weapon uses Sprite (not Image) so setFrame() is reliable on spritesheets
    this.weapon = scene.add.sprite(x, y, '__missing__')
    this.weapon.setScale(1)
    this.weapon.setVisible(false)
  }

  setAnchors(data: AnchorData): void {
    this.anchors = data
  }

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
            frameRate: anim === 'slash' || anim === 'interact' ? 10 : 7,
            repeat:    anim === 'slash' || anim === 'interact' ? 0  : -1,
          })
        }
      })
    })
  }

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
    this._updateWeaponOverlay()
  }

  /** Perform an attack appropriate for the active weapon. */
  attack(): void {
    if (this.isAttacking) return
    const w = this.inventory.active
    if (!w) return

    const type = this._attackType(w)
    if (type === 'melee') {
      this._doSlash()
    } else {
      this._doRanged(w, type)
    }
  }

  /** Call every frame with current velocity. */
  update(vx: number, vy: number): void {
    if (!this.isAttacking) {
      this._updateDirection(vx, vy)
      this._updateMovementAnim(vx, vy)
    }
    this._updateWeaponOverlay()
  }

  // ── public helpers ─────────────────────────────────────────────────────────

  getAttackType(): AttackType | null {
    const w = this.inventory.active
    return w ? this._attackType(w) : null
  }

  // ── private ───────────────────────────────────────────────────────────────

  private _attackType(w: string): AttackType {
    if (RANGED_WEAPONS.has(w)) return 'ranged'
    if (SPELL_WEAPONS.has(w))  return 'spell'
    if (THROWN_WEAPONS.has(w)) return 'thrown'
    return 'melee'
  }

  private _dirVector(): { x: number; y: number } {
    const map: Record<DirName, { x: number; y: number }> = {
      down:  { x:  0, y:  1 },
      up:    { x:  0, y: -1 },
      left:  { x: -1, y:  0 },
      right: { x:  1, y:  0 },
    }
    return map[this.currentDir]
  }

  private _doSlash(): void {
    this.isAttacking = true
    this.currentAnim = 'slash'
    const key = `${this.body.texture.key}_slash_${this.currentDir}`
    this.body.play(key)
    this.body.once(Phaser.Animations.Events.ANIMATION_COMPLETE, () => {
      this.isAttacking = false
      this.currentAnim = 'walk'
      this._resumeMovementAnim()
    })
  }

  private _doRanged(weapon: string, type: AttackType): void {
    this.isAttacking = true
    this.currentAnim = 'interact'

    // Fire callback at frame 1 (arm extended) via a short delay
    this.scene.time.delayedCall(80, () => {
      if (this.onFire) {
        const dir = this._dirVector()
        // Muzzle position = weapon sprite's world position
        this.onFire({
          x:      this.weapon.visible ? this.weapon.x : this.body.x,
          y:      this.weapon.visible ? this.weapon.y : this.body.y,
          dirX:   dir.x,
          dirY:   dir.y,
          weapon,
          type,
        })
      }
    })

    const key = `${this.body.texture.key}_interact_${this.currentDir}`
    this.body.play(key)
    this.body.once(Phaser.Animations.Events.ANIMATION_COMPLETE, () => {
      this.isAttacking = false
      this.currentAnim = 'walk'
      this._resumeMovementAnim()
    })
  }

  private _updateDirection(vx: number, vy: number): void {
    if (Math.abs(vx) > Math.abs(vy)) {
      this.currentDir = vx < 0 ? 'left' : 'right'
    } else if (vy !== 0) {
      this.currentDir = vy < 0 ? 'up' : 'down'
    }
  }

  private _updateMovementAnim(vx: number, vy: number): void {
    const isMoving = vx !== 0 || vy !== 0
    const key      = `${this.body.texture.key}_walk_${this.currentDir}`
    if (isMoving) {
      if (this.body.anims.currentAnim?.key !== key) {
        this.body.play(key)
        this.currentAnim = 'walk'
      }
    } else {
      this.body.anims.stop()
      this.currentAnim = 'walk'
      const animIdx  = 0  // walk row
      const dirIdx   = DIRECTIONS.indexOf(this.currentDir)
      const row      = animIdx * DIRECTIONS.length + dirIdx
      this.body.setFrame(row * FRAMES_PER_DIR)
    }
  }

  private _resumeMovementAnim(): void {
    const key = `${this.body.texture.key}_walk_${this.currentDir}`
    this.body.play(key)
    this.currentAnim = 'walk'
  }

  private _updateWeaponOverlay(): void {
    if (!this.anchors || this.inventory.active === null) {
      this.weapon.setVisible(false)
      return
    }

    const animFrames = this.anchors[this.currentAnim]?.[this.currentDir]
    if (!animFrames) return

    // currentFrame.index is 1-based in Phaser 3, so subtract 1 for 0-based
    const rawIdx   = this.body.anims.currentFrame?.index ?? 1
    const frameIdx = (rawIdx - 1) % FRAMES_PER_DIR
    const anchor   = animFrames[frameIdx] ?? animFrames[0]

    // Convert 32×32 pixel-space coords to screen space
    const ox = (anchor.x - FRAME_HALF) * CHAR_SCALE
    const oy = (anchor.y - FRAME_HALF) * CHAR_SCALE
    this.weapon.setPosition(this.body.x + ox, this.body.y + oy)
    this.weapon.setAngle(anchor.angle)
    this.weapon.setFrame(ORIENT_TO_FRAME[anchor.orient] ?? 0)
    this.weapon.setVisible(true)
  }
}
