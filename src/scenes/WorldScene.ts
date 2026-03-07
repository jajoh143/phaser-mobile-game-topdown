import Phaser from 'phaser'
import { Player } from '@/entities/Player'
import { NPC } from '@/entities/NPC'
import { VirtualJoystick } from '@/systems/VirtualJoystick'
import { NPC_DATA } from '@/data/npcs'
import { TILE_SIZE, SCALE } from '@/constants'
import { isMobile } from '@/utils/device'

// Simple tile map — 0 = grass, 1 = wall
const MAP_DATA = [
  [1,1,1,1,1,1,1,1,1,1,1],
  [1,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,1,1,0,0,1,0,0,1],
  [1,0,0,1,0,0,0,1,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,1,0,0,0,1,0,0,1],
  [1,0,0,1,1,0,0,1,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,1],
  [1,1,1,1,1,1,1,1,1,1,1],
]

export class WorldScene extends Phaser.Scene {
  private player!: Player
  private npcs!: Phaser.Physics.Arcade.StaticGroup
  private walls!: Phaser.Physics.Arcade.StaticGroup
  private joystick!: VirtualJoystick
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys
  private wasd!: Record<'up' | 'down' | 'left' | 'right', Phaser.Input.Keyboard.Key>
  private interactBtn!: Phaser.GameObjects.Container
  private inDialogue = false
  private npcList: NPC[] = []
  private mobile = isMobile()

  constructor() {
    super({ key: 'WorldScene' })
  }

  create() {
    this.buildMap()
    this.spawnPlayer()
    this.spawnNPCs()
    this.setupCamera()
    this.setupInput()
    this.setupCollisions()
    this.buildInteractButton()
    this.setupUIBridge()
  }

  // ── Map ──────────────────────────────────────────────────────────────────

  private buildMap() {
    this.walls = this.physics.add.staticGroup()
    const tileW = TILE_SIZE * SCALE
    const tileH = TILE_SIZE * SCALE

    MAP_DATA.forEach((row, rowIdx) => {
      row.forEach((cell, colIdx) => {
        const x = colIdx * tileW + tileW / 2
        const y = rowIdx * tileH + tileH / 2

        const img = this.add.image(x, y, 'tiles')
        img.setScale(SCALE)
        img.setDepth(0)

        if (cell === 0) {
          // Grass — crop to first tile
          img.setCrop(0, 0, TILE_SIZE, TILE_SIZE)
        } else {
          // Wall — crop to second tile
          img.setCrop(TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
          const wallBody = this.walls.create(x, y) as Phaser.Physics.Arcade.Image
          wallBody.setVisible(false)
          wallBody.setSize(tileW, tileH)
          wallBody.refreshBody()
        }
      })
    })
  }

  // ── Player ───────────────────────────────────────────────────────────────

  private spawnPlayer() {
    const tileW = TILE_SIZE * SCALE
    this.player = new Player(this, tileW * 2, tileW * 2)
  }

  // ── NPCs ─────────────────────────────────────────────────────────────────

  private spawnNPCs() {
    this.npcs = this.physics.add.staticGroup()

    NPC_DATA.forEach((data) => {
      const npc = new NPC(this, data.x * SCALE, data.y * SCALE, data.id, data.name, data.dialogue)
      this.npcs.add(npc)
      this.npcList.push(npc)
    })
  }

  // ── Camera ───────────────────────────────────────────────────────────────

  private setupCamera() {
    const mapW = MAP_DATA[0].length * TILE_SIZE * SCALE
    const mapH = MAP_DATA.length * TILE_SIZE * SCALE
    this.cameras.main.setBounds(0, 0, mapW, mapH)
    this.cameras.main.startFollow(this.player, true, 0.1, 0.1)
  }

  // ── Input ────────────────────────────────────────────────────────────────

  private setupInput() {
    this.joystick = new VirtualJoystick(this, this.mobile)
    this.cursors = this.input.keyboard!.createCursorKeys()

    const kb = this.input.keyboard!
    this.wasd = {
      up:    kb.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      down:  kb.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      left:  kb.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      right: kb.addKey(Phaser.Input.Keyboard.KeyCodes.D),
    }

    // Keyboard interact (Space / Enter) — desktop only
    if (!this.mobile) {
      kb.on('keydown-SPACE', () => this.tryInteract())
      kb.on('keydown-ENTER', () => this.tryInteract())
    }
  }

  private buildInteractButton() {
    // Only render the on-screen button on mobile
    if (!this.mobile) return

    const { width, height } = this.cameras.main
    const r = 30

    const circle = this.add
      .circle(0, 0, r, 0x4a9ade, 0.7)
      .setStrokeStyle(2, 0xffffff, 0.8)

    const label = this.add.text(0, 0, 'A', {
      fontSize: '16px',
      color: '#ffffff',
      fontStyle: 'bold',
    }).setOrigin(0.5)

    this.interactBtn = this.add.container(width - 60, height - 110, [circle, label])
    this.interactBtn.setDepth(50)
    this.interactBtn.setScrollFactor(0)
    this.interactBtn.setSize(r * 2, r * 2)
    this.interactBtn.setInteractive()
    this.interactBtn.on('pointerdown', () => this.tryInteract())
  }

  // ── Collisions ───────────────────────────────────────────────────────────

  private setupCollisions() {
    this.physics.add.collider(this.player, this.walls)
    this.physics.add.collider(this.player, this.npcs)
  }

  // ── UI Bridge ────────────────────────────────────────────────────────────

  private setupUIBridge() {
    // UIScene listens to events emitted here
    this.events.on('start-dialogue', (npc: NPC) => {
      this.inDialogue = true
      this.player.halt()
      this.scene.get('UIScene').events.emit('open-dialogue', npc.dialogue, () => {
        this.inDialogue = false
      })
    })
  }

  // ── Interaction ──────────────────────────────────────────────────────────

  private tryInteract() {
    if (this.inDialogue) return
    const point = this.player.getInteractPoint()

    // Find the nearest NPC within interact range
    const range = TILE_SIZE * SCALE * 1.2
    let closest: NPC | null = null
    let closestDist = range

    this.npcList.forEach((npc) => {
      const d = Phaser.Math.Distance.Between(point.x, point.y, npc.x, npc.y)
      if (d < closestDist) {
        closestDist = d
        closest = npc
      }
    })

    if (closest) {
      this.events.emit('start-dialogue', closest)
    }
  }

  // ── Update ───────────────────────────────────────────────────────────────

  update() {
    if (this.inDialogue) {
      this.player.halt()
      return
    }

    let vx = this.joystick.dx
    let vy = this.joystick.dy

    // Arrow keys
    if (this.cursors.left.isDown)       vx = -1
    if (this.cursors.right.isDown)      vx = 1
    if (this.cursors.up.isDown)         vy = -1
    if (this.cursors.down.isDown)       vy = 1
    // WASD
    if (this.wasd.left.isDown)          vx = -1
    if (this.wasd.right.isDown)         vx = 1
    if (this.wasd.up.isDown)            vy = -1
    if (this.wasd.down.isDown)          vy = 1

    // Normalize diagonal movement
    const len = Math.sqrt(vx * vx + vy * vy)
    if (len > 1) { vx /= len; vy /= len }

    this.player.move(vx, vy)

    // Update NPC indicators based on proximity
    const point = this.player.getInteractPoint()
    const range = TILE_SIZE * SCALE * 1.5
    this.npcList.forEach((npc) => {
      const d = Phaser.Math.Distance.Between(point.x, point.y, npc.x, npc.y)
      npc.showIndicator(d < range)
    })
  }
}
