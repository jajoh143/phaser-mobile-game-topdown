/**
 * Inventory — 4-slot weapon inventory system.
 *
 * Weapons are referenced by name (matching the keys in generate_weapon.py and
 * the weapon_<name>.png filenames exported to public/assets/sprites/).
 */

export const INVENTORY_SIZE = 4

export class Inventory {
  private slots: (string | null)[]
  private activeSlot: number

  constructor() {
    this.slots      = new Array(INVENTORY_SIZE).fill(null)
    this.activeSlot = 0
  }

  /** Add a weapon to the first empty slot. Returns the slot index, or -1 if full. */
  add(weapon: string): number {
    // Don't add duplicates
    if (this.slots.includes(weapon)) return this.slots.indexOf(weapon)

    const idx = this.slots.indexOf(null)
    if (idx === -1) return -1

    this.slots[idx] = weapon

    // Auto-equip if this is the first pickup
    if (this.slots.filter(s => s !== null).length === 1) {
      this.activeSlot = idx
    }

    return idx
  }

  /** Remove a weapon by name. */
  remove(weapon: string): void {
    const idx = this.slots.indexOf(weapon)
    if (idx === -1) return

    this.slots[idx] = null

    // If we just removed the active weapon, move to the next available
    if (this.activeSlot === idx) {
      this.activeSlot = this._nextOccupied(idx)
    }
  }

  /** Get the name of the currently equipped weapon, or null if no weapon. */
  get active(): string | null {
    return this.slots[this.activeSlot] ?? null
  }

  /** Select a slot directly (0-3). No-op if slot is empty. */
  selectSlot(slot: number): void {
    if (slot < 0 || slot >= INVENTORY_SIZE) return
    if (this.slots[slot] === null) return
    this.activeSlot = slot
  }

  /** Cycle to the next occupied slot. */
  cycleNext(): void {
    this.activeSlot = this._nextOccupied(this.activeSlot)
  }

  /** Cycle to the previous occupied slot. */
  cyclePrev(): void {
    this.activeSlot = this._prevOccupied(this.activeSlot)
  }

  /** Read-only snapshot of all slots for HUD rendering. */
  get snapshot(): ReadonlyArray<string | null> {
    return this.slots
  }

  get activeIndex(): number {
    return this.activeSlot
  }

  get isFull(): boolean {
    return !this.slots.includes(null)
  }

  get isEmpty(): boolean {
    return this.slots.every(s => s === null)
  }

  private _nextOccupied(from: number): number {
    for (let i = 1; i <= INVENTORY_SIZE; i++) {
      const idx = (from + i) % INVENTORY_SIZE
      if (this.slots[idx] !== null) return idx
    }
    return from
  }

  private _prevOccupied(from: number): number {
    for (let i = 1; i <= INVENTORY_SIZE; i++) {
      const idx = (from - i + INVENTORY_SIZE) % INVENTORY_SIZE
      if (this.slots[idx] !== null) return idx
    }
    return from
  }
}
