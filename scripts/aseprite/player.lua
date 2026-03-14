-- scripts/aseprite/player.lua
--
-- Generates the player sprite sheet as a 48×64 Aseprite file.
-- Layout: 3 columns (idle, walk-1, walk-2) × 4 rows (down, up, left, right)
-- Each cell is 16×16 px.
--
-- Usage inside Aseprite:
--   File → Scripts → Run Script → select this file
--   Exports player.aseprite (next to this script) and
--           public/assets/player.png (relative to the project root).

-- ── Helpers ──────────────────────────────────────────────────────────────────

local function fillRect(img, x, y, w, h, color)
  for py = y, y + h - 1 do
    for px = x, x + w - 1 do
      if px >= 0 and py >= 0 and px < img.width and py < img.height then
        img:putPixel(px, py, color)
      end
    end
  end
end

local function rgba(r, g, b)
  return app.pixelColor.rgba(r, g, b, 255)
end

-- ── Palette ───────────────────────────────────────────────────────────────────

local transparent  = app.pixelColor.rgba(0, 0, 0, 0)

-- Body colour per direction row (down, up, left, right)
local dirColors = {
  rgba(0x4a, 0x9a, 0xde),  -- down  (row 0)
  rgba(0x3a, 0x7a, 0xbf),  -- up    (row 1)
  rgba(0x2a, 0x5a, 0x9f),  -- left  (row 2)
  rgba(0x5a, 0xb0, 0xee),  -- right (row 3)
}
local skinColor = rgba(0xf4, 0xc2, 0xa1)  -- head / skin
local legsColor = rgba(0x2d, 0x5a, 0x8e)  -- legs

-- ── Build sprite ─────────────────────────────────────────────────────────────

-- Single-frame 48×64 canvas — the full sprite-sheet grid
local spr = Sprite(48, 64)
spr.filename = "player.aseprite"

-- Rename the default layer and add two more so artists can edit each part
-- independently without touching the others.
local layerLegs = spr.layers[1]
layerLegs.name = "Legs"

local layerBody = spr:newLayer()
layerBody.name = "Body"

local layerHead = spr:newLayer()
layerHead.name = "Head"

-- Retrieve (or create) the image for a layer on frame 1
local function imgFor(layer)
  for _, cel in ipairs(spr.cels) do
    if cel.layer == layer then return cel.image end
  end
  return spr:newCel(layer, spr.frames[1]).image
end

local headImg = imgFor(layerHead)
local bodyImg = imgFor(layerBody)
local legsImg = imgFor(layerLegs)

-- Start transparent
fillRect(headImg, 0, 0, 48, 64, transparent)
fillRect(bodyImg, 0, 0, 48, 64, transparent)
fillRect(legsImg, 0, 0, 48, 64, transparent)

-- Paint all 12 cells
for row = 0, 3 do
  local bodyColor = dirColors[row + 1]
  for col = 0, 2 do
    local x = col * 16
    local y = row * 16

    -- Body (8×9 px, offset 4 px from left, 5 from top of cell)
    fillRect(bodyImg, x + 4, y + 5, 8, 9, bodyColor)

    -- Head (6×5 px, centred horizontally in cell)
    fillRect(headImg, x + 5, y + 1, 6, 5, skinColor)

    -- Legs: col 0 = idle (symmetric), col 1 = stride left, col 2 = stride right
    local legOff = col == 1 and -1 or (col == 2 and 1 or 0)
    fillRect(legsImg, x + 4, y + 12, 3, 3 + legOff, legsColor)
    fillRect(legsImg, x + 9, y + 12, 3, 3 - legOff, legsColor)
  end
end

-- ── Export ────────────────────────────────────────────────────────────────────

local scriptDir  = app.fs.filePath(app.activeScript)
local assetsDir  = app.fs.normalizePath(scriptDir .. "/../../public/assets")
app.fs.makeDirectory(assetsDir)

-- Save editable source next to this script
spr:saveAs(scriptDir .. "/player.aseprite")

-- Export flat PNG for the game to load
spr:saveCopyAs(assetsDir .. "/player.png")

app.alert("player.aseprite + public/assets/player.png saved.")
