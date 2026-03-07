import Phaser from 'phaser'
import { DialogueLine } from '@/types'

type DoneCallback = () => void

export class DialogueSystem {
  private scene: Phaser.Scene
  private container!: Phaser.GameObjects.Container
  private bg!: Phaser.GameObjects.Rectangle
  private speakerText!: Phaser.GameObjects.Text
  private bodyText!: Phaser.GameObjects.Text
  private nextHint!: Phaser.GameObjects.Text

  private lines: DialogueLine[] = []
  private index = 0
  private onDone: DoneCallback | null = null
  private active = false

  // Typewriter state
  private fullText = ''
  private charIndex = 0
  private typeTimer: Phaser.Time.TimerEvent | null = null
  private isTyping = false

  constructor(scene: Phaser.Scene) {
    this.scene = scene
    this.buildUI()
  }

  private buildUI() {
    const { width, height } = this.scene.cameras.main
    const boxH = 140
    const pad = 12

    this.bg = this.scene.add
      .rectangle(0, 0, width - 16, boxH, 0x1a1a2e, 0.92)
      .setOrigin(0, 0)
      .setStrokeStyle(2, 0x4a9ade)

    this.speakerText = this.scene.add.text(pad, pad, '', {
      fontSize: '13px',
      color: '#4a9ade',
      fontStyle: 'bold',
    })

    this.bodyText = this.scene.add.text(pad, pad + 22, '', {
      fontSize: '12px',
      color: '#e0e0e0',
      wordWrap: { width: width - 16 - pad * 2 },
      lineSpacing: 4,
    })

    this.nextHint = this.scene.add.text(
      width - 16 - pad,
      boxH - pad - 2,
      '▶ Tap',
      { fontSize: '11px', color: '#888888' },
    ).setOrigin(1, 1)

    this.container = this.scene.add.container(8, height - boxH - 8, [
      this.bg,
      this.speakerText,
      this.bodyText,
      this.nextHint,
    ])

    this.container.setDepth(100)
    this.container.setVisible(false)
    // Make container interactive so taps advance dialogue
    this.bg.setInteractive()
    this.bg.on('pointerdown', () => this.advance())
  }

  start(lines: DialogueLine[], onDone: DoneCallback) {
    this.lines = lines
    this.index = 0
    this.onDone = onDone
    this.active = true
    this.container.setVisible(true)
    this.showLine(this.lines[0])
  }

  private showLine(line: DialogueLine) {
    this.speakerText.setText(line.speaker)
    this.fullText = line.text
    this.charIndex = 0
    this.bodyText.setText('')
    this.isTyping = true
    this.nextHint.setVisible(false)

    if (this.typeTimer) this.typeTimer.destroy()
    this.typeTimer = this.scene.time.addEvent({
      delay: 28,
      callback: this.typeChar,
      callbackScope: this,
      repeat: this.fullText.length - 1,
    })
  }

  private typeChar() {
    this.charIndex++
    this.bodyText.setText(this.fullText.substring(0, this.charIndex))
    if (this.charIndex >= this.fullText.length) {
      this.isTyping = false
      this.nextHint.setVisible(true)
    }
  }

  advance() {
    if (!this.active) return

    if (this.isTyping) {
      // Skip typewriter — show full text immediately
      if (this.typeTimer) this.typeTimer.destroy()
      this.bodyText.setText(this.fullText)
      this.isTyping = false
      this.nextHint.setVisible(true)
      return
    }

    this.index++
    if (this.index < this.lines.length) {
      this.showLine(this.lines[this.index])
    } else {
      this.close()
    }
  }

  private close() {
    this.container.setVisible(false)
    this.active = false
    this.onDone?.()
  }

  isActive() {
    return this.active
  }
}
