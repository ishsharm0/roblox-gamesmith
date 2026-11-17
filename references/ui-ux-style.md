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

## Images first, and content-led buttons (2026-11-16 verdict)

"UI is still kinda ugly ... needs to be a lot better with background images, way too much padding for a
lot of buttons, use more images." Native frames alone were rejected. Make the frames, plates, titles,
icons, backgrounds and mascot as images with `tools/uiart` and let the kit use them:
`references/ui-image-assets.md`. Button numbers (they replace the 260x64 default below): label cap height
50% of the face, side padding 0.4 x height, primary 52 / secondary 48 high, width hugs the content.
HUD counters are a drawn icon + outlined number with no plate.

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
`clamp(min(viewportX/refX, viewportY/refY), 1, 1.5)` with ref 844x390 for touch and 1280x640 for mouse and
keyboard (`Canvas.fit`): a phone layout magnified to fill a laptop reads as "huge" (owner verdict, 2026-11-17).
Larger screens scale up a little, smaller screens reflow at 1.
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
| `Kit.button` | Image plate (theme art `button<Style>`, pressed, disabled) or native: shadow → lip → gradient face → gloss → icon/content row. Without `Size` it hugs its content: `height` (52 default), label cap 50% of the face (`Kit.labelSize`), side padding 0.4 x height, icon 60% of the face; `fill = true` for a full-width primary; an explicit `Size` keeps a fixed box. `Kit.setButton` sets interactability, selection and muted state. |
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

## Themes: a bespoke kit is a set of tokens, not new components

Components never name a colour; they ask for a role (`primary`, `surface`, `outline`, `onPrimary`,
rarity colours). A theme is only tokens: colour roles, shape (radius, button radius, stroke, lip,
shadow, gradient, title style `tab` / `banner` / `plain`, glow), type (display, body and button
families bundled with Roblox or available as public font assets, title case, text stroke) and motion (pop scale, time, easing,
press scale). Seven starting themes live in `templates/project/ui-themes.json`
(previews: `docs/images/ui-themes-1.jpg`, `ui-themes-2.jpg`):

| Theme | For |
|---|---|
| Toybox | toy, physics and party games: cream panels, ink outline, chunky lips |
| Bubblegum | simulators, pets, collecting: saturated blue panels, outlined white text |
| Garden | farming, cosy plots, cooking: parchment, brown outline, leaf green and wood |
| Night Arcade | night obbies, rhythm, sci-fi, tycoons: navy, thin neon outline with glow |
| Cozy | pets, dress-up, roleplay: white, no outline, soft shadow, pastels |
| Royal | RPG, dungeons, tower defence: slate, gold rule, blackletter titles only |
| Clean | towns, social hangouts: white, flat, one blue |

Making one for a new game (do this before any screen is built, after STYLE.md from `visual-craft.md`):

1. `tools/uitheme new "<Game>" --from <nearest theme>` copies a theme into the JSON.
2. Change tokens to match the game's style bible: the sacred colour becomes `primary` or `accent`,
   the shape motif sets radius and title style, the world colours set `world`.
3. `tools/uitheme sheet --only "<Game>" --out shots/ui-theme` renders the HUD, a shop with rarity cards
   and a result modal at the 844x390 phone reference. Look at it at phone size. Check: every text is
   legible (16 px floor), the primary button is the loudest thing on each screen, rarity colours are
   distinct from the primary, decorative display fonts are used for titles only (`type.button` sets a
   readable button font, as Royal does).
4. `tools/uitheme luau --out src/shared/Themes.luau` writes the tokens for the Luau kit.
5. Prefer Roblox's 2026 `UIShadow` (drop, inset for pressed, text shadow) and per-corner radii over
   stacked frames for lips and shadows (see `visual-craft.md` section 3).

The template loads the generated module automatically and defaults to Toybox. Select the game's theme
in the client entry point **before requiring the HUD** (the HUD builds as it is required):

```luau
local Kit = require(script.Parent.UiKit)
Kit.setTheme("Royal")
local Hud = require(script.Parent.Hud)
```

`setTheme` also refreshes existing kit components. Unknown names raise an error without switching.
For a one-game variation, prefer editing its JSON theme and regenerating; for a runtime preference,
pass partial token groups as the second argument. These use Luau values, including `Color3` and `Font`:

```luau
Kit.setTheme("Toybox", {
    color = { primary = Color3.fromRGB(180, 230, 75) },
    shape = { lip = 4 },
    motion = { popFrom = 0.94, popTime = 0.18, ease = "Quad", press = 0.97 },
})
Kit.reducedMotion = true -- also respects Roblox's ReducedMotionEnabled
```

Overrides merge with that named theme; each call starts fresh and never edits the generated tables.
Keep fill/shade/on-colour roles together when changing contrast. Explicit component props such as
`panel.color`, `panel.headerColor`, `text.FontFace`, `text.TextColor3`, `button.lip`, and `card.color`
win over tokens. `Kit.tokens` exposes the current groups; `Kit.Theme` retains the old aliases
(`Cream`, `Ink`, `Lime`, `Display`, `Ref`, etc.) in the same table for existing callers. Colours copied
into game-owned instances remain the game's responsibility when switching at runtime.

`Kit.button` accepts `primary`, `secondary`, `danger`, `accent`, `neutral`, and the legacy `reward`
(alias of `accent`). `Kit.setButton` preserves the disabled role across switches. `Kit.rarityCard`
(and `Kit.card`) accepts `rarity`, `icon`, `text`, `subtitle`, optional `price`, `enabled`, and
`onActivated`. `Kit.scrim` and `Kit.toast` use their respective colour roles. Panel titles follow
`shape.title`: a coloured tab, a title-band banner, or plain text inside the panel.
`Kit.corner(radius, { TopLeftRadius = 0 })` optionally overrides individual corners on supported builds.

To reproduce the preview, run `scenarios/ui-themes.luau` in Studio's **Client** context during Play
(with other game HUDs hidden by the scenario). It first checks live switching, overrides, disabled
states, native text shadows, scale compensation, and the text/target floors, then builds the three
844x390 screens. Change the `ThemePreview` ScreenGui's `Theme` attribute to `Toybox`, `Night Arcade`,
`Cozy`, or `Royal`, and `Screen` to `HUD`, `Shop`, or `Result`; capture with `studio shot`.
The scenario uses drawn fallback icons; production games should still call `configureIcons`.
Native UIShadow capability is detected at runtime, with the old-build approximation isolated in
`templates/project/src/client/UiShadow.luau`. Blur, offsets and spread account for ancestor UIScales.

Font correction (verified against the Studio 0.747 content families and Roblox's public font-family
JSON): the earlier boards used browser-only Titan One / Bungee names. Bubblegum now uses the bundled
Fredoka One; Night Arcade uses Roblox's [Bungee Inline font](https://create.roblox.com/store/asset/12187370000/)
through its public font-family asset ID. The generator and HTML sheet use these same corrected names;
no nonexistent local `Bungee.json` or `TitanOne.json` is emitted. Royal exports ExtraBold for its
800-weight title and a separate readable Nunito button font.

`type.displayScale` / `type.buttonScale` are optional Roblox font-metric corrections (default 1),
not layout scaling; the HTML preview already uses browser font metrics. Royal's bundled blackletter
needs `displayScale = 1.5` to match the preview's visible title size. Its Nunito buttons stay at 1.

Verified 2026-11-15 on Studio 0.747: the Client scenario passed live theme/override/disabled-state,
text-shadow, UIScale and reduced-motion counter assertions. Reviewed 12 actual 844x390 captures
(HUD, shop, result/settings for Toybox, Night Arcade, Cozy, Royal) against `tools/uitheme sheet`;
corrected modal layering, action positions and native font metrics. Each screen also passed the
16px text / 48px target / on-screen action / <=100 enabled shadow audit. A separate real input
probe verified native Inset press, token press scale, lip restoration on release, and the pressed
appearance. Captures remain external to the repository. The older-build fallback was not exercised.

## From the YouTube study (November 2026)

Techniques taken from 21 studied talks and devlogs on Roblox design, retention, loops, UI, monetisation and fun.

- Currency has a plus button. A failed purchase for lack of currency opens the shop on the third attempt (cap 5 per session).
- Products sit on the route players walk, not beside the free version; HUD shop icon is one tap.
- A help icon in the top corner opens a one-screen recap; every system has one NPC that explains it.
- Onboarding ends with a congratulation, a new unlock and the next goal on the HUD; prompts do not vanish silently.

## From the YouTube study, batch 2 (November 2026)

From 48 further talks and devlogs (69 studied in total).

- Icons: show a friend the icon; if they guess the meaning it passes.
- Cross-platform: design gamepad first; touch hit targets and text readable at phone size (about 60% of minutes).
- Dark box or vignette behind HUD values so they read over any scene.
- Shop: main item largest and first, big art, short text, green price button with currency icon.

## From the YouTube study, batch 3 (November 2026)

From 51 further talks and devlogs (120 studied in total, 20 per topic).

- Physical sizes (mobile): touch target 10-15 mm with padding, body about 16-17 pt, captions not under 12 pt; key actions in the thumb zone; add a skip or an experience question to tutorials.
- UI motion goals: responsiveness, intention, awareness, consistency, physical intuition; polish cannot rescue a design that does not work.
- Tutorial art stays plain: pretty art with text lost players in a health-regen tutorial until the art was simplified and the text cut.
- Haptics only with a visual or audio partner. Leave room for two lines in item names (pseudo-localise to test).
- Inventory is a task menu: reduce swapping (always-open inventory, quick wheel), group items by how they are used, slow or pause time when open in combat on purpose.
