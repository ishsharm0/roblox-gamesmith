# UI engineering: the plumbing under the design

`ui-ux-style.md` says what screens should look like and how they flow. This file is how to build them
so they work on a phone, a TV and a 4K monitor without breaking. Build with `src/client/UiKit.luau`
from the project template; it already does most of this.

## One reference size, one scale

Lay everything out in offset pixels on a fixed reference canvas (the kit uses 1100x620), then scale
the whole root with one `UIScale`:

```lua
local function fit()
	local v = workspace.CurrentCamera.ViewportSize
	scale.Scale = math.clamp(math.min(v.X / 1100, v.Y / 620), 0.6, 1.35)
end
workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(fit)
fit()
```

This beats a mix of scale and offset sizes: proportions stay as designed, text grows with its boxes,
and there is one number to reason about. Use `Scale` sizing only for full-screen layers (dimmers,
backdrops).

## ScreenGui settings

- `ResetOnSpawn = false` on every ScreenGui you create from code; otherwise it is destroyed and
  rebuilt each time the character respawns, along with its state.
- `IgnoreGuiInset`: true for full-bleed backgrounds; false (or a safe-area frame) for interactive UI.
- `ScreenInsets = DeviceSafeInsets` keeps buttons out of the notch and home bar; full-bleed art uses
  `None`.
- `DisplayOrder` sets which ScreenGui draws on top. Assign them in one place (backdrop 4, HUD 5, modals
  10, toasts 20) rather than tweaking ad hoc.
- `ZIndexBehavior = Sibling` (default for new guis) so children draw above parents predictably.

## Layout objects

- `UIListLayout` with `Padding` for rows and columns; `UIGridLayout` for inventories (set `CellSize`
  in offsets and let UIScale do the rest); `UIPadding` instead of nudging positions.
- `AutomaticSize` for containers that wrap text; set a max with `UISizeConstraint`.
- `UIAspectRatioConstraint` on icons and cards that must not stretch.
- `AnchorPoint = Vector2.new(0.5, 0.5)` and `Position = UDim2.fromScale(0.5, 0.5)` to centre; pop
  animations then scale from the middle.

## Text

- `TextSize` and `TextScaled` both cap at 100. For a big title, set 100 and scale the label (or its
  parent) with a `UIScale`.
- Avoid `TextScaled` on body text: neighbouring labels end up at different sizes. Use fixed sizes on
  the reference canvas.
- Fonts via `Font.new("rbxasset://fonts/families/...json", weight)`; one display face and one body face
  per game.
- `RichText = true` for inline emphasis; escape player text (`<`, `>`, `&`) before inserting it.
- Player-entered text shown to others is filtered on the server (`TextService:FilterStringAsync`).

## Input

- Buttons are `TextButton` / `ImageButton` with `Activated` (works for mouse, touch and gamepad), not
  `MouseButton1Click`.
- Touch targets at least 44 px on the device after scaling: on a phone at UIScale 0.6, that is 74 px
  on the reference canvas.
- Gamepad: set `Selectable` on buttons, `GuiService.SelectedObject` when a modal opens, and make sure
  every screen can be left with B.
- `UserInputService.PreferredInput` (Touch / Gamepad / KeyboardAndMouse) to swap prompts ("Space" vs
  "A" vs a button).
- `ContextActionService:BindAction` for gameplay verbs; it creates the mobile touch button for you.
  Resize and reposition it with `GetButton` so thumbs reach it.
- Modals sink input: a full-screen transparent `TextButton` behind a modal stops clicks reaching the
  world.

## World-space UI

- `BillboardGui` for labels over characters and objects; parent client-created ones to the camera or
  a client folder in Workspace (one under PlayerGui doesn't render in captures). `AlwaysOnTop` only
  for markers that must show through walls.
- `SurfaceGui` for signs; set `PixelsPerStud` (about 50) and `SizingMode = PixelsPerStud` so text
  stays crisp.
- Use `MaxDistance` so far labels disappear instead of turning into clutter.

## Motion

- Tween `Size` / `Position` / `Transparency` with `TweenService`; a 0.18-0.3 s Back-out pop on
  open, 0.12 s on close. Respect a reduced-motion setting by skipping straight to the end state.
- Don't tween `TextSize` (it re-rasterises every step); scale a `UIScale` instead.
- Number counters: tween a NumberValue and write `math.floor(v)` on `Changed`.

## Performance

- Build screens once and toggle `Enabled` / `Visible`; don't destroy and rebuild on every open.
- Many frequently changing labels (damage numbers, timers): pool them.
- `ClipsDescendants` and `UIGradient` / `UIStroke` cost something on low-end phones; use them on few
  elements.
- Check with the device simulator (`rbxgame tour ... --device "iPhone 1"`) every time a screen
  changes; most UI bugs only show on small screens.
