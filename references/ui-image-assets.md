# Image-based game UI: make the art, slice it, ship it

Native frames (Frame + UICorner + UIStroke) can't draw a scalloped frame, a ribbon, a mascot, a drawn
icon or text with an extruded lip, and a UI made only of them was rejected twice as "drab", "ugly",
"way too much padding". The top Roblox UIs (Dress to Impress, Pet Simulator 99, Grow a Garden, Adopt Me)
are mostly images: 9-slice window frames, painted button plates, text-art titles, illustrated
backgrounds, drawn icons and a reacting mascot, with native text for anything that changes.
This file is how to make those images with `tools/uiart`, upload them and use them through `UiKit`.
Design rules for screens stay in `ui-ux-style.md`; the sauce rules (mascot, motif, moments) in `sauce.md`.

## What is an image and what stays native

| Image (make it with uiart) | Native (UiKit draws it) |
|---|---|
| Window frame, 9-slice, with the game's trim and corner ornaments | Every number, name and price that changes |
| Surface pattern inside panels, tiled at 8-12% opacity | Toggles, sliders, scroll frames |
| Button plates per style, with rest / pressed / disabled states | Rarity chips and small tags |
| Title ribbons and text-art titles; round shouts ("WHACK THE PINATA!") | Body text (16 px floor) |
| Full-screen illustrated backgrounds behind menus, shop, results | Layout, motion, sound |
| Drawn icons (one ink weight, one light), touch action buttons | Fallback for every role without art |
| Mascot poses (at least 4: e.g. panic, dizzy, cheer, smug) | |

## The numbers (measured on top games, 844x390 phone reference)

Measured from screenshots of Grow a Garden, Pet Simulator 99, Steal a Brainrot and Dress to Impress
(pixel measurements, about +-10%), then applied in the template kit and checked on phone captures of
Pinata Panic (2026-11-16):

- **Button label cap height = 50% of the button face** (measured 45-58%). `Kit.labelSize(h)` computes the
  text size from the font's cap-height ratio (`type.capHeight`; `uiart metrics "Font"` measures it).
  Vertical padding then lands at 22-25% of the height per side, as measured.
- **Side padding = 0.4 x button height** (measured 0.3-0.6). Buttons hug their content: give `height` and
  no `Size`; width = icon + gap + label + 2 x 0.4h. Only a full-width primary uses `fill = true`.
- **Heights:** primary 52, secondary 48, the 48 px target floor (above 44 pt) never shrinks. In list rows,
  keep the 48 px target and drop the label to about 45% (`TextSize` explicit) rather than widen the row.
- **Icons in buttons** 60% of the face; gap 16% of the height.
- **Button corner radius** 20% of height (10-11 px at 52), lip 5 px. Rounder reads as a pill, not a plate.
- **Windows:** 12-16 px from the frame's inner edge to content, 8-12 px gaps, under 15% empty area.
  If a window is a quarter blank, shrink it or put art in it.
- **HUD:** no plates. Currency and counters are a drawn icon (about 44 px) breaking left of an outlined
  number (26-28 px, stroke 11% of size). Side buttons are bare 50 px icons with an outlined 16 px caption.
- **Close:** 48 px drawn button over the top-right corner, a third outside the frame.
- **Title ribbon:** 50 px high, text art 32 px, centred on the top edge so it breaks the frame.
- Text on art always has an ink outline (UIStroke ~11% of size) so it reads on any colour.

## Making the art: `tools/uiart`

A spec (JSON) lists assets; uiart draws each in headless Chromium (HTML/CSS/SVG, Google Fonts, no
window), post-processes with Pillow and writes PNGs, `manifest.json` and a contact sheet:

```bash
tools/uiart render assets/ui/game.json            # -> assets/ui/game/*.png, manifest.json, sheet.jpg
tools/uiart render assets/ui/game.json --only panel,button-primary   # iterate on a few
tools/uiart metrics "Luckiest Guy"                # cap height for Kit.labelSize
```

Spec shape (`vars` are reusable with `$name`; `defaults` set per-type params and post ops):

```json
{"name": "My game UI", "scale": 2, "fonts": ["Luckiest Guy"],
 "vars": {"ink": "#2B1D4A", "pink": "#FF4FA3"},
 "assets": [
  {"name": "panel", "type": "panel", "size": [192, 192], "role": "panel",
   "params": {"rim": "$pink", "rimWidth": 11, "face": "#FFF6E6", "radius": 26, "lip": 7, "ornaments": ["#FFC93C"]}},
  {"name": "button-primary", "type": "button", "size": [112, 52], "role": "buttonPrimary",
   "params": {"fill": "$pink", "radius": 11, "lip": 5}},
  {"name": "title-shop", "type": "title", "params": {"text": "PARTY SHOP", "size": 32, "rotate": -2},
   "post": [{"op": "trim"}, {"op": "pad", "px": 2}]},
  {"name": "icon-candy", "type": "icon", "size": [56, 56], "params": {"file": "svg/candy.svg"},
   "post": [{"op": "outline", "px": 2.5, "color": "$ink"}, {"op": "shadow", "y": 3, "alpha": 0.35}]}
 ]}
```

Types: `panel` (frame; `rim`, `face`, `innerLine`, `ornaments`), `button` (plate; renders rest, pressed,
disabled), `chip`, `bar` (`kind` track or fill; draw the fill near white, the kit tints it), `ribbon`,
`badge` (starburst or round sticker with text), `bunting` (horizontal tile), `pattern` (seamless tile:
confetti, dots, stripes), `backdrop` (layers: gradient, radial, rays, bunting, scatter, balloons, hills,
image, svg, vignette), `title` (text art: outline, extruded lip, two-tone fill, optional white rim,
rotation), `icon`/`svg` (an .svg file or inline markup), `html` (anything, e.g. a plate with an
`<img>` composited on it). Sizes are design px at the 844x390 reference; `scale: 2` renders at 2x.

Post ops: `trim`, `pad`, `outline` (uniform ink weight for a whole icon set), `shadow`, `glow`, `tint`,
`opacity`, `fit`. Every output is fitted to 1024 px (Roblox's limit) and alpha-bled: transparent pixels
take their neighbours' colour so filtering never pulls a dark fringe into edges (the same fix Tarmac
and asphalt apply).

**9-slice:** frame, plate, chip, bar and ribbon templates compute their SliceCenter (corners, lip and
gloss stay fixed, the middle stretches) and record it in image pixels with `sliceScale = 1/density`, so
a 2x image draws its corners at design size. `"nine": [l, t, r, b]` (design px) overrides it. The
contact sheet shows each sliced asset stretched to 2.2x width: check corners and ornaments survive.
Edges stretch, they don't tile, so keep repeating detail (scallops, stripes) out of frame edges; put it
in a tiled pattern or the corners.

**Drawing your own art:** write SVG as code (a small Python script that emits .svg files is easiest:
shared parts, variants per pose). No AI images. Keep one ink colour, one outline weight (from the
`outline` post op), light from the top-left, a white highlight, and the game's motif (bunting, fringe).
3D renders work too: render with transparent film (`blender-kit.md`) and use them in a backdrop
`image` layer or as an icon.

Look at `sheet.jpg` after every render (Read the image), then at the real game on a phone capture.

## Upload and use in Roblox

```bash
tools/uiart upload assets/ui/game/manifest.json --ids assets/ui/ids.json            # preview: sends nothing
tools/uiart upload assets/ui/game/manifest.json --ids assets/ui/ids.json --upload   # free, expectedPrice=0
tools/uiart luau  assets/ui/game/manifest.json --ids assets/ui/ids.json --out src/shared/UiArt.luau
tools/uiart theme assets/ui/game/manifest.json --ids assets/ui/ids.json --themes ui-themes.json --theme "My Game"
tools/uitheme luau ui-themes.json --out src/shared/Themes.luau
```

Upload goes through `rbxcloud` (`open-cloud.md`): only new or changed files (by hash) are sent, ids are
kept in `ids.json`. New images show as Reviewing for a while; they rendered for the owner in Studio
right away (verified 2026-11-16). Assets with a `role` become theme art (`Themes.<name>.art`); every
asset is also in `UiArt.luau` by name.

In the client, before requiring the HUD:

```luau
Kit.configureArt(require(ReplicatedStorage.Shared.UiArt))
Kit.setTheme("My Game")
```

Then the kit uses the art wherever a role exists and falls back to native drawing where it doesn't:
`Kit.panel` (frame `panel`, `pattern` tile, `titleArt` on `ribbonArt`, `onClose` corner button),
`Kit.button` (`button<Style>`, `Pressed`, `Disabled`; content insets keep the label on the face),
`Kit.pill` (`chip`, or `bare = true` for the HUD), `Kit.bar` (`barTrack`, `barFill`), `Kit.backdrop`
(full-screen background, `dim`), `Kit.icon` (`icon-<kind>` drawn, never tinted), `Kit.closeButton`,
`Kit.art(parent, name)` for titles, mascots and anything else. Raw ImageLabel 9-slice, if you need it:

```luau
img.ScaleType = Enum.ScaleType.Slice
img.SliceCenter = Rect.new(68, 68, 316, 302) -- image px, from the manifest
img.SliceScale = 0.5                         -- 2x art drawn at design size
```

Backgrounds go on their own ScreenGui (`ScreenInsets = None`, `IgnoreGuiInset = true`) under the menus.

## Checks before calling it done

- Contact sheet: every 9-slice still clean at 2.2x; icons one weight; no white or dark fringes.
- Phone capture of every screen (`rbxgame tour ... --device "iPhone 1"`), read next to the references:
  no flat cream rectangle, no plain plate, no text-only row, no plate taller than 2x its label.
- Every element with art still works without it (unset a role and look once).

Verified 2026-11-16 on Pinata Panic: 66 assets rendered, uploaded free and used; four look-fix rounds on
phone captures through Studio on a remote PC (iPhone 11 simulator). Not verified: real-device touch
feel, gamepad focus on art buttons, very small Android screens.
