# Level Design

Load when laying out a map, hub, obby, dungeon or first-time user experience (FTUE). Pairs with `art-direction.md` (how it looks), `game-design.md` (loops) and `retention-liveops.md` (why the first minute matters for discovery).

## The 5 rules that matter most

1. **Spawn-to-fun under 30 seconds.** A new player should perform the core action within 10-15 s of control and get a reward within 30 s. Roblox now weighs first-play bounce rate directly in recommendations.
2. **Teach with space, not text.** One path, one obvious goal, one safe place to try the mechanic. Words are a last resort.
3. **Always show the next goal.** From any spawn or checkpoint, the next objective or a landmark leading to it is on screen.
4. **Fail cheap, fail fair.** Checkpoints close together, hazards that read as hazards, collisions that match visuals, instant respawn.
5. **Pace in waves.** Tension, release, reward. Never more than ~60 s of the same intensity.

---

## 1. Units and metrics

| Thing | Number |
|---|---|
| Default character height | ~5 studs (R15 ~5.2) |
| Default `WalkSpeed` | 16 studs/s |
| Default `JumpPower` 50 (`JumpHeight` 7.2), gravity 196.2 | Airtime ~0.54 s, so ~9 studs horizontal at walk speed; with body width a flat gap of ~9-10 studs is the limit. Plan gaps of 4-8 |
| Comfortable corridor | 8-12 studs wide; 6 min for tense horror |
| Door | 5-6 wide x 8-9 tall |
| Stair step | 1 stud rise; `Humanoid.MaxSlopeAngle` 89 by default lets players walk most ramps |
| Ceiling for interiors | 12-16 studs (camera needs room; low ceilings fight the third-person camera) |
| Landmark spacing | something new or a landmark every 60-100 studs of travel (4-6 s of walking) |
| Hub spawn to first interactable | under 30 studs (2 s) |

Confirm jumps by testing, not maths alone: build a calibration strip with gaps 4, 6, 8, 10, 12 studs and heights 2, 4, 6, 8 and have `character_navigation` / a human try them.

---

## 2. First 60 seconds (FTUE)

Timeline for a new player (first visit):

| Time | What happens |
|---|---|
| 0-5 s | Loads into a framed view: landmark + first goal visible. No modal popups, no daily reward window, no shop. |
| 5-15 s | First action: a big obvious interactable (glowing pad, ProximityPrompt, breakable, first jump). |
| 15-30 s | First reward with full juice: currency burst, sound, counter pop (see `game-feel.md`). |
| 30-60 s | Second goal introduces the second verb or the first upgrade; show a hint of the next zone. |
| 1-5 min | First meaningful purchase/upgrade; first social cue (other players visible, a friend invite prompt only after this). |

Rules:

- Spawn new players in an FTUE pocket or facing the right way (`SpawnLocation` orientation matters; the camera starts behind the character).
- Defer everything that is not the core loop: daily rewards, codes, settings, shop, group-join prompts. Show them after the first reward or on the second session.
- Track it: `AnalyticsService:LogOnboardingFunnelStepEvent(player, step, "StepName")` for each FTUE step (steps 1-100). Find the step where players drop and fix that space. https://create.roblox.com/docs/en-us/reference/engine/classes/AnalyticsService.md
- Returning players skip the tutorial pocket; spawn them in the hub with a "continue" goal.

---

## 3. Teaching without text

- **Gate by geometry**: the only way forward requires the new verb (a gap that needs a jump, a door that needs the key you just got).
- **Safe first, then stakes**: first use of a mechanic has no failure cost (a jump over a shallow pit you can walk out of), second has a little, third is a real test.
- **Show, then ask**: an NPC or animated prop demonstrates (a box sliding down a chute, an enemy walking into a trap) before the player must do it.
- **Affordances**: consistent visual language for climbable, breakable, bouncy, deadly. Decide once, document in the art bible, never break it.
- **Contextual prompts**: `ProximityPrompt` with `ActionText` ("Open", "Plant") and `ObjectText`, shown only within range. Input hints change per platform automatically.
- **Arrows and beams** as a last resort: a `Beam` from the player to the goal for the first objective only, then remove it.

---

## 4. Pacing and difficulty curves

- **Sawtooth**: each section starts a bit easier than the last section's peak, then climbs higher. After a spike, a breather with a reward.
- **Rule of three**: introduce, develop, twist. Mechanic A alone; A with more pressure; A combined with B.
- **Intensity budget**: alternate high (combat/hard jumps) and low (exploration/shop/social) beats every 30-90 s.
- **Session shape**: a meaningful milestone every 5-10 minutes (new zone, upgrade, rank); the session should end on a teaser of the next thing.

### Obby specifics

| Stage band | Content |
|---|---|
| 1-5 | Walk-and-jump basics, gaps 4-6 studs, wide platforms (6x6+), no kill bricks or only over shallow drops |
| 6-15 | Introduce one hazard per stage (kill parts, moving platforms, spinners); gaps up to 8 |
| 16-30 | Combine two mechanics; narrower platforms (3x3), timing elements |
| 30+ | Precision and speed; every 10 stages a "boss" stage, followed by an easier breather and a theme change |

- Change theme (palette, music, skybox tint) every 10-15 stages so progress is visible.
- Show stage number and a progress bar; a leaderstat for highest stage.
- Difficulty comes from execution, never from deception: no invisible kill parts, no fake platforms without a tell, no blind jumps where the landing is off-screen.
- Moving platforms: move the platform with `PrismaticConstraint`/`AlignPosition` or a server-side `TweenService` on an anchored part, and make sure players standing on it carry with it (constraints-driven, unanchored assemblies carry characters better than CFrame-tweened anchored parts). Test on a 200 ms simulated connection (Studio Network Simulation).
- Skips for Robux are acceptable only if difficulty is not inflated to sell them.

---

## 5. Sightlines and landmarks

- From spawn: landmark visible, first goal visible, exits visible.
- Each zone has a unique landmark recognisable by silhouette (see `art-direction.md`).
- Use height: players read the map from vantage points. Give them one early (a hill, a tower in the hub) that overlooks the next 2-3 goals.
- Block sightlines to unfinished or out-of-bounds areas with terrain or props, not invisible walls alone.
- With `StreamingEnabled` on, distant landmarks may not be streamed; set landmark models to `ModelStreamingMode = Persistent` or give them `LevelOfDetail = StreamingMesh` so their low-detail imposter shows at distance.

---

## 6. Hub layouts

- **Radial hub**: spawn in the centre, 3-6 spokes to activities, each spoke's entrance visually distinct. Best for simulators and minigame collections.
- **Linear hub with branches**: spawn at one end, main street of shops/portals. Best for roleplay towns.
- Keep the hub compact: every main feature within ~20 s of walking (about 300 studs) or one teleport pad.
- Put social stuff where players naturally wait: leaderboards, trading area and showcase pedestals next to the spawn and the queue/portal area.
- Shop and upgrades on the path back from the activity, not off to the side.
- Signpost with shapes and colour (a giant pickaxe over the mining portal) before text.

---

## 7. Collision, kill parts and fairness

- Kill parts look dangerous (hazard colour, glow, animation, sound) and are `CanCollide = true` only if the player should stand on them before dying; otherwise use `CanCollide = false` with a `Touched` check, or better, a region query.
- Prefer server-side region checks for kill zones and fall-outs (`workspace:GetPartBoundsInBox` per tick or a `Y` threshold) over relying solely on `Touched`, which can miss fast or lagging players. Use `FallenPartsDestroyHeight` for the global floor.
- Hitboxes smaller than visuals for hazards (forgiving), larger than visuals for pickups and checkpoints (generous).
- Respawn quickly: `Players.RespawnTime` 1-2 s for obbies (default 5).
- Collision groups (`PhysicsService:RegisterCollisionGroup`, `BasePart.CollisionGroup`) to stop players colliding with each other in obbies and queues.
- No unanchored decorations in play paths; physics props near spawn get flung by exploiters and lag.

Kill zone using a region instead of `Touched`:

```lua
-- Server. KillZones are tagged parts (CollectionService tag "KillZone"), CanCollide false, transparent if needed.
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local params = OverlapParams.new()
params.FilterType = Enum.RaycastFilterType.Include

local accumulator = 0
RunService.Heartbeat:Connect(function(dt)
	accumulator += dt
	if accumulator < 0.1 then return end
	accumulator = 0
	local characters = {}
	for _, p in Players:GetPlayers() do
		if p.Character then table.insert(characters, p.Character) end
	end
	params.FilterDescendantsInstances = characters
	for _, zone in CollectionService:GetTagged("KillZone") do
		for _, part in workspace:GetPartsInPart(zone, params) do
			local hum = part.Parent and part.Parent:FindFirstChildOfClass("Humanoid")
			if hum and hum.Health > 0 then hum.Health = 0 end
		end
	end
end)
```

---

## 8. Checkpoints

- Obby: one per stage. Adventure: at every intensity peak and before every hazard sequence longer than ~20 s.
- Checkpoint pads are big, glow, play a sound and a particle burst on first touch, and show "Stage N" feedback.
- Store the checkpoint on the server (attribute on the player + saved in profile data), never trust a client-reported stage. Only advance when the new stage is exactly `current + 1` (or within allowed skips) to stop teleport exploits from skipping to the end.
- On respawn, move the character to the checkpoint in `CharacterAdded` (`character:PivotTo(cp.CFrame + Vector3.new(0, 3, 0))`) after the character is parented.

```lua
-- Server: checkpoint advance with sequence validation
local function onCheckpointTouched(player: Player, stage: number)
	local current = player:GetAttribute("Stage") or 0
	if stage == current + 1 then
		player:SetAttribute("Stage", stage)
		-- persist to profile.Data.Stage; fire a client feedback remote
	end
end
```

---

## 9. Playtesting a layout with MCP

1. `start_stop_play` and `character_navigation` from spawn to each objective in order; record time per leg (`execute_luau` Server reading `os.clock()` attributes, or console prints).
2. `screen_capture` at spawn eye level: is the goal visible?
3. Walk the critical path at 16 studs/s; any leg over 20 s without a goal change or reward is a pacing gap.
4. Jump-test every gap with a human-like approach, not a perfect line.
5. Run with Studio Network Simulation at 200 ms latency for moving platforms and kill zones.

---

## Level design checklist

- [ ] Core action within 15 s, first reward within 30 s of control
- [ ] No popups before the first reward
- [ ] Landmark and next goal visible from every spawn and checkpoint
- [ ] Mechanics introduced safe -> stakes -> combined
- [ ] Intensity alternates every 30-90 s; milestone every 5-10 min
- [ ] Gaps and heights measured against default movement
- [ ] Hazards readable; collisions match visuals; hitboxes forgiving
- [ ] Checkpoints frequent, server-validated, persisted
- [ ] Map edges hidden; no reachable void
- [ ] FTUE funnel steps logged with AnalyticsService

---

## CHANGELOG

- 2026-11-03: New file.
