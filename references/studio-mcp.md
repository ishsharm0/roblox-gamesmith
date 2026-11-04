# Driving Roblox Studio from the shell

Roblox Studio ships its own MCP server (`StudioMCP`, inside the app bundle). The `studio` command in
`tools/` is a small client for it: each call starts StudioMCP over stdio, finds the Studio window,
runs one tool and prints the result. No editor plugin and no restart of your agent are needed.

## Setup (once)

1. Install Roblox Studio and sign in.
2. In Studio, turn on **Enable Studio as MCP server** (Assistant panel -> `...` -> Manage MCP Servers,
   or Studio Settings, depending on version).
3. `rbxgame doctor` checks the binary, the connection, and the Rojo toolchain.

## Hidden by default

People keep using their computer while an agent works. Open places with `rbxgame open` or
`studio open` only: they launch Studio with `open -g -j` (not focused, hidden) and re-hide it after
play/stop. Reuse the project's one window (`rbxgame push` hot-swaps code) instead of quitting and
reopening. Never take a full-screen screenshot of the desktop; the viewport comes from `studio shot`.

## Commands

```bash
studio list                                   # connected windows: id, place name
studio luau build.luau                        # run a file in the Edit data model
echo 'return #workspace:GetDescendants()' | studio luau -
studio play ; studio luau bot.luau --ctx Client ; studio stop
studio shot out.png --pos 40,30,40 --look 0,0,0   # capture from a camera, then restore it
studio console                                # output log
studio export 'workspace["Map"]' world/Map.rbxm  # instance -> model file (chunked, any size)
studio import asset.rbxm 'game.ServerStorage'
studio call <tool> '<json>'                   # any MCP tool directly
studio tools / studio schema <tool>           # what Studio's MCP offers right now
```

With several windows open, `--studio <id or name>` picks one; otherwise the window with the project's
place is used.

## Contexts

- **Edit**: the place as saved. Build worlds, edit properties, run audits. Changes here are what
  `rbxgame save` exports.
- **Server** / **Client**: exist only while playing (`studio play`). Server for rules and state, Client
  for input, camera, UI and the local character. Changes vanish on stop.

## What the MCP Luau context can and can't do (tested)

- Runs with plugin-level rights: `Script.Source` writes, `ChangeHistoryService`,
  `SerializationService`, `EditableMesh`, `InsertService:LoadAsset` for owned assets.
- Can't read or write `Lighting.Technology`: set it in `default.project.json`.
- Text results are cut at about 100k characters: return summaries, not dumps; the CLI moves files in
  60k-character chunks for export/import.
- A long loop with no yield freezes Studio and drops the connection: build in chunks with
  `task.wait()` between them.
- Calls time out after about 5 minutes: start long work with `task.spawn`, write progress to an
  attribute, return, and poll.
- `print` output goes to the console (`studio console`), not to the call result; `return` what the
  shell should see.

## Useful built-in tools

| Tool | Use |
|---|---|
| `execute_luau` | everything (the `studio luau` command) |
| `screen_capture` | viewport image, optionally from a given camera (the `studio shot` command) |
| `start_stop_play`, `get_studio_state` | playtest control |
| `user_keyboard_input`, `user_mouse_input` | real input during play: hold keys for real durations, click GUI by instance path |
| `character_navigation` | walk the character to a point or instance |
| `get_console_output` | errors and prints |
| `search_game_tree`, `inspect_instance`, `script_grep`, `script_read` | explore an existing place |
| `insert_asset` | Creator Store / inventory assets (audit them: `security.md`) |
| `list_skills`, `skill` | Roblox's own guides (debugging, profiling, device simulator, analytics, unit tests) |
| `generate_*` | AI meshes, textures, materials, avatars, scenes: **off by default**; use only when the person asks for them by name |

## Patterns

**Build a world from code.** World builders live in `src/server/World/*.luau` as modules with a
`Build(parent)` function; a scenario requires and runs them in Edit, then `rbxgame save` exports the
result. The world is then reproducible and reviewable.

**Playtest a scenario.** `rbxgame test scenarios/x.luau` = play, run on Server, print console, stop.
For client bots: `studio play`, start the bot in Client context, poll an attribute, `studio stop`.

**Capture a review sheet.** `rbxgame shots` reads cameras from `shots.json` and writes one contact
sheet; `rbxgame tour` clicks through UI screens and captures each.

**Inspect someone else's place.** `search_game_tree` for structure, `script_grep` for patterns,
`inspect_instance` for properties; then decide whether to move it into files (`studio export`).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `no Studio connected` | Studio not running, no place open, or the MCP server toggle is off |
| Call hangs then times out | Studio is busy (a modal dialog, a frozen script); check the window, then `studio stop` |
| `Edit datamodel is not available in Play mode` | `studio stop` first, or pass `--ctx Server/Client` |
| Wrong window answers | `studio list`, then `--studio <id>` |
| World edits disappeared | Studio was closed without `rbxgame save`; `rbxgame open` saves first, a manual quit doesn't |
