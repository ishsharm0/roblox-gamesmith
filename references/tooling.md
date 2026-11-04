# Tooling: files are the source, Studio is the editor

Every project is a folder under version control. Studio opens a place that Rojo built from it; code
edits happen in files; world edits made in Studio are exported back to `.rbxm` files with
`rbxgame save`. Nothing exists only inside Studio.

## The toolchain

| Tool | Job | Install |
|---|---|---|
| **Rokit** | installs and pins the tools below per project (`rokit.toml`) | `install.sh` sets it up |
| **Rojo** 7.x | builds `default.project.json` into a place; live-syncs to Studio | `rokit add rojo-rbx/rojo` |
| **Selene** | linter (unused vars, shadowing, deprecated APIs, Roblox std) | `rokit add Kampfkarren/selene` |
| **StyLua** | formatter | `rokit add JohnnyMorganz/StyLua` |
| **Lune** | runs Luau outside Roblox: unit tests, build scripts | `rokit add lune-org/lune` |
| **Wally** | package manager (optional) | `rokit add UpliftGames/wally` |
| **luau-lsp** | editor type checking and autocomplete (optional) | editor extension |

The skill's `tools/` (Python 3 standard library only, plus `uv` for the research tools):

| Command | Job |
|---|---|
| `rbxgame` | project lifecycle: new, build, open, push, save, check, test, shots, tour, doctor |
| `studio` | talks to Studio's built-in MCP server: run Luau, capture, play/stop, console, export/import |
| `rbx-research` | Roblox discovery charts, game stats, passes, thumbnails |
| `yt-research` | YouTube search, transcripts and frames for reference gameplay |
| `devforum` | DevForum search |
| `rbxcloud` | Open Cloud asset upload and key status (needs your own API key) |

## Project file

`default.project.json` maps folders to the data model:

```json
{
  "name": "My Game",
  "tree": {
    "$className": "DataModel",
    "ReplicatedStorage": { "Shared": { "$path": "src/shared" } },
    "ServerScriptService": { "Server": { "$path": "src/server" } },
    "StarterPlayer": { "StarterPlayerScripts": { "Client": { "$path": "src/client" } } },
    "Workspace": { "Map": { "$path": "world/Map.rbxm" } },
    "Lighting": { "$properties": { "Technology": "Future" } }
  }
}
```

- Properties that scripts can't set (`Lighting.Technology`) go in `$properties` here.
- File naming: `Foo.server.luau` -> Script, `Foo.client.luau` -> LocalScript, `Foo.luau` -> ModuleScript,
  `init.luau` makes a folder a module.

## The daily loop

```bash
rbxgame new ~/rbx/my-game --name "My Game"   # scaffold from templates/project
cd ~/rbx/my-game
rbxgame open        # build and open hidden in Studio (reuses the window next time)
# edit src/...
rbxgame push        # hot-reload code into the open Studio
rbxgame check       # selene + stylua + lune tests
rbxgame test scenarios/smoke.luau
rbxgame save        # after building or editing the world in Studio
git commit
```

`rbxgame open` saves the world before closing a window and rebuilding; `push` swaps code without
touching the world. Prefer `push` while iterating.

## Lint and format settings

`selene.toml`: `std = "roblox"`. `stylua.toml`: tabs, 120 columns, double quotes. `rbxgame check`
fails on any Selene warning, so keep the code at zero warnings; suppress a rule inline only with a
comment saying why (`-- selene: allow(shadowing) -- reason`). Vendored code lives in `Vendor/` folders,
which check skips.

## Packages

Small projects don't need Wally. When you do: `wally.toml` at the root, `wally install`, map
`Packages` into ReplicatedStorage in the project file, and commit `wally.lock`. Read every package's
source the first time; they run with your game's permissions.

## Version control

- Commit `src/`, `world/`, `tests/`, `scenarios/`, the project file and docs. Ignore `build/`,
  `shots/`, `sourcemap.json`.
- `.rbxm` world files are binary; commit them after each meaningful world change with a message
  saying what changed, and capture a shot so reviewers can see it.
- Never commit API keys; tools read them from `~/.config/roblox/` or environment variables.
