# Performance: hold 60 fps on a cheap phone

Most Roblox players are on phones. The budget is a mid-range Android at 60 fps (16.6 ms per frame)
with under ~1 GB of memory for the game. Measure first, then fix the biggest thing.

## Measure

- **MicroProfiler** (Ctrl+F6, or the `rbx-perf-profiling` skill from Studio's MCP): find the label
  eating the frame. Script time shows under the script's name.
- **Developer Console** (F9): Memory (by category), Network (data in/out), Scripts (activity %),
  Server stats when playing a published game.
- `Stats` service from code for automated checks:
  `Stats:GetTotalMemoryUsageMb()`, `workspace:GetRealPhysicsFPS()`.
- In Studio over MCP, a `scenarios/` script can sample memory and part count during a bot run and
  report peaks.
- Test on a real low-end device before launch; the emulator shows layout, not speed.

## Usual suspects, in order

1. **Too many moving or unanchored parts.** Anchor everything that doesn't need physics. Scenery
   that moves (water bobbing, swaying plants) moves on the client, in one loop, only when on screen.
2. **Per-frame script work over many objects.** One loop over a list beats one connection per object.
   Throttle anything that doesn't need every frame (AI to 5-10 Hz, UI counters to 10 Hz).
3. **Part and draw count.** Merge static detail into meshes or unions (fewer draw calls), reuse the
   same `MeshId` (instanced rendering), keep unique textures few and small (512 or 1024 px).
4. **Transparency and particles.** Overlapping transparent parts and big particle emitters cost fill
   rate on phones. Cap `Rate`, shorten `Lifetime`, keep emitters small, avoid transparent walls.
5. **Shadows and lights.** `CastShadow = false` on small decorative parts. Few dynamic lights;
   `Future` lighting is the expensive one (set `Lighting.Technology` in `default.project.json`, since
   it isn't scriptable from plugins or MCP).
6. **Network.** Changing replicated properties every frame on many parts floods the client. Animate
   on the client, replicate only gameplay state.
7. **Memory leaks.** Connections never disconnected, tables keyed by players never cleared, instances
   cloned and never destroyed. Memory climbing over a 10-minute session is a leak.

## Streaming

`Workspace.StreamingEnabled = true` for any map bigger than one screen of detail. It lowers memory
and join time on phones. Costs: client code must handle parts that aren't there yet
(`WaitForChild` with a timeout), and models that must always exist use
`ModelStreamingMode = Persistent` (sparingly). Tune `StreamingTargetRadius` to the gameplay's sight
lines.

## Physics

- `CanCollide = false`, `CanTouch = false` and `CanQuery = false` on decoration that the player never
  touches or raycasts against; touch and query tests are not free.
- Collision fidelity `Box` or `Hull` on detailed meshes; `PreciseConvexDecomposition` only where the
  shape matters for gameplay.
- Raycasts with a `RaycastParams` include list (only landable parts) are faster and more correct
  than excluding scenery.

## Server

- One server serves up to `MaxPlayers` players; per-player costs multiply. Profile a server with bots
  or a full test session.
- DataStore and HTTP calls are slow; never inside per-frame loops; cache.
- `task.wait()` in a tight loop on the server still runs at 60 Hz; use `task.wait(0.2)` where 5 Hz is
  enough.

## Checks before publish

- [ ] MicroProfiler on a phone-class device: no frame over 16 ms in normal play.
- [ ] Memory flat over a 10-minute bot session.
- [ ] Part count and unique mesh/texture count noted in NOTES.md, with the biggest offenders.
- [ ] No per-frame replicated property changes on scenery.
- [ ] Streaming on (or a written reason why not).

`workflows/audits.md` has the full performance audit.
