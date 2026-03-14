-- scripts/aseprite/tiles.lua
--
-- Generates the world tile sheet as a 64×32 Aseprite file.
-- Layout: two 32×32 tiles side by side.
--   x=0  … grass tile   (tile index 0 in game)
--   x=32 … wall/stone tile (tile index 1 in game)
--
-- Usage inside Aseprite:
--   File → Scripts → Run Script → select this file
--   Exports tiles.aseprite (next to this script) and
--           public/assets/tiles.png (relative to the project root).

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

local grassBase   = rgba(0x4a, 0x7c, 0x59)
local grassDetail = rgba(0x3d, 0x6b, 0x4a)
local stoneBase   = rgba(0x7a, 0x7a, 0x7a)
local stoneDetail = rgba(0x5a, 0x5a, 0x5a)

-- ── Build sprite ─────────────────────────────────────────────────────────────

local spr = Sprite(64, 32)
spr.filename = "tiles.aseprite"

-- Separate layers per tile type and surface detail so artists can adjust
-- colours or detail patterns without redrawing everything.
local layerGrassBase   = spr.layers[1]  ; layerGrassBase.name   = "Grass – base"
local layerGrassDetail = spr:newLayer() ; layerGrassDetail.name = "Grass – detail"
local layerStoneBase   = spr:newLayer() ; layerStoneBase.name   = "Stone – base"
local layerStoneDetail = spr:newLayer() ; layerStoneDetail.name = "Stone – detail"

local function imgFor(layer)
  for _, cel in ipairs(spr.cels) do
    if cel.layer == layer then return cel.image end
  end
  return spr:newCel(layer, spr.frames[1]).image
end

local transparent = app.pixelColor.rgba(0, 0, 0, 0)

local grassBaseImg   = imgFor(layerGrassBase)
local grassDetailImg = imgFor(layerGrassDetail)
local stoneBaseImg   = imgFor(layerStoneBase)
local stoneDetailImg = imgFor(layerStoneDetail)

fillRect(grassBaseImg,   0, 0, 64, 32, transparent)
fillRect(grassDetailImg, 0, 0, 64, 32, transparent)
fillRect(stoneBaseImg,   0, 0, 64, 32, transparent)
fillRect(stoneDetailImg, 0, 0, 64, 32, transparent)

-- Grass tile (left 32×32)
fillRect(grassBaseImg,    0,  0, 32, 32, grassBase)
fillRect(grassDetailImg,  4,  8,  3,  3, grassDetail)
fillRect(grassDetailImg, 18, 20,  4,  4, grassDetail)
fillRect(grassDetailImg, 10, 25,  3,  2, grassDetail)

-- Stone/wall tile (right 32×32, offset x=32)
fillRect(stoneBaseImg,   32,  0, 32, 32, stoneBase)
fillRect(stoneDetailImg, 34,  2, 12, 12, stoneDetail)
fillRect(stoneDetailImg, 48, 16, 12, 12, stoneDetail)
fillRect(stoneDetailImg, 34, 18, 10, 10, stoneDetail)

-- ── Export ────────────────────────────────────────────────────────────────────

local scriptDir = app.fs.filePath(app.activeScript)
local assetsDir = app.fs.normalizePath(scriptDir .. "/../../public/assets")
app.fs.makeDirectory(assetsDir)

spr:saveAs(scriptDir .. "/tiles.aseprite")
spr:saveCopyAs(assetsDir .. "/tiles.png")

app.alert("tiles.aseprite + public/assets/tiles.png saved.")
