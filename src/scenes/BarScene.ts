import Phaser from 'phaser'
import { TILE_SIZE, GAME_WIDTH, GAME_HEIGHT, PLAYER_SPEED } from '../constants'
import { VirtualJoystick } from '../systems/VirtualJoystick'
import { isMobile } from '../utils/device'

// ─── Map constants ────────────────────────────────────────────────────────────
const TILE   = TILE_SIZE        // 32 px
const MAP_W  = 11
const MAP_H  = 20
const ROOM_W = MAP_W * TILE     // 352 px
const ROOM_H = MAP_H * TILE     // 640 px
const ROOM_X = Math.floor((GAME_WIDTH - ROOM_W) / 2)  // centred in canvas

// Camera zoom — 2× makes each 32 px tile render as 64 px on screen
const CAM_ZOOM = 2

// 0 = wood floor  |  1 = brick wall  |  2 = bar counter
//
// Row 1 is the bartender's zone (open floor behind the bar).
// Row 2 holds the bar counter, moved forward so there's space behind it.
// Player area starts at row 3.
const MAP: number[][] = [
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  // row  0 — north wall
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  1 — behind-bar floor (bartender zone)
  [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  // row  2 — bar counter
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  3 — floor (bar front face hangs here)
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  4
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  5
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  6
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  7
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  8  ← bat pickup
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  9
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 10
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 11
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 12 ← player start
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 13
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 14
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 15
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 16
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 17
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 18
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  // row 19 — south wall
]

// ─── Bottle placement [tile-col, spritesheet-frame] ───────────────────────────
// Bottles sit on the bar counter surface at row 2
const BOTTLE_DEFS: [number, number][] = [
  [2, 0],  // whiskey
  [4, 3],  // beer
  [6, 1],  // wine
  [8, 2],  // gin
]
const BOTTLE_ROW = 2  // bar counter row

// ─── Spawn positions [tile-col, tile-row] ─────────────────────────────────────
const BAT_TILE:        [number, number] = [5, 8]   // moved one row down with bar shift
const PLAYER_TILE:     [number, number] = [5, 12]
const BARTENDER_TILE:  [number, number] = [5, 1]   // center of behind-bar row

// ─── Spritesheet frame layout (128×640, 32×32 frames) ─────────────────────────
// ANIMATIONS = [walk, jump, crouch, interact, slash] × DIRECTIONS = [down, left, right, up]
//  walk  rows  0-3  → frames   0-15
//  slash rows 16-19 → frames  64-79

// ─── Anchor-based weapon placement ────────────────────────────────────────────
// hand_anchors.json: { anim: { direction: [{x,y,angle,orient}, ...] } }
// x, y = pixel position within the 32×32 frame (from top-left).
// The bat sprite's GRIP END is set as the Phaser origin so setPosition() lands
// the grip exactly on the hand anchor and setAngle() swings around that pivot.

type AnchorFrame = { x: number; y: number; angle: number; orient: string }
type AnchorData  = Record<string, Record<string, AnchorFrame[]>>

// weapon_bat.png frame per orient
const ORIENT_FRAME: Record<string, number> = { east: 0, south: 1, west: 2, north: 3 }

// Bat sprite grip-end in normalised (0-1) origin space.
// East frame (bat→right): barrel at x≈29, grip center at x≈9, y≈15
//   → origin_x = 9/32 ≈ 0.28, origin_y = 15/32 ≈ 0.47
// West is mirrored, South/North rotate the same offset 90°.
const ORIENT_ORIGIN: Record<string, { ox: number; oy: number }> = {
  east:  { ox: 0.28, oy: 0.47 },
  west:  { ox: 0.72, oy: 0.47 },
  south: { ox: 0.47, oy: 0.28 },
  north: { ox: 0.47, oy: 0.72 },
}

// Bat scale — weapon_bat frames are 32×32 (full tile). Scale down to hand-held.
const BAT_HELD_SCALE = 0.55

// ─── Scene ────────────────────────────────────────────────────────────────────
export class BarScene extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite
  private walls!: Phaser.Physics.Arcade.StaticGroup
  private barBodies!: Phaser.Physics.Arcade.StaticGroup

  private batPickup!: Phaser.Physics.Arcade.Sprite
  private batGlow!: Phaser.GameObjects.Arc
  private batAlive = true

  private heldBat: Phaser.GameObjects.Sprite | null = null
  private hasBat      = false
  private attacking   = false
  private handAnchors: AnchorData | null = null

  private facing = 'down'

  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys
  private wasd!: Record<string, Phaser.Input.Keyboard.Key>
  private keyE!:     Phaser.Input.Keyboard.Key
  private keySpace!: Phaser.Input.Keyboard.Key

  private joystick!: VirtualJoystick
  private hintText!: Phaser.GameObjects.Text
  private controlsText!: Phaser.GameObjects.Text
  private swingBtn: Phaser.GameObjects.Text | null = null

  constructor() {
    super({ key: 'BarScene' })
  }

  // ── create ────────────────────────────────────────────────────────────────
  create() {
    this.handAnchors = this.cache.json.get('hand_anchors') as AnchorData
    this.createAnimations()
    this.buildMap()
    this.spawnPlayer()
    this.spawnBartender()
    this.spawnBatPickup()
    this.setupCollisions()
    this.setupInput()
    this.setupCamera()
    this.setupHUD()
  }

  // ── Animations ────────────────────────────────────────────────────────────
  private createAnimations() {
    // Both char_0 and demon_bartender use the same 128×640 frame layout
    for (const [prefix, key] of [['bar', 'char_0'], ['demon', 'demon_bartender']] as [string, string][]) {
      const defs: Array<{ suffix: string; start: number; end: number; rate: number; repeat: number }> = [
        // Walk (looping)
        { suffix: 'walk-down',    start:  0, end:  3, rate: 8,  repeat: -1 },
        { suffix: 'walk-left',    start:  4, end:  7, rate: 8,  repeat: -1 },
        { suffix: 'walk-right',   start:  8, end: 11, rate: 8,  repeat: -1 },
        { suffix: 'walk-up',      start: 12, end: 15, rate: 8,  repeat: -1 },
        // Slash (one-shot, player only but registered for both for simplicity)
        { suffix: 'slash-down',   start: 64, end: 67, rate: 10, repeat: 0 },
        { suffix: 'slash-left',   start: 68, end: 71, rate: 10, repeat: 0 },
        { suffix: 'slash-right',  start: 72, end: 75, rate: 10, repeat: 0 },
        { suffix: 'slash-up',     start: 76, end: 79, rate: 10, repeat: 0 },
      ]
      for (const a of defs) {
        const animKey = `${prefix}-${a.suffix}`
        if (!this.anims.exists(animKey)) {
          this.anims.create({
            key: animKey,
            frames: this.anims.generateFrameNumbers(key, { start: a.start, end: a.end }),
            frameRate: a.rate,
            repeat: a.repeat,
          })
        }
      }

      // Idle — single frame per direction
      const idles = [
        { suffix: 'idle-down',  frame:  0 },
        { suffix: 'idle-left',  frame:  4 },
        { suffix: 'idle-right', frame:  8 },
        { suffix: 'idle-up',    frame: 12 },
      ]
      for (const a of idles) {
        const animKey = `${prefix}-${a.suffix}`
        if (!this.anims.exists(animKey)) {
          this.anims.create({
            key: animKey,
            frames: [{ key, frame: a.frame }],
            frameRate: 1,
          })
        }
      }
    }
  }

  // ── Map / environment ─────────────────────────────────────────────────────
  private buildMap() {
    this.walls     = this.physics.add.staticGroup()
    this.barBodies = this.physics.add.staticGroup()

    for (let row = 0; row < MAP_H; row++) {
      for (let col = 0; col < MAP_W; col++) {
        const wx   = ROOM_X + col * TILE
        const wy   = row * TILE
        const cell = MAP[row][col]

        // Wood floor underneath everything (depth 0)
        this.add.image(wx, wy, 'wood_floor').setOrigin(0, 0).setDepth(0)

        if (cell === 1) {
          this.add.image(wx, wy, 'brick_wall').setOrigin(0, 0).setDepth(1)
          const body = this.walls.create(
            wx + TILE / 2, wy + TILE / 2, 'brick_wall',
          ) as Phaser.Physics.Arcade.Sprite
          body.setVisible(false)
          body.refreshBody()

        } else if (cell === 2) {
          // wooden_bar.png is 32×64 — top half is the bar surface,
          // bottom half is the front face visible from the player's side.
          this.add.image(wx, wy, 'wooden_bar').setOrigin(0, 0).setDepth(2)
          const body = this.barBodies.create(
            wx + TILE / 2, wy + TILE / 2, 'wooden_bar',
          ) as Phaser.Physics.Arcade.Sprite
          body.setVisible(false)
          ;(body.body as Phaser.Physics.Arcade.StaticBody).setSize(TILE, TILE)
          body.refreshBody()
        }
      }
    }

    // Bottles on the bar counter surface
    for (const [col, frame] of BOTTLE_DEFS) {
      const bx = ROOM_X + col * TILE + TILE / 2
      const by = BOTTLE_ROW * TILE + TILE / 2
      this.add.sprite(bx, by, 'alcohol_bottles', frame).setDepth(3)
    }
  }

  // ── Bartender NPC ─────────────────────────────────────────────────────────
  private spawnBartender() {
    const bx = ROOM_X + BARTENDER_TILE[0] * TILE + TILE / 2
    const by = BARTENDER_TILE[1] * TILE + TILE / 2
    const bartender = this.add.sprite(bx, by, 'demon_bartender', 0)
    bartender.setDepth(10 + by / ROOM_H)
    bartender.play('demon-idle-down')

    // Subtle idle sway — bartender slowly turns left/right
    this.time.addEvent({
      delay: 3500,
      loop: true,
      callback: () => {
        const anims = ['demon-idle-down', 'demon-idle-left', 'demon-idle-down', 'demon-idle-right']
        const pick = anims[Math.floor(Math.random() * anims.length)]
        bartender.play(pick)
      },
    })
  }

  // ── Player ────────────────────────────────────────────────────────────────
  private spawnPlayer() {
    const px = ROOM_X + PLAYER_TILE[0] * TILE + TILE / 2
    const py = PLAYER_TILE[1] * TILE + TILE / 2
    this.player = this.physics.add.sprite(px, py, 'char_0', 0)
    this.player.body!.setSize(20, 10)
    this.player.body!.setOffset(6, 22)
    this.player.play('bar-idle-down')

    // Return to idle when slash animation completes
    this.player.on(Phaser.Animations.Events.ANIMATION_COMPLETE, (anim: Phaser.Animations.Animation) => {
      if (anim.key.startsWith('bar-slash-')) {
        this.attacking = false
        this.player.play(`bar-idle-${this.facing}`)
      }
    })
  }

  // ── Bat pickup ────────────────────────────────────────────────────────────
  private spawnBatPickup() {
    const bx = ROOM_X + BAT_TILE[0] * TILE + TILE / 2
    const by = BAT_TILE[1] * TILE + TILE / 2

    // Glow halo
    this.batGlow = this.add.circle(bx, by, 18, 0xffdd44, 0.3).setDepth(4)
    this.tweens.add({
      targets: this.batGlow,
      alpha: 0.6, duration: 900, yoyo: true, repeat: -1, ease: 'Sine.easeInOut',
    })

    // Bat sprite at reduced scale — frame 1 = south/down
    this.batPickup = this.physics.add.sprite(bx, by, 'weapon_bat', 1)
    this.batPickup.setDepth(5).setScale(BAT_HELD_SCALE)
    ;(this.batPickup.body as Phaser.Physics.Arcade.Body).setImmovable(true)
    ;(this.batPickup.body as Phaser.Physics.Arcade.Body).allowGravity = false

    this.tweens.add({
      targets: this.batPickup,
      y: by - 4, duration: 900, yoyo: true, repeat: -1, ease: 'Sine.easeInOut',
    })
  }

  // ── Physics ───────────────────────────────────────────────────────────────
  private setupCollisions() {
    this.physics.add.collider(this.player, this.walls)
    this.physics.add.collider(this.player, this.barBodies)
  }

  // ── Input ─────────────────────────────────────────────────────────────────
  private setupInput() {
    this.cursors = this.input.keyboard!.createCursorKeys()
    this.wasd = {
      up:    this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      down:  this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      left:  this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      right: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.D),
    }
    this.keyE     = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.E)
    this.keySpace = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE)

    if (isMobile()) {
      this.joystick = new VirtualJoystick(this, true)

      this.add.text(GAME_WIDTH - 72, GAME_HEIGHT - 80, 'PICK\nUP', {
        fontSize: '13px', color: '#ffffff',
        backgroundColor: '#44444488',
        padding: { x: 12, y: 8 }, align: 'center',
      })
        .setScrollFactor(0).setDepth(100).setInteractive()
        .on('pointerdown', () => this.tryPickup())

      this.swingBtn = this.add.text(GAME_WIDTH - 72, GAME_HEIGHT - 148, 'SWING', {
        fontSize: '13px', color: '#ffe566',
        backgroundColor: '#66330088',
        padding: { x: 12, y: 8 }, align: 'center',
      })
        .setScrollFactor(0).setDepth(100).setInteractive()
        .setVisible(false)
        .on('pointerdown', () => this.startAttack())
    }
  }

  // ── HUD ───────────────────────────────────────────────────────────────────
  private setupHUD() {
    this.hintText = this.add
      .text(GAME_WIDTH / 2, GAME_HEIGHT - 44, '', {
        fontSize: '12px', color: '#ffe566',
        backgroundColor: '#00000099',
        padding: { x: 10, y: 5 }, align: 'center',
      })
      .setOrigin(0.5).setScrollFactor(0).setDepth(100).setVisible(false)

    this.controlsText = this.add
      .text(8, 8, 'WASD — move    E — pick up', {
        fontSize: '10px', color: '#aaaaaa',
        backgroundColor: '#00000066',
        padding: { x: 6, y: 4 },
      })
      .setScrollFactor(0).setDepth(100)
  }

  // ── Camera ────────────────────────────────────────────────────────────────
  private setupCamera() {
    this.cameras.main.setBounds(ROOM_X, 0, ROOM_W, ROOM_H)
    this.cameras.main.startFollow(this.player, true, 0.1, 0.1)
    this.cameras.main.setZoom(CAM_ZOOM)
    this.cameras.main.setBackgroundColor('#111111')
  }

  // ── update ────────────────────────────────────────────────────────────────
  update() {
    this.handleMovement()
    this.updateBatProximity()
    this.updateHeldBat()

    if (Phaser.Input.Keyboard.JustDown(this.keyE))     this.tryPickup()
    if (Phaser.Input.Keyboard.JustDown(this.keySpace)) this.startAttack()

    this.player.setDepth(10 + this.player.y / ROOM_H)
  }

  // ── Movement (locked while attacking) ────────────────────────────────────
  private handleMovement() {
    if (this.attacking) {
      this.player.setVelocity(0, 0)
      return
    }

    let vx = 0
    let vy = 0

    if (isMobile() && this.joystick) {
      vx = this.joystick.dx
      vy = this.joystick.dy
    } else {
      if (this.cursors.left.isDown  || this.wasd.left.isDown)  vx = -1
      if (this.cursors.right.isDown || this.wasd.right.isDown) vx =  1
      if (this.cursors.up.isDown    || this.wasd.up.isDown)    vy = -1
      if (this.cursors.down.isDown  || this.wasd.down.isDown)  vy =  1
    }

    if (vx !== 0 && vy !== 0) { vx *= 0.707; vy *= 0.707 }

    this.player.setVelocity(vx * PLAYER_SPEED, vy * PLAYER_SPEED)

    if (vx !== 0 || vy !== 0) {
      this.facing = Math.abs(vx) >= Math.abs(vy)
        ? (vx > 0 ? 'right' : 'left')
        : (vy > 0 ? 'down'  : 'up')
      const key = `bar-walk-${this.facing}`
      if (this.player.anims.currentAnim?.key !== key) this.player.play(key)
    } else {
      const key = `bar-idle-${this.facing}`
      if (this.player.anims.currentAnim?.key !== key) this.player.play(key)
    }
  }

  // ── Pickup proximity hint ─────────────────────────────────────────────────
  private updateBatProximity() {
    if (!this.batAlive || this.hasBat) {
      if (this.hasBat && !this.attacking) {
        this.hintText.setText(isMobile() ? '' : 'Space — swing bat')
        this.hintText.setVisible(!isMobile())
      } else {
        this.hintText.setVisible(false)
      }
      return
    }
    const dist = Phaser.Math.Distance.Between(
      this.player.x, this.player.y,
      this.batPickup.x, this.batPickup.y,
    )
    if (dist < 52) {
      this.hintText.setText(isMobile() ? 'Tap PICK UP to grab the bat' : 'E — pick up bat')
      this.hintText.setVisible(true)
    } else {
      this.hintText.setVisible(false)
    }
  }

  // ── Pickup ────────────────────────────────────────────────────────────────
  private tryPickup() {
    if (this.hasBat || !this.batAlive) return
    const dist = Phaser.Math.Distance.Between(
      this.player.x, this.player.y,
      this.batPickup.x, this.batPickup.y,
    )
    if (dist >= 52) return

    this.batAlive = false
    this.batPickup.destroy()
    this.batGlow.destroy()
    this.hasBat = true

    // Held bat — scaled down to match character proportions
    this.heldBat = this.add.sprite(this.player.x, this.player.y, 'weapon_bat', 1)
      .setScale(BAT_HELD_SCALE)

    this.tweens.add({
      targets: this.heldBat,
      scaleX: BAT_HELD_SCALE * 1.5, scaleY: BAT_HELD_SCALE * 1.5,
      duration: 100, yoyo: true, ease: 'Back.easeOut',
    })

    const label = this.add.text(this.player.x, this.player.y - 28, 'Bat equipped!', {
      fontSize: '12px', color: '#ffe566',
      stroke: '#000000', strokeThickness: 3,
    }).setOrigin(0.5).setDepth(50)
    this.tweens.add({
      targets: label, y: label.y - 32, alpha: 0, duration: 1100,
      ease: 'Power2', onComplete: () => label.destroy(),
    })

    if (isMobile()) {
      this.swingBtn?.setVisible(true)
    } else {
      this.controlsText.setText('WASD — move    Space — swing')
    }
  }

  // ── Attack ────────────────────────────────────────────────────────────────
  private startAttack() {
    if (this.attacking || !this.hasBat) return
    this.attacking = true
    this.player.setVelocity(0, 0)
    this.player.play(`bar-slash-${this.facing}`)
    // Bat position/angle is driven entirely by hand_anchors.json each frame —
    // no manual tween needed; updateHeldBat() reads the slash anchor per frame.
  }

  // ── Held bat — anchor-driven placement ───────────────────────────────────
  // Reads hand_anchors.json for the current animation, direction, and frame.
  // Anchor (x, y) is in 32×32 frame pixel space (from top-left of the sprite).
  // We convert to world offset by subtracting the frame centre (16, 16), then
  // set the bat's Phaser origin to the grip end so rotation pivots there.
  private updateHeldBat() {
    if (!this.heldBat || !this.handAnchors) return

    const animKey = this.player.anims.currentAnim?.key ?? ''

    // Map the current player animation to an anchor table entry.
    // Idle animations use the walk frame-0 anchor (same hand position).
    const animName = animKey.includes('slash') ? 'slash' : 'walk'

    // Frame index 0-3 within the current animation cycle
    const frameIdx = Number(this.player.anims.currentFrame?.textureFrame ?? 0) % 4

    const anchor = this.handAnchors[animName]?.[this.facing]?.[frameIdx]
    if (!anchor) return

    // Convert frame-space anchor to world offset from the player's centre
    // (player sprite has default origin 0.5, 0.5, so centre = pixel 16,16)
    const wx = this.player.x + anchor.x - 16
    const wy = this.player.y + anchor.y - 16

    // Set bat origin to the grip end so position() lands the grip on the hand
    // and setAngle() rotates the bat around that pivot point
    const grip = ORIENT_ORIGIN[anchor.orient] ?? { ox: 0.5, oy: 0.5 }
    this.heldBat.setOrigin(grip.ox, grip.oy)
    this.heldBat.setPosition(wx, wy)
    this.heldBat.setFrame(ORIENT_FRAME[anchor.orient] ?? 0)
    this.heldBat.setAngle(anchor.angle)

    // Depth: below player when facing down (barrel goes behind body),
    // above when facing up or to the side (arm extends forward)
    this.heldBat.setDepth(
      this.facing === 'down'
        ? this.player.depth - 0.5
        : this.player.depth + 0.5,
    )
  }
}
