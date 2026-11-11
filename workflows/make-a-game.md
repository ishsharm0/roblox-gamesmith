# Make a game, end to end

Read `references/creative-quality.md` before choosing the concept and `references/geometry-quality.md`
before building any hero or world asset. The numbers below are the defaults; change one only for a
reason the genre gives you, and write the reason in CONCEPT.md.

The order matters: fun before pretty, pretty before features, and a capture before every claim. Each
stage ends with something you looked at, not something you wrote.

## 0. The bar, in the project before anything else

Run `rbxgame doctor` first; fix every MISS line before building.

Write the bar into `CONCEPT.md` (it survives context compaction; your memory of this file does not):
- one pitch sentence a 12-year-old would repeat to a friend;
- spawn to fun in under 30 seconds with no text to read: the first thing in view is the thing to do;
- a world that looks made on purpose: a style, a palette, lighting set for the mood, landmarks, no
  default grey baseplate, no studs-on-everything, no free-model soup;
- every player action answered within 100 ms with sound, motion and a number or effect;
- it works and reads on a phone (thumb zones, 375-pt-wide screens, touch controls) and on a gamepad;
- the server owns the rules; data saves; nothing breaks when a player leaves mid-action;
- monetization a player would call fair (cosmetics, convenience, never pay-to-win).

## 1. Research (about 15 minutes): `references/research.md`

`rbx-research` on the genre's charts and 3-5 comparables (numbers, passes and prices, screenshots),
`yt-research` on one or two gameplay videos each (first-minute frames and transcript). Write what they
share (the genre's floor), what the best one does that the others don't, and the twist this game adds.
Take structure, never names, art or text.

## 2. CONCEPT.md

Fill every section of the template: core loop at 30 seconds, session goals at 5 minutes, progression
over a week, social hooks, monetization, art direction with 3 reference screenshots from the research
folder, and the scope of the first playable (one area, the core loop, one progression step). If the
person gave a vague request, choose the strongest of three concepts yourself and name the other two in
one line.

## 2a. SESSION.md and visual direction — required

Read references/player-journey.md and references/visual-review.md. Write the actual first-session
state map, returning-player path and visible beat-by-beat experience. Record the user's art direction,
reference imagery, palette, asset language and arrival/play/payoff compositions. Prototype arrival,
one taught mechanic, one earned success, a failure recovery and a finish/replay before expanding.
An intro must establish the world, goal and a clear way to play; use a title scene, walkable arrival
or short sequence as the genre warrants. Tutorial steps must respond to real actions and completion
must persist. Do not force repeat tutorials on returning players.

## 3. Scaffold and greybox

`rbxgame new <dir> --name "<Name>"` copies a small playable game (title, rounds, results, saving, sounds, bot hook, scenarios): read its `STARTER.md` and replace its placeholder verb and arena before adding systems. Then `cd <dir>`, `rbxgame open`. Build the play space from code: one ModuleScript
per area in `src/server/World/` with a `Build(parent)` that clears and rebuilds its own folder (idempotent,
yields between chunks). Run it in Studio with `rbxgame push` then `studio luau` (`require(game.
ServerScriptService.Server.World.<Area>).Build(workspace.Map)`), look, adjust, run again. Terrain is not
in `workspace.Map`, so a terrain builder also runs from the server's startup when the terrain is empty.
(`build/` is Rojo's output folder; keep nothing hand-made in it.) Greybox first: blocks at the
real scale (a character is 5 studs tall, jumps 7.2 studs up and about 12 across at default settings).
`rbxgame save` writes the world to `world/Map.rbxm`; do it after every build step.

## 4. Core loop, then playtest it

Write the systems in `src/` (server rules in `src/server`, client feel in `src/client`, shared config in
`src/shared/Config.luau`); `rbxgame push` hot-reloads them. Look up every API you haven't used in this
project with `rbxdocs api <Class>[.Member]` before writing it (parameters, yields, security,
deprecation); pure rules go in `src/shared` with a Lune test in `tests/`. Write `scenarios/*.luau` that play the loop
on the server (move the character with `character_navigation` or by setting its position, fire the
prompts, check the currency, the stage, the data) and return a short report; `rbxgame test` runs one
and prints the console. Fix until a scenario walks the whole first session with no errors in the console.

## 4b. Mechanics and fun: `references/mechanics-and-fun.md`

Before any art pass, make the game worth playing. Write the core verb in CONCEPT.md (input → what the
player judges → outcome → failure → mastery), lay the course out as a beats table per stage
(introduce, test, twist, breathe), give it stakes and a score (lives or a timer, a combo or streak, stars or a rank; pick the ones this loop makes tense), and animate the
verb (`references/procedural-animation.md`, `src/client/Poser.luau`). Then add a client test hook
that drives the real controls and a bot scenario that plays the whole game; run it several times. It
must finish every time. Then run a second bot that misses like a person (judgement, timing and
reaction error; casual profile, 4+ runs, fixed seed). Its failures per stage are your difficulty
curve: a stage far above the rest is a wall, and a hot spot on an easy beat is a bug, usually in a
path only failure reaches (respawn, retry). Then play it with real input and capture the moments that matter. "Would a
12-year-old ask for another go after the results screen?" If not, the verb or the curve is wrong,
and no amount of UI will fix it.

## 4c. The play sheet

Fill in `scenarios/play-tour.txt` (it starts a session, runs your bot and captures a frame every few
seconds) and run `rbxgame tour scenarios/play-tour.txt`. This sheet is the game as the player sees it:
the real camera, the HUD, the feedback, each zone in order. From here on it is the main evidence for
every look, feel and UI claim; rerun it after every pass. On it, check:
- the next thing to do is the most visible thing in each frame (if you have to hunt for the target, add
  a beacon, a glow or contrast until you don't);
- the frames from different zones could not be mistaken for each other;
- nothing sits over the play space for more than a moment (banners, toasts, panels);
- water, sky and ground are not blown out to white or one flat colour.

Also film 30 seconds of play (`burst 30 gameplay` in the tour,
see `references/testing.md`) once the loop works and again before release: motion problems (a camera that
jitters, a hit with no feedback, ten seconds where nothing happens) are invisible on a sheet of stills.

## 5. Art pass: `references/art-direction.md`

Pick the style and a lighting preset from the reference, set Lighting in `default.project.json`
(Technology can only be set there), then dress the greybox: materials and colours from one palette,
terrain or ground with variation, landmarks visible from spawn, props that say what the place is.
`rbxgame shots` (from `shots.json`: overview, spawn, eye level, and one per area) and look at the sheet.
Then the play sheet again for the player's own camera. Give every zone its own look with
`src/client/Mood.luau` (time of day, air, water, grade), so reaching a new zone is a reward you can see. Judge it against the genre's best screenshots
from the research folder side by side.

## 6. Feel pass: `references/game-feel.md`

Every action the player takes is answered within 100 ms by at least motion and sound. The core verb
gets all the layers (anticipation, the move, impact particles, a camera kick, a sound, a number);
routine actions get two; the rare payoff gets the biggest version. Check the timings in play (they are the difference between a game that feels cheap and one
that feels good).

## 7. UI and audio: `references/ui-ux-style.md`, `references/audio.md`

Build every screen from `src/client/UiKit.luau` (it comes with the project): one theme set in its tokens (palette, corner radius, font) to match the world. Keep the kit's lip buttons, drawn icons and pop motion unless the game's art direction replaces them with something as tactile; flat web-style panels were rejected twice. List the screens from SESSION.md (title, first action, coach, reward, countdown,
HUD, stage change, failure, results, menu, settings) and build each from the recipes in
`references/ui-ux-style.md`: one focal point and one next action per screen, HUD in the corners, nothing
under the thumbs, every change animated. Then write `scenarios/ui-tour.txt` and run `rbxgame tour` on
desktop and with `--device "iPhone 1"`; judge the two sheets with the rubric in the same reference and
fix before moving on. The first UI of the test game was a website-style panel with text-pill buttons
and was rejected twice; the tour is how you see that before the person does.
Audio: music per zone, a sound on every action and every UI press, the payoff sound the loudest thing in the mix, and silence before a big moment.

## 8. Systems: data, economy, monetization, retention

`references/data.md`, `references/monetization.md`,
`references/retention-liveops.md`; instrument the funnel with the analytics skill. Run
`workflows/audits.md` before calling a build finished.

## 8a. Full journey and art review — independent of mechanical correctness

From a clean launch, activate the real UI, learn through the tutorial, play a complete session,
recover from a failure, finish, replay and return to the menu. Repeat the returning-player path and
phone layout. Keep captures of the actual entry, learning, transition and result screens, alongside
player-height environment views. Teleports do not prove the journey or the quality of the artwork.
Compare visual compositions with the baseline and user's chosen direction. Fix ugly or repetitive
asset arrangements, blocked views, weak hierarchy and flat pacing as actual defects. Do not declare
a game finished because a bot can visit all its platforms.

## 9. Review rounds

A round is: `rbxgame check`, every scenario, `rbxgame shots` and the play sheet, then a written
review in `NOTES.md` against the bar in CONCEPT.md, as a first-time player would see it: P0 (broken,
ugly, confusing, or unfair), P1 (weak), P2 (polish), and the ONE change that would most raise the game.
Fix every P0 and the ONE change in a single pass, then run the next round. Run at least three rounds and keep going while a round still finds a P0. If the same weakness survives two rounds, name its layer (concept, mechanic, geometry, composition or code) and fix it there; polishing around a dull verb is the usual mistake.

## 10. Publish: `workflows/publish.md`

Store page from real in-game captures (icon, thumbnails, title, description), age and content
questionnaire, passes and products priced. Publishing, uploading assets and creating passes use the
person's Roblox account: show them what will go out and wait for their yes.

## Hand-off

Tell the person in a few lines: the pitch, where the project is, how to open it (`cd <dir> && rbxgame
open`, or open `build/<Name>.rbxlx` in Studio), the contact sheet path, what is left, and anything that
needs them (a publish, an API key, a purchase).
