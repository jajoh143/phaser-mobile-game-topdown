/**
 * WeaponDemoScene — demonstrates melee, ranged, spell, and thrown attacks.
 *
 * Controls:
 *   WASD / arrows — move
 *   Space / Z     — attack (melee: slash | ranged: fire | staff: spell)
 *   1-4           — select inventory slot
 *   Q / E         — cycle weapons
 *   Walk into pickups to collect (up to 4 slots)
 *
 * Projectile types by weapon:
 *   pistol  — fast bullet, grey, small muzzle flash
 *   shotgun — 3-pellet spread, grey, wider flash
 *   rifle   — very fast elongated bullet, yellow-white flash
 *   bow     — slow arrow, brown/tan, no flash
 *   staff   — slow magic bolt, colour tinted, sparkle trail
 *   molotov — arc-trajectory fire bottle, orange glow on impact
 */

import Phaser from 'phaser'
import { EquippedPlayer, AnchorData, FireEvent } from '@/entities/EquippedPlayer'
import { INVENTORY_SIZE } from '@/systems/Inventory'

const CHAR_KEY = 'char_0'

const DEMO_WEAPONS = ['sword', 'pistol', 'staff', 'bow']

const PICKUP_POSITIONS = [
  { weapon: 'sword',  tx: 5,  ty: 5  },
  { weapon: 'pistol', tx: 14, ty: 5  },
  { weapon: 'staff',  tx: 5,  ty: 14 },
  { weapon: 'bow',    tx: 14, ty: 14 },
]

const TILE     = 48
const MAP_TILES = 20

const WEAPON_COLORS: Record<string, number> = {
  sword: 0xc0a060, axe: 0x8080ff, spear: 0x60c080, staff: 0x8040c0,
  bow: 0x80c040, dagger: 0xc04040, mace: 0xa06040, greatsword: 0xff8040,
  pistol: 0x808080, shotgun: 0x606060, rifle: 0x506050, bat: 0x804020,
  knife: 0xd0d0d0, chain: 0xa0a0a0, molotov: 0xff6020, taser: 0xffff40,
}

// Projectile config per weapon
interface ProjConfig {
  count:    number      // pellets / projectiles
  speed:    number      // px/s
  color:    number
  w:        number      // visual width
  h:        number      // visual height
  spread:   number      // random angle spread (degrees)
  lifetime: number      // ms
  arc:      boolean     // molotov-style gravity arc
  flash:    number      // muzzle flash color, 0 = none
  trail:    boolean     // leave a colour trail
}

const PROJ_CONFIGS: Record<string, ProjConfig> = {
  pistol:  { count: 1, speed: 520, color: 0xdddddd, w: 4,  h: 4,  spread: 3,  lifetime: 800,  arc: false, flash: 0xffff88, trail: false },
  shotgun: { count: 5, speed: 380, color: 0xbbbbbb, w: 4,  h: 4,  spread: 18, lifetime: 400,  arc: false, flash: 0xffee66, trail: false },
  rifle:   { count: 1, speed: 800, color: 0xfff0aa, w: 8,  h: 3,  spread: 1,  lifetime: 600,  arc: false, flash: 0xffffff, trail: false },
  bow:     { count: 1, speed: 260, color: 0x9a7a40, w: 10, h: 2,  spread: 2,  lifetime: 1200, arc: false, flash: 0,        trail: false },
  staff:   { count: 1, speed: 220, color: 0xaa44ff, w: 6,  h: 6,  spread: 0,  lifetime: 1400, arc: false, flash: 0xcc88ff, trail: true  },
  molotov: { count: 1, speed: 180, color: 0xff7700, w: 8,  h: 8,  spread: 5,  lifetime: 1600, arc: true,  flash: 0,        trail: true  },
}

interface Pickup {
  sprite: Phaser.GameObjects.Arc
  weapon: string
  label:  Phaser.GameObjects.Text
}

export class WeaponDemoScene extends Phaser.Scene {
  private player!:    EquippedPlayer
  private cursors!:   Phaser.Types.Input.Keyboard.CursorKeys
  private wasd!:      Record<'up'|'down'|'left'|'right', Phaser.Input.Keyboard.Key>
  private attackKey!: Phaser.Input.Keyboard.Key
  private altAttack!: Phaser.Input.Keyboard.Key
  private slotKeys:   Phaser.Input.Keyboard.Key[] = []
  private cycleNext!: Phaser.Input.Keyboard.Key
  private cyclePrev!: Phaser.Input.Keyboard.Key

  private pickups:    Pickup[] = []
  private hudBorders: Phaser.GameObjects.Rectangle[] = []
  private hudSlots:   Phaser.GameObjects.Rectangle[] = []
  private hudIcons:   Phaser.GameObjects.Text[]      = []

  // Projectile pool
  private projectiles!: Phaser.Physics.Arcade.Group
  // Flash sprites (short-lived)
  private flashes:      Phaser.GameObjects.Arc[] = []
  // Trail particles stored per projectile
  private trailTimers:  Map<Phaser.Physics.Arcade.Image, Phaser.Time.TimerEvent> = new Map()

  constructor() {
    super({ key: 'WeaponDemoScene' })
  }

  preload(): void {
    this.load.spritesheet(CHAR_KEY, `assets/sprites/${CHAR_KEY}.png`, {
      frameWidth: 32, frameHeight: 32,
    })
    for (const w of DEMO_WEAPONS) {
      this.load.spritesheet(`weapon_${w}`, `assets/sprites/weapon_${w}.png`, {
        frameWidth: 32, frameHeight: 32,
      })
    }
    this.load.json('hand_anchors', 'assets/sprites/hand_anchors.json')
  }

  create(): void {
    this._createWorld()

    const cx = (MAP_TILES / 2) * TILE
    const cy = (MAP_TILES / 2) * TILE

    this.player = new EquippedPlayer(this, cx, cy, CHAR_KEY)
    this.player.createAnimations(CHAR_KEY)

    const anchors = this.cache.json.get('hand_anchors') as AnchorData | null
    if (anchors) this.player.setAnchors(anchors)

    // Projectile group
    this.projectiles = this.physics.add.group()

    // Hook weapon fire events
    this.player.onFire = (e) => this._spawnProjectiles(e)

    this.children.bringToTop(this.player.weapon)

    this._createPickups()

    this.cameras.main.setBounds(0, 0, MAP_TILES * TILE, MAP_TILES * TILE)
    this.cameras.main.startFollow(this.player.body, true, 0.1, 0.1)

    this._setupInput()
    this._createHUD()
    this._createHelp()
  }

  update(): void {
    let vx = 0
    let vy = 0
    if (this.cursors.left.isDown  || this.wasd.left.isDown)  vx = -160
    if (this.cursors.right.isDown || this.wasd.right.isDown) vx =  160
    if (this.cursors.up.isDown    || this.wasd.up.isDown)    vy = -160
    if (this.cursors.down.isDown  || this.wasd.down.isDown)  vy =  160

    this.player.body.setVelocity(vx, vy)
    this.player.update(vx, vy)

    if (Phaser.Input.Keyboard.JustDown(this.attackKey) ||
        Phaser.Input.Keyboard.JustDown(this.altAttack)) {
      this.player.attack()
    }

    for (let i = 0; i < INVENTORY_SIZE; i++) {
      if (Phaser.Input.Keyboard.JustDown(this.slotKeys[i])) {
        this.player.inventory.selectSlot(i)
        this.player.equipWeapon(this.player.inventory.active)
      }
    }
    if (Phaser.Input.Keyboard.JustDown(this.cycleNext)) {
      this.player.inventory.cycleNext()
      this.player.equipWeapon(this.player.inventory.active)
    }
    if (Phaser.Input.Keyboard.JustDown(this.cyclePrev)) {
      this.player.inventory.cyclePrev()
      this.player.equipWeapon(this.player.inventory.active)
    }

    this._checkPickups()
    this._updateHUD()
    this._tickProjectiles()
  }

  // ── projectile spawning ────────────────────────────────────────────────────

  private _spawnProjectiles(e: FireEvent): void {
    const cfg = PROJ_CONFIGS[e.weapon]
    if (!cfg) return

    // Muzzle flash
    if (cfg.flash) {
      const f = this.add.circle(e.x, e.y, 8, cfg.flash, 0.9).setDepth(10)
      this.flashes.push(f)
      this.time.delayedCall(80, () => {
        f.destroy()
        this.flashes = this.flashes.filter(x => x !== f)
      })
    }

    const baseAngle = Math.atan2(e.dirY, e.dirX) // radians

    for (let i = 0; i < cfg.count; i++) {
      const spread  = (cfg.spread * (Math.random() - 0.5) * Math.PI) / 180
      const angle   = baseAngle + spread
      const vx      = Math.cos(angle) * cfg.speed
      const vy      = Math.sin(angle) * cfg.speed

      const proj = this.physics.add.image(e.x, e.y, '__missing__') as Phaser.Physics.Arcade.Image
      proj.setDisplaySize(cfg.w, cfg.h)
      proj.setTint(cfg.color)
      proj.setDepth(9)
      proj.setRotation(angle)
      ;(proj as any)._type   = e.type
      ;(proj as any)._weapon = e.weapon
      ;(proj as any)._born   = this.time.now

      if (cfg.arc) {
        // Arc: apply gravity-like vy addition over time
        proj.setVelocity(vx, vy)
        ;(proj.body as Phaser.Physics.Arcade.Body).setGravityY(320)
      } else {
        proj.setVelocity(vx, vy)
      }

      if (cfg.trail) {
        const t = this.time.addEvent({
          delay: 40,
          loop: true,
          callback: () => this._emitTrail(proj, cfg),
        })
        this.trailTimers.set(proj, t)
      }

      this.projectiles.add(proj)
    }
  }

  private _emitTrail(
    proj: Phaser.Physics.Arcade.Image,
    cfg: ProjConfig,
  ): void {
    if (!proj.active) return
    const dot = this.add.circle(proj.x, proj.y, 3, cfg.color, 0.5).setDepth(8)
    this.tweens.add({
      targets: dot,
      alpha: 0,
      scaleX: 0,
      scaleY: 0,
      duration: 220,
      onComplete: () => dot.destroy(),
    })
  }

  private _tickProjectiles(): void {
    const now = this.time.now
    this.projectiles.getChildren().forEach((child) => {
      const p = child as Phaser.Physics.Arcade.Image
      if (!p.active) return
      const born = (p as any)._born as number
      const weapon = (p as any)._weapon as string
      const cfg  = PROJ_CONFIGS[weapon]
      if (!cfg) { p.destroy(); return }
      if (now - born > cfg.lifetime) {
        this._destroyProjectile(p)
      }
    })
  }

  private _destroyProjectile(p: Phaser.Physics.Arcade.Image): void {
    const t = this.trailTimers.get(p)
    if (t) { t.destroy(); this.trailTimers.delete(p) }
    // Impact effect for molotov
    const weapon = (p as any)._weapon as string
    if (weapon === 'molotov') {
      this._spawnImpact(p.x, p.y, 0xff5500, 28)
    } else if ((PROJ_CONFIGS[weapon]?.trail) && weapon === 'staff') {
      this._spawnImpact(p.x, p.y, 0xaa44ff, 16)
    }
    p.destroy()
  }

  private _spawnImpact(x: number, y: number, color: number, radius: number): void {
    const ring = this.add.circle(x, y, radius, color, 0.7).setDepth(10)
    this.tweens.add({
      targets: ring,
      scaleX: 2.5,
      scaleY: 2.5,
      alpha: 0,
      duration: 380,
      onComplete: () => ring.destroy(),
    })
  }

  // ── world, pickups, input, HUD ─────────────────────────────────────────────

  private _createWorld(): void {
    const size = MAP_TILES * TILE
    const bg   = this.add.graphics()
    for (let ty = 0; ty < MAP_TILES; ty++) {
      for (let tx = 0; tx < MAP_TILES; tx++) {
        bg.fillStyle((tx + ty) % 2 === 0 ? 0x2a4a2a : 0x254525, 1)
        bg.fillRect(tx * TILE, ty * TILE, TILE, TILE)
      }
    }
    this.add.graphics().lineStyle(4, 0x606060, 1).strokeRect(0, 0, size, size)
    this.physics.world.setBounds(TILE, TILE, size - TILE * 2, size - TILE * 2)
  }

  private _createPickups(): void {
    for (const { weapon, tx, ty } of PICKUP_POSITIONS) {
      const wx    = tx * TILE + TILE / 2
      const wy    = ty * TILE + TILE / 2
      const color = WEAPON_COLORS[weapon] ?? 0xffffff
      const dot   = this.add.circle(wx, wy, 10, color).setDepth(1)
      const label = this.add.text(wx, wy + 13, weapon, {
        fontSize: '9px', color: '#eeeeee',
        backgroundColor: '#00000088', padding: { x: 2, y: 1 },
      }).setOrigin(0.5, 0).setDepth(1)
      this.pickups.push({ sprite: dot, weapon, label })
    }
  }

  private _checkPickups(): void {
    const px = this.player.body.x
    const py = this.player.body.y
    for (let i = this.pickups.length - 1; i >= 0; i--) {
      const p    = this.pickups[i]
      const dist = Phaser.Math.Distance.Between(px, py, p.sprite.x, p.sprite.y)
      if (dist < 28) {
        const slot = this.player.inventory.add(p.weapon)
        if (slot !== -1) {
          if (this.player.inventory.snapshot.filter(s => s !== null).length === 1) {
            this.player.equipWeapon(p.weapon)
          }
          p.sprite.destroy()
          p.label.destroy()
          this.pickups.splice(i, 1)
        }
      }
    }
  }

  private _setupInput(): void {
    this.cursors    = this.input.keyboard!.createCursorKeys()
    const KB        = Phaser.Input.Keyboard.KeyCodes
    this.wasd       = {
      up:    this.input.keyboard!.addKey(KB.W),
      down:  this.input.keyboard!.addKey(KB.S),
      left:  this.input.keyboard!.addKey(KB.A),
      right: this.input.keyboard!.addKey(KB.D),
    }
    this.attackKey  = this.input.keyboard!.addKey(KB.SPACE)
    this.altAttack  = this.input.keyboard!.addKey(KB.Z)
    this.cycleNext  = this.input.keyboard!.addKey(KB.E)
    this.cyclePrev  = this.input.keyboard!.addKey(KB.Q)
    for (let i = 0; i < INVENTORY_SIZE; i++) {
      this.slotKeys.push(this.input.keyboard!.addKey((KB.ONE as number) + i))
    }
  }

  private _createHUD(): void {
    const sz  = 44
    const pad = 6
    const sx  = 12
    const sy  = this.scale.height - sz - 12
    for (let i = 0; i < INVENTORY_SIZE; i++) {
      const x = sx + i * (sz + pad)
      this.hudBorders.push(
        this.add.rectangle(x + sz / 2, sy + sz / 2, sz, sz, 0, 0)
          .setStrokeStyle(2, 0x888888).setScrollFactor(0).setDepth(100)
      )
      this.hudSlots.push(
        this.add.rectangle(x + sz / 2, sy + sz / 2, sz - 4, sz - 4, 0x222222, 0.8)
          .setScrollFactor(0).setDepth(101)
      )
      this.hudIcons.push(
        this.add.text(x + sz / 2, sy + sz / 2, '', {
          fontSize: '10px', color: '#ffffff',
        }).setOrigin(0.5).setScrollFactor(0).setDepth(102)
      )
      this.add.text(x + 3, sy + 2, `${i + 1}`, {
        fontSize: '9px', color: '#aaaaaa',
      }).setScrollFactor(0).setDepth(103)
    }
  }

  private _updateHUD(): void {
    const snap   = this.player.inventory.snapshot
    const active = this.player.inventory.activeIndex
    for (let i = 0; i < INVENTORY_SIZE; i++) {
      const isActive = i === active && snap[i] !== null
      this.hudBorders[i].setStrokeStyle(2, isActive ? 0xffdd44 : 0x888888)
      this.hudSlots[i].setFillStyle(isActive ? 0x443300 : 0x222222, 0.8)
      this.hudIcons[i].setText(snap[i] ? snap[i]!.substring(0, 6) : '')
    }
  }

  private _createHelp(): void {
    const type = this.player.getAttackType() ?? 'melee'
    const lines = [
      'WASD / Arrows — move',
      'Space / Z — attack',
      '1-4 — select slot  Q/E — cycle',
      'Walk into pickups to collect',
    ]
    this.add.text(12, 12, lines.join('\n'), {
      fontSize: '11px', color: '#cccccc',
      backgroundColor: '#00000088', padding: { x: 6, y: 4 },
    }).setScrollFactor(0).setDepth(100)
  }
}
