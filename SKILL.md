---
name: roblox-gamesmith
description: >
  Make complete Roblox games end to end on a Mac: research what's working on Roblox, design a core
  mechanic that is actually fun, build the world and systems as files (Rojo) while driving Roblox
  Studio through its built-in MCP server, playtest with bots that play like people, review captures,
  polish UI, feel and audio, and prepare the release. Includes the official Roblox docs offline
  (rbxdocs), a project template with a UI kit and bot harness, and references for Luau, architecture,
  security, data, monetization, UI, performance and every major genre. Use for any Roblox game,
  Roblox Studio or Luau task.
---

# Roblox Gamesmith

A game is a folder: code in `src/`, the world in `world/*.rbxm`, `default.project.json` mapping them
into the place, and Rojo building it. Studio is the editor and the test rig, driven from the shell;
it is never the only copy of anything.

**The bar:** a game a player would pick from the Roblox home page over its genre's top ten. It looks
made on purpose, it is fun within 30 seconds, it is a skill to get better at, and it works on a phone.

## Start here

1. `rbxgame doctor`. Fix anything marked MISS before building. If Studio isn't connected, ask the
   person to open Studio and turn on "Enable Studio as MCP server".
2. New game: pass `references/concept-gate.md` in writing first (two polished games were rejected as unoriginal and thin; the idea was wrong before the first file). Then read `references/creative-quality.md` and `workflows/make-a-game.md` before the first file. It sets the order and the bar. `rbxgame new` scaffolds a playable starter game: edit it, don't rewrite it (`templates/project/STARTER.md`).
3. Existing game or a single task: find it in **Routing** below and read that file first.
4. Unsure how something is done: `references/reference-game.md` shows the patterns a tested game used.

## Check the official docs, not your memory

Roblox's APIs change monthly. `rbxdocs` is Roblox's own documentation (github.com/Roblox/creator-docs),
cached locally and refreshed weekly:

```bash
rbxdocs api TweenService              # a class: summary, inheritance, every member with types
rbxdocs api BasePart.CanQuery         # one member in full (inherited members work too)
rbxdocs api Enum.EasingStyle          # enums, datatypes (Vector3), libraries (task), globals (typeof)
rbxdocs find PartsIn                  # API names containing text
rbxdocs search streaming persistent   # ranked guide + API search
rbxdocs read ui/frames --section Clipping   # a guide page or one section of it
```

Before you write an API you haven't used in this project, look it up: names, parameter order,
security level, yields, deprecation, limits. This skill's references give the judgement (what to build
and why); the docs give the facts. When they disagree on a fact, the docs win: fix the reference.

## Tools (`tools/`, on PATH after `install.sh`)

| Need | Command |
|---|---|
| Setup check | `rbxgame doctor` |
| Scaffold, build, open hidden, hot-reload, save the world, lint and test | `rbxgame new/build/open/push/save/check` |
| Playtest a scenario on the server; camera contact sheets | `rbxgame test <file>`, `rbxgame shots` |
| Click through every UI screen, desktop and phone, onto one sheet | `rbxgame tour scenarios/ui-tour.txt [--device "iPhone 1"]` |
| See the game as the player does: a bot plays, a frame every few seconds | `rbxgame tour scenarios/play-tour.txt` |
| Anything in Studio: run Luau in Edit/Server/Client, capture, play/stop, console, export/import | `studio luau/shot/play/stop/console/export/import/call` |
| Official Roblox docs and API reference | `rbxdocs api/find/search/read` |
| What's trending on Roblox, a game's stats and passes | `rbx-research` |
| Reference gameplay: YouTube search, transcripts, frames | `yt-research` |
| DevForum answers | `devforum` |
| Upload assets with your own Open Cloud key | `rbxcloud` (`references/open-cloud.md`) |
| Meshes from Blender, headless | `tools/blender/` (`references/blender-pipeline.md`) |

## Rules that hold on every task

- **Server authority.** The server owns every rule, reward and currency; the client asks, predicts and
  animates. Validate every remote: type, range, ownership/state, rate (`references/security.md`).
- **Files are the source.** Code changes go in `src/` and reach Studio with `rbxgame push`. World edits
  made in Studio are exported with `rbxgame save` before anything closes.
- **A game is a skill to get better at.** Before art, the core verb needs a judgement in it (timing,
  distance, aim, route, risk). Design the session beat by beat (introduce, test, twist, breathe) and
  give it stakes and a score the player can beat; drop one only when the genre has a better
  answer, and write that answer down. A precise bot must finish it, and a bot with a person's errors must show a
  gentle curve (`references/mechanics-and-fun.md`). A first version without this was rejected as "an
  obby for babies".
- **Look before you claim.** Capture the game (the play sheet from `scenarios/play-tour.txt` first, then
  `rbxgame shots`, `studio shot`, the UI tour) and look at
  the images before saying how it looks. Run the scenario before saying it works. A claim without a
  capture or a passing run behind it is a guess; say which parts are untested.
- **Probe before you blame.** When a test fails in a surprising place, reproduce that one action with
  exact inputs before changing the game. Bots and scenarios have bugs too.
- **Be a quiet guest on the person's computer.** Studio opens hidden (`rbxgame open`, `studio open`)
  and one window per project is reused. No full-desktop screenshots. Blender runs headless and only
  when the person wants meshes from it. If they have a second machine, put Studio there: with
  `STUDIO_REMOTE=user@host` set (a Windows PC over SSH, signed in to Studio, MCP server on) every
  `studio` and `rbxgame` command, playtests and captures included, runs on that machine and nothing
  opens here.
- **Built or licensed art, not generated.** Parts, terrain, Blender meshes, CC0 kits and vetted
  Creator Store assets. Studio's `generate_*` tools and AI images stay off unless the person asks for
  them by name.
- **Free models are untrusted.** Audit every inserted asset for scripts before keeping it.
- **Player data** goes through one session-locked module (`references/data.md`); purchases are granted
  idempotently (`references/receipts.md`).
- **Every `:Connect` has an owner that disconnects it; every loop yields.**
- **Money and publishing need a yes.** Never spend Robux, create products, or publish or update a
  live experience without the person's explicit go-ahead for that specific action.

## Routing

| Task | Read |
|---|---|
| Make a game, any genre | `workflows/make-a-game.md`, then `templates/genres.md` and `references/game-design.md` |
| Choosing or judging a concept: originality, social stake, depth, difficulty targets | `references/concept-gate.md` |
| Research ideas, comparable games, trends | `references/research.md` |
| The core mechanic, difficulty curve, scoring, stakes, fairness, bot playtests | `references/mechanics-and-fun.md` |
| First session, onboarding, the flow from arrival to "one more go" | `references/player-journey.md` |
| Level and course layout | `references/level-design.md` |
| How a tested game was put together (patterns with code) | `references/reference-game.md` |
| Drive Studio, build worlds from code, playtest | `references/studio-mcp.md` |
| Project structure, state, remotes, networking | `references/architecture.md` |
| Luau language, types, scheduling, cleanup | `references/luau.md` |
| The look: lighting, atmosphere, materials, composition | `references/art-direction.md`, then `references/visual-review.md` |
| Game feel: tweens, camera, hit-stop, juice | `references/game-feel.md` |
| Particles, beams, trails, animation assets | `references/vfx.md` |
| Character animation without assets (crouch, jump, flip, land) | `references/procedural-animation.md` + `templates/project/src/client/Poser.luau` |
| UI and UX: screens, HUD, menus, flow | `references/ui-ux-style.md` (design), then `references/ui-engineering.md` (build); use `UiKit.luau` |
| Audio | `references/audio.md` |
| Procedural geometry, model quality, proportions and construction | `references/geometry-quality.md` |
| Original concepts, audience appeal, pacing and creative review | `references/creative-quality.md` |
| Models, meshes, textures, Creator Store, Blender | `references/assets-pipeline.md`, `references/blender-pipeline.md`, `references/open-cloud.md` |
| Tested Blender Python kit: stylised props, rigs, animation, renders, CC0 assets and export | `references/blender-kit.md` |
| Saving player data | `references/data.md` |
| Shops, passes, products, receipts | `references/monetization.md`, `references/receipts.md` |
| Retention, live ops, store page, analytics | `references/retention-liveops.md` |
| Combat, enemies | `references/systems-combat.md` |
| Inventory, items, trading | `references/systems-inventory.md` |
| Security and exploits | `references/security.md` |
| Performance | `references/performance.md` |
| Tests: Lune, scenarios, bots, tours | `references/testing.md` |
| Rojo, Rokit, Selene, StyLua, Lune, Wally | `references/tooling.md` |
| A bug | `workflows/debug.md`, then `references/sharp-edges.md` |
| Audits before publish or merge | `workflows/audits.md` |
| Publishing | `workflows/publish.md` |
| Anything about a specific Roblox API or feature | `rbxdocs` first |

Roblox Studio also serves its own guides over MCP (`studio call list_skills '{}'`, then
`studio call skill '{"skill_name":"rbx-debug"}'`): debugging, profiling, the device simulator,
analytics, network simulation and unit tests.

## Done means

A game is done when the work in `workflows/make-a-game.md` is checked off with evidence:
`rbxgame check` green, scenarios passing, both bots run, the UI tour reviewed on desktop and phone,
captures of the key moments looked at, and NOTES.md saying what was tested, how, and what wasn't.
Then tell the person in a few lines what the game is, how to open it, and what still needs human hands.
