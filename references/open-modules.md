# Open modules: what to vendor and what to skip

Checked 2026-11-14 against the GitHub API (licence, last push, archived flag). Re-check before vendoring: `gh api repos/<owner>/<repo> --jq '[.license.spdx_id,.pushed_at,.archived]'`. Vendor by copying the single module file into `src/server/Vendor/` or `src/shared/Vendor/`, keep its licence header, and read it once before use. Downloaded code is untrusted until read.

## ADOPT

| Module | URL | Licence | Use | Credit requirement | Last push |
|---|---|---|---|---|---|
| Trove (in RbxUtil, `modules/trove`) | https://github.com/Sleitnick/RbxUtil | MIT | One object that owns connections, instances, threads and callbacks, cleaned up together: `trove:Connect`, `trove:Add`, `trove:Clean`. Use for every per-player, per-round and per-UI-screen lifetime (see `references/luau.md` on cleanup). | Keep the MIT header in the copied file. | 2026-08-11 |
| ProfileStore | https://github.com/MadStudioRoblox/ProfileStore | Apache-2.0 | Session-locked player data with retries. Already the default in `references/data.md`. | Keep the licence header and NOTICE text. | 2025-07-31 (stable, quiet) |
| TopbarPlus v3.5.0 | https://github.com/1ForeverHD/TopbarPlus | MPL-2.0 plus a credit clause | Topbar icons, menus and toggles that match the platform's own bar, with controller and mobile support. | Required: keep the module's Attribute unchanged, or credit TopbarPlus in the experience description (or in a DevForum post linked from it). Put the credit line in the experience description (`workflows/publish.md`, section 2) before publishing. | 2026-11-13 |

Credit line to paste when you do not keep the Attribute: `Topbar icons by TopbarPlus (1ForeverHD).`

## ADAPT (read, borrow ideas, do not make the default)

| Module | URL | Licence | Why only ideas | Last push |
|---|---|---|---|---|
| Vide | https://github.com/centau/vide | MIT | Lighter reactive UI than React; small community, so budget time for gaps. Try only when a screen is state-heavy. | 2026-10-26 |
| Charm | https://github.com/littensy/charm | MIT | Atom-style shared state, client and server sync. Useful pattern; the project template's own state module is simpler. | 2026-10-01 |
| jest-roblox | https://github.com/Roblox/jest-roblox | MIT | Luau unit tests. `rbxgame check` and the Lune tests in `references/testing.md` already cover the need. | 2026-11-10 |

## SKIP

| Module | Reason |
|---|---|
| Fusion | Works and is MIT, but upkeep is slow (last push 2026-02-02) and it adds a second UI paradigm next to `UiKit`. |
| react-lua (jsdotlua) | Heavy dependency tree, last push 2025-05-23, and the template's UI kit already builds screens without it. |
| Matter (ECS) | Last push 2024-12-31; the game sizes here do not need an ECS. |
| Knit | Archived. Use plain modules and remotes (`references/architecture.md`). |
| Red | Reported archived (not re-checked here); use `Net.luau` from the template. |
| Flipper | Last push 2021; use `TweenService`. |
| RbxCameraShaker | Last push 2023-07-06; the camera shake recipe in `references/game-feel.md` section 3 is enough and has no dependency. |
| Roblox-named "MCP server" repos with SEO titles (many appeared with tens of stars, no licence, pushed the same day) | Bait pattern; never run them. The built-in Studio MCP is the supported route (`references/studio-mcp.md`). |
| `Roblox/studio-rust-mcp-server` | Archived and superseded by the built-in Studio MCP. |
