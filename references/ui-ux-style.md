# Game UI: design it like the game, not like a website

Mechanics (classes, layouts, tween APIs, input wiring) live in `ui-engineering.md`; the session flow lives
in `player-journey.md`. This file is how the screens should look, move and read, and how to check them.
Every project gets `src/client/UiKit.luau` from the template: start from it.

## What the person rejected, and why

Lily Pad Leap's first UI was called "barely a game" and then "UI design and flow overall needs to be
better". The screens it had are the catalogue of what not to ship:
- a title made like a website hero: a dark translucent rectangle on the left with small body text;
- "Menu", "Settings", "Skip tutorial" as text pills stacked in a corner;
- a tutorial prompt in a dark box at the bottom centre, between the thumbstick and the jump button;
- floating world labels for every area, visible from anywhere, cluttering every view;
- dark navy panels on some screens and cream cards on others, so nothing felt like one game;
- settings as buttons whose label is the state ("Sound off"), so a player can't tell state from action;
- modals that didn't dim what was behind them, and screens that appeared with no motion at all.
The rebuild below fixed each one; the same fixes apply to any game.

## The five rules

1. **One kit, built once, used everywhere.** Tokens (ink, cream, primary, accent, reward, danger; a
   display font and a body font; one radius, one stroke, one lip) and components (panel, button,
   icon button, pill, switch, banner, toast, big word) in one module. A screen that builds its own
   frame by hand is a bug.
2. **Every screen has one focal point and one next action.** The biggest, brightest thing on screen
   is what the player should do now. Secondary actions are smaller and quieter; a third is an icon.
3. **The world is the background, the HUD lives in corners.** Counters top-left, progress top-centre,
   pause top-right, nothing persistent in the centre or the bottom third (thumbs), transient words in
   the middle for a second at most.
4. **Everything moves a little.** Panels pop in, counters punch when they change, banners slide, the
   logo floats, buttons press down onto their lip, stars land one by one with a rising tick. Respect
   reduced motion (GuiService.ReducedMotionEnabled and an in-game switch).
5. **Look at every screen on a phone before calling it done.** `rbxgame tour` with `--device`, every
   screen on one sheet; judge it against the rubric at the bottom.

## The kit (`src/client/UiKit.luau`)

| Piece | What it is |
|---|---|
| `Kit.Theme` | colours with a darker `*Shade` for each fill, `Display` (Fredoka One) and `Body`/`BodyHeavy` (Builder Sans), `Radius` 18, `Stroke` 3, `Lip` 6, and the 1100x620 reference size |
| `Kit.screen(playerGui, name, order)` | a ScreenGui (CoreUISafeInsets) whose `Root` is scaled from the reference by one UIScale, clamped 0.6-1.35. A phone in landscape (about 844x390 pt) comes out near 0.65, so a 72-unit button is 47 pt: author at reference size and stop thinking in device pixels |
| `Kit.panel` | cream face, 3-px ink outline, faint top-to-bottom gradient, a soft ink shadow 8 units below. Returns the face; `face.Parent` is the holder to show, hide or pop |
| `Kit.button` | `style` primary (lime), secondary (cream), accent (aqua), danger (coral), reward (sun); a darker lip under the face; the face drops onto the lip on press (0.06 s), hovers to 1.04, a sun-coloured selection ring for gamepads; optional `icon` and key `hint` chip |
| `Kit.iconButton` | a square button with a drawn icon (pause, sliders, close, home, check, star, drop, clock) |
| `Kit.pill` | rounded counter with an icon badge: time, currency, collectibles |
| `Kit.switch` | a labelled row with an on/off track; the label names the setting, the track shows its state |
| `Kit.text` | text with optional ink outline; sizes above 100 (Roblox's cap) keep 100 and scale the label |
| `Kit.pop`, `Kit.punch`, `Kit.tween` | entrance (0.88 to 1 with a Back ease, 0.28 s), emphasis (scale up and settle), any tween; all skip motion when reduced |

Icons are drawn from frames (no uploads, no AI art). Add a kind to `Kit.icon` when a screen needs one;
keep them in the same weight (round ends, ink on cream or cream on ink).

## Screen recipes

- **Title.** The live world is the background (a slow camera over the level), shaded only at the top
  and bottom for legibility. A logo lockup at top centre: a small tilted ribbon with the first words
  and one huge outlined word, floating gently. One line of promise under it. One big primary button at
  bottom centre (Play; "Play again" for a returning player), a small secondary under it (How to play), a
  settings icon top-right, the player's best as a pill bottom-left once they have one. Nothing else.
- **Coach (tutorial).** A card at top centre, clear of both thumbs: a step badge (1/3), the instruction
  as a short imperative in the display font, the input hint for the player's actual device
  (`UserInputService.PreferredInput`) underneath. Skip is a small secondary beside it. A bouncing
  marker over the world target, low enough not to hide under the card. Teach by doing; one mechanic
  per step.
- **Ready / reward moments.** A panel with a badge overlapping its top edge (a star on a sun disc), a
  short celebration title, one sentence on what's next and the goals, one primary button.
- **Countdown.** Huge numbers, each in its own colour (3 coral, 2 sun, 1 aqua), punching in, then GO! in
  the primary colour with a one-line instruction. Gone within a second of the start.
- **Run HUD.** Pills top-left (time, collectibles; punch on change), a progress tracker top-centre (one
  segment per stage in the stage's colour, filling as you go, the stage name above), pause top-right.
  Stage changes get a banner: a stage-coloured ribbon with "GARDEN 2 OF 4", the name, one line, sliding
  in and out within 2.5 s. Small events ("Back to your lotus") are a toast chip under the tracker.
- **Results.** A ribbon header naming the outcome by how well it went (POND CHAMPION! for three stars),
  stars landing one at a time with a rising tick, stat tiles (time with a NEW BEST tag when beaten,
  collectibles as n/total), the goals as checks, a wide primary (play again) and a narrower secondary
  (menu, with a home icon).
- **Menu sheet and settings.** Modals dim everything behind them (a shade inside the HUD, above every
  HUD element), close on tapping outside, on B and on Esc, and give gamepad focus to their first
  control. Settings are switches with a label, plus a close icon.
- **World labels.** Only where a name helps you choose a direction, and only near it
  (`BillboardGui.MaxDistance` about 40 studs). Never a label for every object.

## Type and layout numbers (at the 1100x620 reference)

Logo word 150-190; screen titles 36-42; buttons 28-40 (primary), 22-26 (secondary); instructions 28;
body 21-23; captions 18. After the root scale, nothing interactive renders below 44 pt and no text
below 13 pt on a phone. Primary buttons 300x72-78; secondary 220x54; icon buttons 56. Keep 12-unit
margins from the safe-area edges, 16-18 between stacked controls. On touch, the bottom-left 30% x 40%
(thumbstick) and the jump button's corner stay empty during play.

## Flow and input

The server owns the phase (an attribute or a state value) and the client shows the screens for it; one
ScreenGui shows and hides groups, so there is never a frame with two screens fighting. Confirm with
Space or Enter on the focused primary, back out with B or Esc, and set `GuiService.SelectedObject` to the
primary whenever a screen with buttons appears and a gamepad is in use. A button that waits for the
server disables itself (`Interactable = false`) and shows it.

## Review: `rbxgame tour`

Write `scenarios/ui-tour.txt` (template in the project): play, click the real buttons, force any screen
the tour can't reach from the server, `shot` each one. Run it on desktop and with `--device "iPhone 1"`;
each run makes one labelled sheet. Studio's simulated clicks can miss under a simulated phone's insets,
so give the HUD a test hook (a "Modal" attribute that opens the menu or settings) and use it on the
phone tour.

Judge every screen on the sheet:
- Is there one focal point, and is it the right next action?
- Would it read on a phone held at arm's length? (Zoom into the phone capture; check the smallest text.)
- Does it look like the same game as every other screen (colours, outline, radius, fonts, icons)?
- Is anything covering the thumbs, the character or the route?
- Is there any label, panel or line of text a player wouldn't miss if it were gone? Remove it.
- Does the screen arrive and leave with motion, and does every press answer with sound and movement?
- Compare with the genre's top games' screens from `rbx-research` (their store shots): would this hold
  up next to them?

## Platform notes (still true)

- `ScreenInsets = CoreUISafeInsets` for the HUD; `None` only for full-screen shades and backdrops.
- Detect input with `UserInputService.PreferredInput`, not the device; swap hints and enlarge targets
  for Touch.
- `TextSize` stops at 100 (and `TextScaled` does too): scale the label instead (`Kit.text` does).
- Respect `GuiService.PreferredTextSize` if the game has a lot of reading.
- A `BillboardGui` inside a ScreenGui still renders in the world; keep it out from under HUD cards.

CHANGELOG
- 2026-11-03: rewritten around a design system, screen recipes and the tour review after the person
  rejected Lily Pad Leap's first two UIs; the kit and tour tool were built and tested on that game.
