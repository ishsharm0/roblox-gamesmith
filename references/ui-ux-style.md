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

## UiKit v2: shipped phone-first specification

This replaces the older 1100x620 / shrinking-canvas guidance. Author at **844x390**. The root scale is
`clamp(min(viewportX/844, viewportY/390), 1, 2)`: larger screens scale up, smaller screens reflow at 1.
A screen must fit its panels and scroll content to the resulting root; a scale floor alone cannot
make arbitrary old fixed layouts responsive. Never solve overflow by shrinking text below 16px.

The shipped game was reviewed at a **446x441** capture viewport (the available small-phone stand-in),
with every modal checked for **16px minimum text and 48x48px minimum targets**. This proves that
viewport, not real-phone touch feel, console navigation or every aspect ratio. Run a device tour too.

| Component | Shipped anatomy / API |
|---|---|
| `Kit.Theme` | Ink #103440, cream #FFF9E8, primary lime #C4F25C, danger coral #FF7A84, info aqua #56D6CC, reward sun #FFC846, disabled #C4CABA; matching darker shades. Fredoka One display, Builder Sans Bold/ExtraBold body. Reference 844x390. |
| `Kit.screen` | Persistent ScreenGui, CoreUISafeInsets, Sibling ZIndex, one root UIScale. Returns gui/root. Default HUD order 5, modals 10, feedback 20 in the shipped game. |
| `Kit.panel` | Ink shadow at +10 / .72 transparency; cream face, radius 20, 4px ink border. Optional 52px ribbon, about 70% width, 30px display title, state-coloured aqua/sun/coral. Returns face; holder is `face.Parent`. Add a 48px close target overlapping the corner. |
| `Kit.button` | Shadow → 6px darker lip → gradient face → inset gloss → icon/content row. Radius 16, border 3. Styles primary/secondary/accent/danger/reward. Default 260x64; content icon 28 with 8px gap. `Kit.setButton` sets interactability, selection and muted state. |
| `Kit.iconButton` | 48px minimum, normally 52px; same layered face and selection ring. Keep 8–12px between targets. |
| `Kit.pill` | 44px tall, radius 22, 3px border; overlapping 36px badge and 26px icon; 24–26px display number. |
| `Kit.card` | Cream, radius 14, 3px border; 32px rarity band, 60px icon and 16px name. Usually 136px wide. Add details below, and put long collections inside a scroller. |
| `Kit.switch` | Label names the setting; 88x44 track and 36px knob show state. Whole 56px row is the target. Returns row/setter; setter does not call onChanged. |
| `Kit.text` | 16–100px clamp; fixed sizes and wrapping. Body 18, captions 16, HUD 26, titles 30–34. Scale a label explicitly if a logo needs >100. |
| `Kit.configureIcons` | Supply public image IDs by semantic name. ImageLabel tinting keeps one icon weight. No game-specific asset IDs or private paths belong in the generic kit. Frame-drawn fallbacks preserve the starter's basic icons when no map is configured. |
| `Kit.pop`, `Kit.punch`, `Kit.roll`, `Kit.tween` | Shared motion and number roll-up; honour both the in-game reduced-motion flag and GuiService.ReducedMotionEnabled. |

Use ink text on coloured fills, cream text on an ink chip. Rarity bands are grey Common #B8C0C8,
green Uncommon #6FD16B, blue Rare #4DA3FF, purple Epic #A86BFF, gold Legendary #FFC846; print the rarity
name as well. Keep credits/licences with uploaded assets and check that every image actually loads.

### Motion numbers

- Hover/focus: scale 1.04, Back, .12s. Press: face down 5px and scale .97 in .06s; release .15s Back.
- Modal: .88 → 1, Back, .28s. Counter emphasis: up to 1.25 → 1 over .3s.
- Number roll: .8s Quad Out. Merge rewards arriving within .25s into one total before rolling/toasting.
- Toast: .3s slide in, 2.2s hold, .25s out; keep each message slot's own cancellation ticket.
- Hand hint: 1.4s drag/release loop, removed on the first successful input.
- Optional stars: .35s Back landing, .25s stagger, rising pitch. Do not add stars to a game without star rules.
- Reduced motion: set final properties immediately; keep rewards and state changes visible.

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

## HUD placement and responsive layout

Inside safe insets, keep 16px edge margins: currency top-left, one progress item top-centre, pause
48px top-right. A side stack has at most four 48px icon buttons, spaced about 12px. Bottom-left and
bottom-right 30% × 40% stay clear for thumbs. A special-tool selector can sit bottom-centre; move
transient hints above it. Toasts sit below the progress bar and never cover a modal's controls.

Panels occupy roughly 60–80% of phone height with 20px padding and 12px gaps. The shipped shop uses
one readable upgrade row at a time in the small viewport instead of shrinking five rows; a book
reflows 136px cards into the available columns. Fit panel holders to `root.AbsoluteSize` and use
scrolling for content that exceeds it. On a wider screen use the room; do not stretch text lines.

## Flow and input

The server owns the phase (an attribute or a state value) and the client shows the screens for it; one
ScreenGui shows and hides groups, so there is never a frame with two screens fighting. Confirm with
Space or Enter on the focused primary, back out with B or Esc, and set `GuiService.SelectedObject` to the
first enabled control (or Close when purchases are disabled) whenever a screen with buttons appears and a gamepad is in use. A button that waits for the
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
- `TextSize` stops at 100 (and `TextScaled` does too): use an explicit UIScale for larger logo text.
- Respect `GuiService.PreferredTextSize` if the game has a lot of reading.
- A `BillboardGui` inside a ScreenGui still renders in the world; keep it out from under HUD cards.

CHANGELOG
- 2026-11-03: rewritten around a design system, screen recipes and the tour review after the person
  rejected Lily Pad Leap's first two UIs; the kit and tour tool were built and tested on that game.

- 2026-11-14: UiKit v2 ported from the shipped toy-siege UI: 844x390 authoring, scale-up/reflow, 16px text / 48px target floors, layered buttons, ribbon panels, image icon configuration, rarity cards, settings switches and reward motion. Small-viewport captures and runtime floor checks reviewed; physical-device play remains a separate check.
