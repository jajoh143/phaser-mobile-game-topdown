import { NPCData } from '@/types'

export const NPC_DATA: NPCData[] = [
  {
    id: 'elder',
    name: 'Village Elder',
    x: 200,
    y: 180,
    dialogue: [
      {
        speaker: 'Village Elder',
        text: 'Ah, a traveler! Welcome to our humble village. These lands have grown dangerous of late...',
      },
      {
        speaker: 'Village Elder',
        text: 'Strange creatures have been spotted near the eastern forest. You look capable — perhaps you could investigate?',
      },
      {
        speaker: 'Village Elder',
        text: 'Come speak to me again when you have learned more. Safe travels.',
      },
    ],
  },
  {
    id: 'merchant',
    name: 'Merchant',
    x: 100,
    y: 300,
    dialogue: [
      {
        speaker: 'Merchant',
        text: 'Step right up! I have wares from across the realm — potions, tools, maps!',
      },
      {
        speaker: 'Merchant',
        text: "...Well, I *had* them. My supply cart was overturned by those creatures everyone's talking about.",
      },
      {
        speaker: 'Merchant',
        text: 'If you recover my goods, I can offer you a fine discount. The cart was near the old mill.',
      },
    ],
  },
  {
    id: 'child',
    name: 'Young Scout',
    x: 300,
    y: 350,
    dialogue: [
      {
        speaker: 'Young Scout',
        text: 'Hey! I saw the creatures! They went into the cave past the river — I barely got away!',
      },
      {
        speaker: 'Young Scout',
        text: 'Mama says I shouldn\'t have gone. But I got a good look at them. Big eyes, mossy skin.',
      },
    ],
  },
]
