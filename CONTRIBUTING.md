# Contributing

Thanks for helping. This skill is only as good as the lessons in it, so the bar for a change is:
**is it true, and does an agent reading it make a better game?**

## Good contributions

- A pitfall you hit in a real project, with the symptom, cause and fix: a row in
  `references/sharp-edges.md`.
- A mechanic, UI or feel pattern proven in a game you shipped or tested, with the numbers that worked.
- Tool fixes and new tool features, with a test in `tests/`.
- Corrections. If the official docs (`rbxdocs`) disagree with a reference on a fact, fix the reference.

## Before opening a pull request

```bash
python3 -m unittest discover -s tests -v     # docs integrity + tool tests
tools/rbxgame new /tmp/gs-check && (cd /tmp/gs-check && rbxgame check)
```

If you changed the project template, scaffold a fresh project and run its checks.

## Style

- Plain, direct sentences. Say what to do and why; skip filler.
- `SKILL.md` stays a router. Detail goes in `references/`, process in `workflows/`.
- Mark verified findings and say how they were verified. Don't present guesses as facts.
- Original writing only. Don't paste text from other guides or repositories; link them instead.
