export interface DialogueLine {
  speaker: string
  text: string
}

export interface NPCData {
  id: string
  name: string
  x: number
  y: number
  dialogue: DialogueLine[]
}

export interface PlayerState {
  x: number
  y: number
  facing: 'up' | 'down' | 'left' | 'right'
}
