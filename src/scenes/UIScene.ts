import Phaser from 'phaser'
import { DialogueSystem } from '@/systems/DialogueSystem'
import { DialogueLine } from '@/types'

export class UIScene extends Phaser.Scene {
  private dialogue!: DialogueSystem

  constructor() {
    super({ key: 'UIScene', active: false })
  }

  create() {
    this.dialogue = new DialogueSystem(this)

    // Listen for dialogue requests from WorldScene
    this.events.on('open-dialogue', (lines: DialogueLine[], onDone: () => void) => {
      this.dialogue.start(lines, onDone)
    })

    // Handle SPACE / Enter to advance dialogue from keyboard
    const advance = () => {
      if (this.dialogue.isActive()) this.dialogue.advance()
    }

    this.input.keyboard?.on('keydown-SPACE', advance)
    this.input.keyboard?.on('keydown-ENTER', advance)
  }
}
