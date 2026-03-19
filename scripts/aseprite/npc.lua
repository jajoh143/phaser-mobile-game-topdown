-- scripts/aseprite/npc.lua
--
-- Generates the NPC sprite as a 16×16 Aseprite file.
-- A floating "!" indicator is on its own layer so you can toggle it
-- independently (the game renders its own animated text indicator on top).
--
-- Usage inside Aseprite:
--   File → Scripts → Run Script → select this file
--   Exports npc.aseprite (next to this script) and
--           public/assets/npc.png (relative to the project root).

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
local bodyColor    = rgba(0xe0, 0x7b, 0x3a)
local skinColor    = rgba(0xf4, 0xd0, 0xa1)
local legsColor    = rgba(0x8b, 0x45, 0x13)
local indicatorCol = rgba(0xff, 0xff, 0x00)

-- ── Build sprite ─────────────────────────────────────────────────────────────

local spr = Sprite(16, 16)
spr.filename = "npc.aseprite"

local layerLegs      = spr.layers[1]  ; layerLegs.name      = "Legs"
local layerBody      = spr:newLayer() ; layerBody.name      = "Body"
local layerHead      = spr:newLayer() ; layerHead.name      = "Head"
local layerIndicator = spr:newLayer() ; layerIndicator.name = "Indicator (unused in-game)"

local function imgFor(layer)
  for _, cel in ipairs(spr.cels) do
    if cel.layer == layer then return cel.image end
  end
  return spr:newCel(layer, spr.frames[1]).image
end

local legsImg      = imgFor(layerLegs)
local bodyImg      = imgFor(layerBody)
local headImg      = imgFor(layerHead)
local indicatorImg = imgFor(layerIndicator)

-- Start transparent
fillRect(legsImg,      0, 0, 16, 16, transparent)
fillRect(bodyImg,      0, 0, 16, 16, transparent)
fillRect(headImg,      0, 0, 16, 16, transparent)
fillRect(indicatorImg, 0, 0, 16, 16, transparent)

-- Body (8×9 px)
fillRect(bodyImg, 4, 5, 8, 9, bodyColor)
-- Head (6×5 px)
fillRect(headImg, 5, 1, 6, 5, skinColor)
-- Legs (symmetric — NPC does not walk)
fillRect(legsImg, 4, 12, 3, 3, legsColor)
fillRect(legsImg, 9, 12, 3, 3, legsColor)

-- Indicator: stem at y=-4 (only y=0 is within bounds), dot at y=2-3.
-- The real animated "!" is a Phaser Text object in NPC.ts; this layer is
-- just a pixel-art reference for the sprite sheet.
fillRect(indicatorImg, 7, -4, 2, 5, indicatorCol)  -- stem (clips to y=0)
fillRect(indicatorImg, 7,  2, 2, 2, indicatorCol)  -- dot

-- ── Export ────────────────────────────────────────────────────────────────────

local scriptDir = app.fs.filePath(app.activeScript)
local assetsDir = app.fs.normalizePath(scriptDir .. "/../../public/assets")
app.fs.makeDirectory(assetsDir)

spr:saveAs(scriptDir .. "/npc.aseprite")
spr:saveCopyAs(assetsDir .. "/npc.png")

app.alert("npc.aseprite + public/assets/npc.png saved.")
