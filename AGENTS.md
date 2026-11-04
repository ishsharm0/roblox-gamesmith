# For coding agents

This repository is a skill for making Roblox games. If you are an agent working on a Roblox game:

1. Read `SKILL.md`. It has the rules, the tools, and a routing table from task to the file to read.
2. Run `tools/rbxgame doctor` and fix anything marked MISS.
3. For a new game, follow `workflows/make-a-game.md` in order.
4. For any Roblox API detail, run `tools/rbxdocs` (the official docs, offline) instead of relying on memory.

If you are an agent changing this repository itself:

- Keep `SKILL.md` a router: rules and pointers, not long explanations. Detail belongs in `references/`.
- Every new reference gets a row in the SKILL.md routing table; `python3 -m unittest discover -s tests`
  fails otherwise, and also fails on any path a doc mentions that doesn't exist.
- Write what you verified. Mark findings from real builds with how they were verified, and correct a
  doc when a test proves it wrong. A confident wrong instruction costs every agent after you.
- Tools use the Python standard library. If a tool needs a package, use a `uv` inline script header
  (see `tools/rbxdocs`).
- Template changes: `rbxgame new` a scratch project and run `rbxgame check` in it.
