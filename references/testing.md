# Testing a Roblox game from the shell

Three layers, fastest first. Each catches a different class of bug; a game isn't tested until all
three ran.

## 1. Pure rules in Lune (milliseconds, no Studio)

Anything that is a function of data (scoring, progression, state transitions, layout maths, save
migrations) lives in `src/shared/` without Roblox-only APIs, so Lune can run it.

```lua
-- tests/flow.luau
local Flow = require("../src/shared/Flow")
assert(Flow.action("Lobby", "Begin", false) == "Tutorial")
assert(Flow.action("Countdown", "Restart", true) == nil, "duplicate starts cannot stack countdowns")
assert(Flow.stars(23, 23, 0 / 0, 18000) == 0, "reject non-finite scores")
print("PASS: flow")
```

- `rbxgame check` runs every `tests/*.luau` with Lune after Selene and StyLua. A changed rule then
  can't leave a stale test behind (this happened: a test asserted an old star rule for days).
- Test the edges: illegal transitions, NaN and huge numbers, empty tables, the last stage.
- Keep these tests deterministic; no clocks, no randomness without a seed.

## 2. Server scenarios in Studio (seconds)

A scenario is a Luau file run in a playtest's Server or Client context through Studio's MCP:

```bash
rbxgame test scenarios/core-loop.luau          # play, run on the server, print console, stop
studio luau scenarios/leap-bot.luau --ctx Client  # during a play session you started
```

- A scenario `return`s a one-line summary (`phase=Results leaps=36 splashes=0 ...`) and `error`s on a
  broken expectation, so the shell sees pass or fail.
- Server scenarios may teleport and set state to isolate one rule (does a skipped checkpoint
  count?). Say so in the file header; such a scenario proves the rule, not the play.
- Client scenarios drive the **real controls** through a test hook (a `BindableFunction` the client
  exposes, `BotHook:Invoke("act", amount)`; see `templates/project/scenarios/human-bot.luau`), so input buffering, camera, aim assist and animation are
  in the loop.
- Long runs: MCP calls time out after about 5 minutes. Start the work in `task.spawn`, publish progress
  to a player attribute, return at once, and poll from the shell.

## 3. Bots and tours (minutes)

- **Precise bot**: plays the whole game with the real controls and perfect judgement. It must finish
  every time. If it can't, the game is broken.
- **Human-model bot**: same, with a person's judgement, timing and reaction error (profiles careful,
  casual, new). Run 4+ runs with a fixed seed. Its failures per stage are the difficulty curve; a spot
  far above its neighbours is usually a bug in a path only failure reaches (respawn, retry). Rank spots
  by failures / tries. Full method: `mechanics-and-fun.md`.
- **Probe**: before blaming the game for a hot spot, repeat that one action with zero error (and with
  deliberate offsets) to measure the real tolerance.
- **UI tour**: `rbxgame tour scenarios/ui-tour.txt [--device "iPhone 1"]` clicks through every screen
  with real input and captures each onto one contact sheet. Review it against the rubric in
  `ui-ux-style.md`.
- **Play sheet**: `rbxgame tour scenarios/play-tour.txt` runs a bot through a session and captures a frame every
  few seconds: the only capture that shows the real camera, HUD and feedback together. A game that owns its
  camera returns identical frames from `rbxgame shots --play`; use this instead.
- **Play film**: a tour step `burst 30 gameplay` films the
  Studio window for 30 s while the bot keeps playing; the MP4 lands in `shots/`. Stills cannot show pacing,
  camera motion, feedback timing or animation; a film can. Watch it yourself as a contact sheet
  (`ffmpeg -i film.mp4 -vf fps=2,scale=480:-1,tile=6x5 film-sheet.jpg`) and, if you have a video-capable
  model to hand, have it review the film as a game: where a new player is lost, which actions land with
  no feedback, the longest stretch where nothing new happens. Treat its notes as a second opinion and
  check each on a still. `studio burst out.mp4 --seconds 20` films outside a tour. `record` (a real 30 fps screen recording) also exists but needs a live display on the Studio machine; prefer `burst`. At 3 fps a reviewer cannot see particles or short pops: check those on stills.
- **Automatic sheet review**: set `RBXGAME_SHEET_HOOK` to a command that takes an image path and
  `--kind game|ui` (for example a script that asks a strong vision model for defects) and every tour prints
  that review under its sheet.
- **Camera sheet**: `rbxgame shots` captures the cameras in `shots.json` for an art review.

- **Physics games: a settle probe.** Before any bot fires, start a level, wait 5 s, and compare every
  dynamic part's position with where it was built (server scenario: record `Position` at build, then
  report the largest drift). Anything over a stud means the world moves on its own: stacks that slide,
  balls that roll off, parts that sleep and then jitter. Fix those before tuning difficulty: the Topple
  Toys build lost 20 minutes to balls rolling off towers that a bot was blamed for.

## What to test for every game

- [ ] Lune: rules, flow, stars/score, save migration.
- [ ] Server scenario: the core loop's rules, including illegal requests (skip a checkpoint, claim a
      reward twice, fire remotes with garbage types).
- [ ] Persistence: mock profile save -> end session -> reload -> fields intact.
- [ ] Receipts: failed save, duplicate receipt, partial grant rollback (`receipts.md`).
- [ ] Precise bot finishes 3/3.
- [ ] Human-model bot (casual, 4 runs): every run finishes; gentle curve; no hot spot unexplained.
- [ ] UI tour on desktop and phone: every screen reachable and leavable, nothing clipped.
- [ ] A capture of each key moment (start, mid-action, success, failure, results).

## What tests can't tell you

Whether it's fun, whether the feel is right with real hands, and how it runs on a real phone. Play it
with real input (`user_keyboard_input` holding keys for real lengths), and say plainly in the handoff
what wasn't tested by a person.
