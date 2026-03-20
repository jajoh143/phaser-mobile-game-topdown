import Phaser from 'phaser'
import { TILE_SIZE, GAME_WIDTH, GAME_HEIGHT, PLAYER_SPEED } from '../constants'
import { VirtualJoystick } from '../systems/VirtualJoystick'
import { isMobile } from '../utils/device'

// ─── Map constants ────────────────────────────────────────────────────────────
const TILE = TILE_SIZE          // 32 px
const MAP_W = 11
const MAP_H = 20
const ROOM_W = MAP_W * TILE     // 352 px
const ROOM_H = MAP_H * TILE     // 640 px
const ROOM_X = Math.floor((GAME_WIDTH - ROOM_W) / 2)  // 4 px — centred in 360

// 0 = wood floor  |  1 = brick wall  |  2 = bar counter
const MAP: number[][] = [
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  // row  0 — north wall
  [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  // row  1 — bar counter
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  2 — floor (bar-front overhang here)
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  3
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  4
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  5
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  6
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  7  ← bat pickup
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  8
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row  9
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 10
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 11 ← player start
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 12
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 13
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 14
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 15
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 16
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 17
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // row 18
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  // row 19 — south wall
]

// ─── Bottle placement [tile-col, spritesheet-frame] ───────────────────────────
// alcohol_bottles.png frames: 0=whiskey 1=wine 2=gin 3=beer
const BOTTLE_DEFS: [number, number][] = [
  [2, 0],  // whiskey
  [4, 3],  // beer
  [6, 1],  // wine
  [8, 2],  // gin
]

// ─── Pickup / spawn positions [tile-col, tile-row] ───────────────────────────
const BAT_TILE: [number, number]    = [5, 7]
const PLAYER_TILE: [number, number] = [5, 11]

// ─── Weapon-frame and hand-offset per facing direction ───────────────────────
// weapon_bat.png frames: 0=East 1=South 2=West 3=North
const DIR_BAT_FRAME: Record<string, number> = {
  right: 0, down: 1, left: 2, up: 3,
}
const DIR_BAT_OFFSET: Record<string, { x: number; y: number }> = {
  right: { x: 16, y:  2 },
  down:  { x:  2, y: 16 },
  left:  { x: -16, y:  2 },
  up:    { x:  2, y: -16 },
}

// ─── Scene ────────────────────────────────────────────────────────────────────
export class BarScene extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite
  private walls!: Phaser.Physics.Arcade.StaticGroup
  private barBodies!: Phaser.Physics.Arcade.StaticGroup

  private batPickup!: Phaser.Physics.Arcade.Sprite
  private batGlow!: Phaser.GameObjects.Arc
  private batAlive = true

  private heldBat: Phaser.GameObjects.Sprite | null = null
  private hasBat = false

  private facing = 'down'

  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys
  private wasd!: Record<string, Phaser.Input.Keyboard.Key>
  private keyE!: Phaser.Input.Keyboard.Key

  private joystick!: VirtualJoystick
  private hintText!: Phaser.GameObjects.Text

  constructor() {
    super({ key: 'BarScene' })
  }

  // ── create ────────────────────────────────────────────────────────────────
  create() {
    this.createAnimations()
    this.buildMap()
    this.spawnPlayer()
    this.spawnBatPickup()
    this.setupCollisions()
    this.setupInput()
    this.setupCamera()
    this.setupHintText()
  }

  // ── Animations ────────────────────────────────────────────────────────────
  private createAnimations() {
    // char_0.png: 128×128, frameWidth=32, frameHeight=32
    // Row 0 (frames  0-3): walk down
    // Row 1 (frames  4-7): walk left
    // Row 2 (frames  8-11): walk right
    // Row 3 (frames 12-15): walk up
    const walks = [
      { key: 'bar-walk-down',  start: 0,  end: 3  },
      { key: 'bar-walk-left',  start: 4,  end: 7  },
      { key: 'bar-walk-right', start: 8,  end: 11 },
      { key: 'bar-walk-up',    start: 12, end: 15 },
    ]
    for (const a of walks) {
      if (!this.anims.exists(a.key)) {
        this.anims.create({
          key: a.key,
          frames: this.anims.generateFrameNumbers('char_0', { start: a.start, end: a.end }),
          frameRate: 8,
          repeat: -1,
        })
      }
    }

    const idles = [
      { key: 'bar-idle-down',  frame: 0  },
      { key: 'bar-idle-left',  frame: 4  },
      { key: 'bar-idle-right', frame: 8  },
      { key: 'bar-idle-up',    frame: 12 },
    ]
    for (const a of idles) {
      if (!this.anims.exists(a.key)) {
        this.anims.create({
          key: a.key,
          frames: [{ key: 'char_0', frame: a.frame }],
          frameRate: 1,
        })
      }
    }
  }

  // ── Map / environment ─────────────────────────────────────────────────────
  private buildMap() {
    this.walls    = this.physics.add.staticGroup()
    this.barBodies = this.physics.add.staticGroup()

    for (let row = 0; row < MAP_H; row++) {
      for (let col = 0; col < MAP_W; col++) {
        const wx   = ROOM_X + col * TILE
        const wy   = row * TILE
        const cell = MAP[row][col]

        // Wood floor underneath everything (depth 0)
        this.add.image(wx, wy, 'wood_floor').setOrigin(0, 0).setDepth(0)

        if (cell === 1) {
          // Brick wall tile — visual + physics body (depth 1)
          this.add.image(wx, wy, 'brick_wall').setOrigin(0, 0).setDepth(1)
          const body = this.walls.create(
            wx + TILE / 2, wy + TILE / 2, 'brick_wall',
          ) as Phaser.Physics.Arcade.Sprite
          body.setVisible(false)
          body.refreshBody()

        } else if (cell === 2) {
          // Bar counter — 32×64 visual (front face hangs into row 2), depth 2
          // Physics collision covers only the top 32×32
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

    // Bottles sitting on the bar surface (row 1, depth 3)
    for (const [col, frame] of BOTTLE_DEFS) {
      const bx = ROOM_X + col * TILE + TILE / 2
      const by = 1 * TILE + TILE / 2
      this.add.sprite(bx, by, 'alcohol_bottles', frame).setDepth(3)
    }
  }

  // ── Player ────────────────────────────────────────────────────────────────
  private spawnPlayer() {
    const px = ROOM_X + PLAYER_TILE[0] * TILE + TILE / 2
    const py = PLAYER_TILE[1] * TILE + TILE / 2
    this.player = this.physics.add.sprite(px, py, 'char_0', 0)
    // Shrink collision body to feet area
    this.player.body!.setSize(20, 10)
    this.player.body!.setOffset(6, 22)
    this.player.play('bar-idle-down')
  }

  // ── Bat pickup ────────────────────────────────────────────────────────────
  private spawnBatPickup() {
    const bx = ROOM_X + BAT_TILE[0] * TILE + TILE / 2
    const by = BAT_TILE[1] * TILE + TILE / 2

    // Glow halo (depth 4)
    this.batGlow = this.add.circle(bx, by, 18, 0xffdd44, 0.3).setDepth(4)
    this.tweens.add({
      targets: this.batGlow,
      alpha: 0.6,
      duration: 900,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut',
    })

    // Bat sprite — frame 1 (south/down orientation) — depth 5
    this.batPickup = this.physics.add.sprite(bx, by, 'weapon_bat', 1)
    this.batPickup.setDepth(5)
    ;(this.batPickup.body as Phaser.Physics.Arcade.Body).setImmovable(true)
    ;(this.batPickup.body as Phaser.Physics.Arcade.Body).allowGravity = false

    // Gentle bob
    this.tweens.add({
      targets: this.batPickup,
      y: by - 5,
      duration: 900,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut',
    })
  }

  // ── Physics collisions ────────────────────────────────────────────────────
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
    this.keyE = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.E)

    if (isMobile()) {
      this.joystick = new VirtualJoystick(this, true)

      // Interact button — fixed top-right
      this.add.text(GAME_WIDTH - 72, GAME_HEIGHT - 90, 'PICK\nUP', {
        fontSize: '13px',
        color: '#ffffff',
        backgroundColor: '#33333399',
        padding: { x: 12, y: 8 },
        align: 'center',
      })
        .setScrollFactor(0)
        .setDepth(100)
        .setInteractive()
        .on('pointerdown', () => this.tryPickup())
    }
  }

  // ── HUD hint ──────────────────────────────────────────────────────────────
  private setupHintText() {
    this.hintText = this.add
      .text(GAME_WIDTH / 2, GAME_HEIGHT - 56, '', {
        fontSize: '13px',
        color: '#ffe566',
        backgroundColor: '#00000099',
        padding: { x: 10, y: 5 },
        align: 'center',
      })
      .setOrigin(0.5)
      .setScrollFactor(0)
      .setDepth(100)
      .setVisible(false)
  }

  // ── Camera ────────────────────────────────────────────────────────────────
  private setupCamera() {
    this.cameras.main.setBounds(ROOM_X, 0, ROOM_W, ROOM_H)
    this.cameras.main.startFollow(this.player, true, 0.1, 0.1)
    this.cameras.main.setBackgroundColor('#111111')
  }

  // ── update ────────────────────────────────────────────────────────────────
  update() {
    this.handleMovement()
    this.updateBatProximity()
    this.updateHeldBat()

    if (Phaser.Input.Keyboard.JustDown(this.keyE)) {
      this.tryPickup()
    }

    // Y-sort: player renders above floor/bar-front, below nothing (always front)
    this.player.setDepth(10 + this.player.y / ROOM_H)
  }

  // ── Movement ──────────────────────────────────────────────────────────────
  private handleMovement() {
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

    // Normalise diagonal
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
      this.hintText.setVisible(false)
      return
    }
    const dist = Phaser.Math.Distance.Between(
      this.player.x, this.player.y,
      this.batPickup.x, this.batPickup.y,
    )
    const near = dist < 52
    if (near) {
      this.hintText.setText(isMobile() ? 'Tap PICK UP to grab the bat' : 'Press E  to pick up the bat')
      this.hintText.setVisible(true)
    } else {
      this.hintText.setVisible(false)
    }
  }

  // ── Attempt pickup ────────────────────────────────────────────────────────
  private tryPickup() {
    if (this.hasBat || !this.batAlive) return

    const dist = Phaser.Math.Distance.Between(
      this.player.x, this.player.y,
      this.batPickup.x, this.batPickup.y,
    )
    if (dist >= 52) return

    // Remove pickup
    this.batAlive = false
    this.batPickup.destroy()
    this.batGlow.destroy()
    this.hintText.setVisible(false)
    this.hasBat = true

    // Create held-bat sprite at player position (depth just above player)
    this.heldBat = this.add.sprite(this.player.x, this.player.y, 'weapon_bat', 1)

    // Pop effect
    this.tweens.add({
      targets: this.heldBat,
      scaleX: 1.4,
      scaleY: 1.4,
      duration: 100,
      yoyo: true,
      ease: 'Back.easeOut',
    })

    // Floating "Bat equipped!" label
    const label = this.add.text(this.player.x, this.player.y - 24, 'Bat equipped!', {
      fontSize: '12px',
      color: '#ffe566',
      stroke: '#000000',
      strokeThickness: 3,
    }).setOrigin(0.5).setDepth(50)

    this.tweens.add({
      targets: label,
      y: label.y - 32,
      alpha: 0,
      duration: 1100,
      ease: 'Power2',
      onComplete: () => label.destroy(),
    })
  }

  // ── Held bat — follows player each frame ──────────────────────────────────
  private updateHeldBat() {
    if (!this.heldBat) return

    const off = DIR_BAT_OFFSET[this.facing]
    this.heldBat.setPosition(this.player.x + off.x, this.player.y + off.y)
    this.heldBat.setFrame(DIR_BAT_FRAME[this.facing])
    // Render in front of player when facing up, behind when facing down
    this.heldBat.setDepth(
      this.facing === 'down'
        ? this.player.depth - 0.5
        : this.player.depth + 0.5,
    )
  }
}
