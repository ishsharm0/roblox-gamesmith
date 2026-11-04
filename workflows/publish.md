# Publishing

Passing tests and a local build don't make a game published. Publishing changes a public page under
someone's Roblox account: an agent prepares everything, and the owner approves the publish itself,
any spending, and any product creation.

## 1. Release candidate

- [ ] `rbxgame check`, core scenarios, persistence and receipt scenarios pass on the exact build.
- [ ] Precise bot 3/3; human-model bot (casual, 4 runs) finishes every run with a gentle curve.
- [ ] UI tour on desktop and phone reviewed against `references/ui-ux-style.md`.
- [ ] Audits done (`workflows/audits.md`): security, performance, monetization (if any products).
- [ ] NOTES.md lists what was tested, how, and what wasn't (real phone, two humans, live DataStores).

## 2. The store page

- **Title**: says the verb; under ~30 characters; no keyword stuffing.
- **Description**: two short lines of what you do and why it's fun, then a few bullet features, then
  controls. Honest; no promises of content that isn't there.
- **Icon**: 512x512, the character or object that is the game, bold and readable at 50 px.
- **Thumbnails**: 3-5 real captures (`rbxgame shots`, UI hidden or tidy) of the best moments; first
  one carries the game. No AI-generated art; no misleading scenes.
- **Genre and devices**: honest genre; supported devices that were actually tested.
- **Maturity questionnaire**: answered truthfully for the actual content.

## 3. Settings the owner makes

- Publish to Roblox (File -> Publish to Roblox, or Open Cloud place publishing with a key that has
  that permission) under the intended user or group.
- Enable API services for DataStores; keep Studio tests on the mock or a separate test universe.
- Max players, server fill, private server price.
- Permissions: assets (animations, audio, meshes) owned by the same owner as the place.
- Products and passes created with prices the owner chose.

## 4. After publishing

- Play the live version from a phone and a computer, together if possible.
- Rejoin fast twice: data intact, no duplication.
- Watch the first days of analytics: first-session length, day-1 return, where players quit (funnel
  events, `references/retention-liveops.md`).
- Fix the biggest drop-off first. Update thumbnails as the game improves.

## Updates

- Shut down servers for breaking changes only; otherwise let them migrate.
- Save-schema changes always come with a migration (`references/data.md`).
- Note every release in NOTES.md: what changed, what was tested.
