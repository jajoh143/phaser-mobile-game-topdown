import Phaser from 'phaser'
import { GAME_WIDTH, GAME_HEIGHT } from '../constants'

// ─── Combat constants ─────────────────────────────────────────────────────────
const DEMON_MAX_HP       = 80
const PLAYER_MAX_HP      = 100
const ATK_BASE           = { min: 10, max: 20 }  // player unarmed
const ATK_WEAPON_BONUS   = { min: 6,  max: 12 }  // bonus damage with bat
const DEMON_ATK          = { min: 8,  max: 16 }
const DEFEND_MULTIPLIER  = 0.45   // incoming damage × this when defending
const FLEE_SUCCESS_RATE  = 0.60

// ─── Layout Y anchors (scale to GAME_HEIGHT fraction so it works on any size) ─
const LY = {
  demonName:    Math.round(GAME_HEIGHT * 0.04),
  demonHPBar:   Math.round(GAME_HEIGHT * 0.09),
  demonSprite:  Math.round(GAME_HEIGHT * 0.22),
  divider:      Math.round(GAME_HEIGHT * 0.41),
  log:          Math.round(GAME_HEIGHT * 0.50),
  playerSprite: Math.round(GAME_HEIGHT * 0.65),
  playerName:   Math.round(GAME_HEIGHT * 0.79),
  playerHPBar:  Math.round(GAME_HEIGHT * 0.84),
  turnLabel:    Math.round(GAME_HEIGHT * 0.89),
  buttons:      Math.round(GAME_HEIGHT * 0.945),
}

const BAR_W = Math.min(220, Math.round(GAME_WIDTH * 0.6))
const CX    = Math.round(GAME_WIDTH / 2)

type BattleState = 'player_turn' | 'processing' | 'enemy_turn' | 'victory' | 'defeat'

export interface BattleInitData {
  playerHP?:    number
  playerMaxHP?: number
  hasWeapon?:   boolean
}

// ─── Scene ────────────────────────────────────────────────────────────────────
export class BattleScene extends Phaser.Scene {
  // State
  private playerHP    = PLAYER_MAX_HP
  private playerMaxHP = PLAYER_MAX_HP
  private demonHP     = DEMON_MAX_HP
  private hasWeapon   = false
  private defending   = false
  private state: BattleState = 'player_turn'

  // UI
  private demonSprite!:   Phaser.GameObjects.Sprite
  private playerSprite!:  Phaser.GameObjects.Sprite
  private demonBar!:      Phaser.GameObjects.Graphics
  private playerBar!:     Phaser.GameObjects.Graphics
  private demonHPLabel!:  Phaser.GameObjects.Text
  private playerHPLabel!: Phaser.GameObjects.Text
  private logText!:       Phaser.GameObjects.Text
  private turnText!:      Phaser.GameObjects.Text
  private btns:           Phaser.GameObjects.Text[] = []

  constructor() { super({ key: 'BattleScene' }) }

  init(data: BattleInitData) {
    this.playerHP    = data.playerHP    ?? PLAYER_MAX_HP
    this.playerMaxHP = data.playerMaxHP ?? PLAYER_MAX_HP
    this.hasWeapon   = data.hasWeapon   ?? false
    this.demonHP     = DEMON_MAX_HP
    this.defending   = false
    this.state       = 'player_turn'
  }

  create() {
    this.buildBackground()
    this.buildDemonSide()
    this.buildPlayerSide()
    this.buildLog()
    this.buildButtons()
    this.buildTurnLabel()

    this.setLog('The demon bartender\ncrackles with dark energy!')
    this.time.delayedCall(1400, () => this.beginPlayerTurn())
  }

  // ── Background ─────────────────────────────────────────────────────────────
  private buildBackground() {
    const W = GAME_WIDTH, H = GAME_HEIGHT
    const g = this.add.graphics()

    // Base
    g.fillStyle(0x0a0a18)
    g.fillRect(0, 0, W, H)

    // Enemy side (warm dark red)
    g.fillStyle(0x1a0808, 0.92)
    g.fillRect(0, 0, W, LY.divider)

    // Player side (cool dark blue)
    g.fillStyle(0x08081a, 0.92)
    g.fillRect(0, LY.divider, W, H - LY.divider)

    // Outer border
    g.lineStyle(2, 0xcc3333, 0.7)
    g.strokeRect(2, 2, W - 4, H - 4)

    // Divider line
    g.lineStyle(2, 0x663333, 0.6)
    g.lineBetween(8, LY.divider, W - 8, LY.divider)
  }

  // ── Enemy (demon) side ─────────────────────────────────────────────────────
  private buildDemonSide() {
    void GAME_WIDTH

    this.add.text(CX, LY.demonName, 'DEMON BARTENDER', {
      fontSize: '13px', color: '#ff7766',
      stroke: '#000', strokeThickness: 3, fontStyle: 'bold',
    }).setOrigin(0.5)

    // HP bar track
    this.add.rectangle(CX, LY.demonHPBar, BAR_W + 4, 14, 0x330000).setOrigin(0.5)
    this.demonBar    = this.add.graphics()
    this.demonHPLabel = this.add.text(CX, LY.demonHPBar, '', {
      fontSize: '9px', color: '#ffaaaa', stroke: '#000', strokeThickness: 2,
    }).setOrigin(0.5)
    this.drawBar(this.demonBar, LY.demonHPBar, this.demonHP, DEMON_MAX_HP, true)
    this.refreshLabel(this.demonHPLabel, this.demonHP, DEMON_MAX_HP)

    // Demon sprite — large, idle-down
    this.demonSprite = this.add.sprite(CX, LY.demonSprite, 'demon_bartender', 0)
    this.demonSprite.setScale(3.5)
    if (this.anims.exists('demon-idle-down')) {
      this.demonSprite.play('demon-idle-down')
    }

    // "HP" label
    this.add.text(CX - BAR_W / 2 - 2, LY.demonHPBar, 'HP', {
      fontSize: '8px', color: '#ff6666',
    }).setOrigin(1, 0.5)
  }

  // ── Player side ────────────────────────────────────────────────────────────
  private buildPlayerSide() {
    void GAME_WIDTH

    // Player sprite — large, idle-up (facing away = toward enemy, classic JRPG)
    this.playerSprite = this.add.sprite(CX, LY.playerSprite, 'char_0', 12)
    this.playerSprite.setScale(3.5)
    if (this.anims.exists('bar-idle-up')) {
      this.playerSprite.play('bar-idle-up')
    }

    // Weapon badge
    if (this.hasWeapon) {
      this.add.text(CX + 60, LY.playerSprite - 10, 'BAT', {
        fontSize: '8px', color: '#ffe566', backgroundColor: '#332200',
        padding: { x: 4, y: 2 },
      }).setOrigin(0.5)
    }

    this.add.text(CX, LY.playerName, 'PLAYER', {
      fontSize: '13px', color: '#66aaff',
      stroke: '#000', strokeThickness: 3, fontStyle: 'bold',
    }).setOrigin(0.5)

    this.add.rectangle(CX, LY.playerHPBar, BAR_W + 4, 14, 0x000033).setOrigin(0.5)
    this.playerBar    = this.add.graphics()
    this.playerHPLabel = this.add.text(CX, LY.playerHPBar, '', {
      fontSize: '9px', color: '#aaccff', stroke: '#000', strokeThickness: 2,
    }).setOrigin(0.5)
    this.drawBar(this.playerBar, LY.playerHPBar, this.playerHP, this.playerMaxHP, false)
    this.refreshLabel(this.playerHPLabel, this.playerHP, this.playerMaxHP)

    this.add.text(CX - BAR_W / 2 - 2, LY.playerHPBar, 'HP', {
      fontSize: '8px', color: '#6699ff',
    }).setOrigin(1, 0.5)
  }

  // ── Battle log ─────────────────────────────────────────────────────────────
  private buildLog() {
    const logH = LY.playerSprite - LY.log - 12
    this.add.rectangle(CX, LY.log + logH / 2, GAME_WIDTH - 16, logH, 0x000000, 0.75)
      .setOrigin(0.5)
    this.logText = this.add.text(CX, LY.log + logH / 2, '', {
      fontSize: '11px', color: '#dde0cc',
      align: 'center', wordWrap: { width: GAME_WIDTH - 32 },
      lineSpacing: 3,
    }).setOrigin(0.5)
  }

  // ── Turn label ─────────────────────────────────────────────────────────────
  private buildTurnLabel() {
    this.turnText = this.add.text(CX, LY.turnLabel, '', {
      fontSize: '10px', color: '#88ff88',
      stroke: '#000', strokeThickness: 2,
    }).setOrigin(0.5)
  }

  // ── Action buttons ─────────────────────────────────────────────────────────
  private buildButtons() {
    for (const b of this.btns) b.destroy()
    this.btns = []

    const actions: [string, () => void][] = [
      ['ATTACK', () => this.doAttack()],
      ['DEFEND', () => this.doDefend()],
      ['FLEE',   () => this.doFlee()],
    ]
    const pad   = 8
    const btnW  = Math.floor((GAME_WIDTH - pad * (actions.length + 1)) / actions.length)

    actions.forEach(([label, fn], i) => {
      const bx = pad + i * (btnW + pad) + btnW / 2
      const btn = this.add.text(bx, LY.buttons, label, {
        fontSize: '12px', color: '#ffffff',
        backgroundColor: '#1a2a3a',
        padding: { x: 0, y: 9 }, align: 'center',
        fixedWidth: btnW,
      })
        .setOrigin(0.5)
        .setInteractive({ useHandCursor: true })
        .on('pointerover', () => { if (this.state === 'player_turn') btn.setStyle({ backgroundColor: '#2a4a5a' }) })
        .on('pointerout',  () => btn.setStyle({ backgroundColor: '#1a2a3a' }))
        .on('pointerdown', () => { if (this.state === 'player_turn') fn() })
      this.btns.push(btn)
    })

    // Keyboard shortcuts: 1/2/3
    this.input.keyboard!.on('keydown-ONE',   () => { if (this.state === 'player_turn') this.doAttack() })
    this.input.keyboard!.on('keydown-TWO',   () => { if (this.state === 'player_turn') this.doDefend() })
    this.input.keyboard!.on('keydown-THREE', () => { if (this.state === 'player_turn') this.doFlee()   })
  }

  private setButtonsEnabled(on: boolean) {
    this.btns.forEach(b => b.setAlpha(on ? 1 : 0.35))
  }

  // ── HP bar drawing ─────────────────────────────────────────────────────────
  private drawBar(g: Phaser.GameObjects.Graphics, cy: number,
                  hp: number, maxHP: number, isEnemy: boolean) {
    g.clear()
    const frac   = Math.max(0, hp / maxHP)
    const fillW  = Math.floor(BAR_W * frac)
    if (fillW <= 0) return
    const col = isEnemy
      ? (frac > 0.5 ? 0xcc2222 : frac > 0.25 ? 0xdd6600 : 0xff2200)
      : (frac > 0.5 ? 0x2255cc : frac > 0.25 ? 0x44aacc : 0x0077ff)
    g.fillStyle(col)
    g.fillRect(CX - BAR_W / 2, cy - 5, fillW, 10)
  }

  private refreshLabel(t: Phaser.GameObjects.Text, hp: number, max: number) {
    t.setText(`${Math.max(0, hp)} / ${max}`)
  }

  private setLog(msg: string) { this.logText.setText(msg) }

  // ── Turn flow ──────────────────────────────────────────────────────────────
  private beginPlayerTurn() {
    this.state     = 'player_turn'
    this.defending = false
    this.turnText.setText('▼ YOUR TURN').setColor('#88ff88')
    this.setButtonsEnabled(true)
    this.setLog('Choose your action.\n[1] Attack  [2] Defend  [3] Flee')
  }

  private doAttack() {
    if (this.state !== 'player_turn') return
    this.lockTurn()

    const base  = Phaser.Math.Between(ATK_BASE.min, ATK_BASE.max)
    const bonus = this.hasWeapon ? Phaser.Math.Between(ATK_WEAPON_BONUS.min, ATK_WEAPON_BONUS.max) : 0
    const dmg   = base + bonus
    this.demonHP -= dmg

    const weapon = this.hasWeapon ? 'your bat' : 'your fist'
    this.setLog(`You swing ${weapon}!\n−${dmg} HP to the demon.`)

    // Player lunge forward
    this.tweens.add({ targets: this.playerSprite, y: this.playerSprite.y - 18, duration: 70, yoyo: true })
    // Demon shake
    this.time.delayedCall(130, () => {
      this.tweens.add({
        targets: this.demonSprite, x: CX + 10, duration: 35, yoyo: true, repeat: 3,
      })
      this.drawBar(this.demonBar, LY.demonHPBar, this.demonHP, DEMON_MAX_HP, true)
      this.refreshLabel(this.demonHPLabel, this.demonHP, DEMON_MAX_HP)
      this.time.delayedCall(350, () =>
        this.demonHP <= 0 ? this.endBattle(true) : this.beginEnemyTurn()
      )
    })
  }

  private doDefend() {
    if (this.state !== 'player_turn') return
    this.lockTurn()
    this.defending = true
    this.setLog('You brace yourself!\nDefense raised this round.')
    // Crouch tween
    this.tweens.add({ targets: this.playerSprite, y: this.playerSprite.y + 6, duration: 80, yoyo: true })
    this.time.delayedCall(600, () => this.beginEnemyTurn())
  }

  private doFlee() {
    if (this.state !== 'player_turn') return
    this.lockTurn()
    if (Math.random() < FLEE_SUCCESS_RATE) {
      this.setLog('You escaped successfully!')
      this.tweens.add({ targets: this.playerSprite, y: GAME_HEIGHT + 60, duration: 400, ease: 'Power2' })
      this.time.delayedCall(1200, () => this.exitBattle(false))
    } else {
      this.setLog('Escape blocked!\nThe demon cuts you off.')
      this.time.delayedCall(800, () => this.beginEnemyTurn())
    }
  }

  private lockTurn() {
    this.state = 'processing'
    this.setButtonsEnabled(false)
  }

  private beginEnemyTurn() {
    this.state = 'enemy_turn'
    this.turnText.setText('▲ DEMON\'S TURN').setColor('#ff7755')
    this.time.delayedCall(700, () => this.doEnemyAction())
  }

  private doEnemyAction() {
    const raw = Phaser.Math.Between(DEMON_ATK.min, DEMON_ATK.max)
    const dmg = this.defending ? Math.ceil(raw * DEFEND_MULTIPLIER) : raw
    this.playerHP -= dmg

    const shieldNote = this.defending ? '\n(Your defense reduced it!)' : ''
    this.setLog(`The demon strikes!\n−${dmg} HP to you.${shieldNote}`)

    // Demon swipe forward
    this.tweens.add({ targets: this.demonSprite, y: this.demonSprite.y + 18, duration: 70, yoyo: true })
    // Player shake
    this.time.delayedCall(130, () => {
      this.tweens.add({
        targets: this.playerSprite, x: CX - 10, duration: 35, yoyo: true, repeat: 3,
      })
      this.drawBar(this.playerBar, LY.playerHPBar, this.playerHP, this.playerMaxHP, false)
      this.refreshLabel(this.playerHPLabel, this.playerHP, this.playerMaxHP)
      this.time.delayedCall(400, () =>
        this.playerHP <= 0 ? this.endBattle(false) : this.beginPlayerTurn()
      )
    })
  }

  // ── End states ─────────────────────────────────────────────────────────────
  private endBattle(playerWon: boolean) {
    this.state = playerWon ? 'victory' : 'defeat'
    this.setButtonsEnabled(false)
    this.turnText.setVisible(false)

    if (playerWon) {
      this.setLog('VICTORY!\nThe demon bartender falls!')
      this.demonSprite.setTint(0x440000)
      this.tweens.add({ targets: this.demonSprite, alpha: 0.3, angle: 90, duration: 600 })
    } else {
      this.setLog('DEFEATED!\nYou collapse to the floor...')
      this.playerSprite.setTint(0x000044)
      this.tweens.add({ targets: this.playerSprite, alpha: 0.3, y: this.playerSprite.y + 20, duration: 500 })
    }

    this.time.delayedCall(2200, () => this.exitBattle(playerWon))
  }

  private exitBattle(playerWon: boolean) {
    const barScene = this.scene.get('BarScene')
    barScene.events.emit('battle-end', {
      won:      playerWon,
      playerHP: Math.max(1, this.playerHP),
    })
    this.scene.stop()
    this.scene.resume('BarScene')
  }
}
