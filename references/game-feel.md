# Game Feel ("Juice")

Load when an action feels flat, combat lacks impact, UI feels lifeless, or before shipping any core loop. Pairs with `vfx.md` (tools), `audio.md` (sound) and `ui-ux-style.md` (UI).

## The 5 rules that matter most

1. **Respond on the client the same frame.** The player's own input gets visual and audio feedback locally, immediately. Never wait a server round trip (60-200 ms on real connections) to show that a button was pressed or a swing started.
2. **Layer feedback, scale it by importance.** Animation + sound + particles + camera + UI. A coin pickup gets two layers; a boss kill gets all five. If everything shakes, nothing does.
3. **Anticipation, action, recovery.** Short wind-up, fast action, readable settle. Easing does most of this for free.
4. **The server decides outcomes; the client decides presentation.** Predict cosmetics, confirm results, correct quietly when the server disagrees.
5. **Respect the player.** Cap shake and flashes, offer a "reduce motion" toggle, never strobe, and keep the HUD readable during effects.

---

## 1. Latency budget

| Target | Number |
|---|---|
| Feels instant | under ~100 ms from input to first visible response |
| One frame at 60 fps | 16.7 ms |
| Typical Roblox round trip | 60-200 ms; mobile on cellular often worse |
| Button press visual | same frame (client) |
| Hit confirmation | can arrive with the server (100-200 ms) if the swing itself already played locally |

So: client plays the swing animation, whoosh sound and trail on input; server validates and sends back hits; client then plays the impact layer (hit flash, damage number, hit sound). If the server rejects, the impact layer simply never plays.

---

## 2. Tweens, easing and springs

| Use | Duration | Easing |
|---|---|---|
| Button hover/press | 0.08-0.15 s | `Quad` Out |
| Panel open | 0.2-0.3 s | `Back` Out (small overshoot) or `Quint` Out |
| Panel close | 0.12-0.2 s | `Quad` In (exits faster than entries) |
| Reward pop | 0.3-0.45 s | `Back` Out, then settle |
| Camera moves | 0.25-0.6 s | `Sine`/`Quad` InOut |
| Progress bars | 0.2-0.4 s | `Quad` Out; avoid `Linear` except timers |

Tweens are fixed-duration. For anything that is retargeted constantly (camera follow, hover scale, a bar that changes every frame), use a spring: it keeps velocity when the target moves.

```lua
-- ReplicatedStorage/Shared/Spring.luau  (critically-damped-ish, frame-rate independent)
local Spring = {}
Spring.__index = Spring

export type Spring = typeof(setmetatable({} :: {
	position: number, velocity: number, target: number, speed: number, damping: number,
}, Spring))

function Spring.new(initial: number, speed: number?, damping: number?): Spring
	return setmetatable({ position = initial, velocity = 0, target = initial,
		speed = speed or 20, damping = damping or 1 }, Spring)
end

function Spring.step(self: Spring, dt: number): number
	-- semi-implicit Euler with substeps for stability
	local steps = math.max(1, math.ceil(dt / (1 / 240)))
	local h = dt / steps
	for _ = 1, steps do
		local force = (self.target - self.position) * self.speed * self.speed
		local damp = 2 * self.damping * self.speed * self.velocity
		self.velocity += (force - damp) * h
		self.position += self.velocity * h
	end
	return self.position
end

function Spring.impulse(self: Spring, v: number)
	self.velocity += v
end

return Spring
```

Damping 1 settles without overshoot; 0.5-0.7 gives a bouncy, cartoony settle.

---

## 3. Camera: shake and FOV kicks

Apply camera effects after Roblox's camera has updated, so they do not accumulate or fight the camera scripts:

```lua
-- StarterPlayerScripts/CameraFx.client.luau (or a module required by your client bootstrap)
local RunService = game:GetService("RunService")
local camera = workspace.CurrentCamera

local CameraFx = {}
local trauma = 0              -- 0..1; shake = trauma^2
local MAX_ANGLE = math.rad(3) -- cap rotation shake
local MAX_OFFSET = 0.6        -- studs
local DECAY = 1.6             -- trauma per second
local reduceMotion = false
local fovBase = camera.FieldOfView
local fovKick = 0

function CameraFx.addTrauma(amount: number)
	trauma = math.min(1, trauma + amount)
end
function CameraFx.kickFov(degrees: number)
	fovKick = math.max(fovKick, degrees)
end
function CameraFx.setReduceMotion(on: boolean)
	reduceMotion = on
end

RunService:BindToRenderStep("CameraFx", Enum.RenderPriority.Camera.Value + 1, function(dt)
	local t = os.clock()
	if trauma > 0 and not reduceMotion then
		local s = trauma * trauma
		local rx = MAX_ANGLE * s * math.noise(t * 25, 1)
		local ry = MAX_ANGLE * s * math.noise(t * 25, 2)
		local rz = MAX_ANGLE * s * math.noise(t * 25, 3)
		local ox = MAX_OFFSET * s * math.noise(t * 25, 4)
		local oy = MAX_OFFSET * s * math.noise(t * 25, 5)
		camera.CFrame *= CFrame.new(ox, oy, 0) * CFrame.Angles(rx, ry, rz)
	end
	trauma = math.max(0, trauma - DECAY * dt)
	fovKick = fovKick * math.exp(-10 * dt)
	camera.FieldOfView = fovBase + (if reduceMotion then 0 else fovKick)
end)

return CameraFx
```

Suggested trauma: light hit taken 0.15, heavy hit 0.35, explosion nearby 0.6, never 1.0 for routine events. FOV: sprint +6 to +10 (spring, not snap), dash +4 kick, hit-taken +2. Default FOV is 70.

---

## 4. Hit-stop

A 50-120 ms freeze on impact makes hits feel heavy. Roblox has no global time scale; freeze the relevant animation tracks on the client:

```lua
local function hitStop(tracks: { AnimationTrack }, duration: number)
	local speeds = {}
	for i, track in tracks do
		speeds[i] = track.Speed
		track:AdjustSpeed(0)
	end
	task.delay(duration, function()
		for i, track in tracks do
			if track.IsPlaying then track:AdjustSpeed(speeds[i]) end
		end
	end)
end
-- light hit 0.05 s, heavy 0.09 s, finisher 0.12 s. Apply to attacker and victim tracks on the attacker's client.
```

Do not freeze server physics or other players' characters for hit-stop; it is purely presentational.

---

## 5. Particles, beams, trails, highlights

- **Bursts**: one pre-made emitter per effect type, `Rate = 0`, call `:Emit(n)`. Typical: hit sparks 8-15, coin pickup 6-10, level-up 40-80.
- **Place at the contact point**: keep an anchored, invisible, `CanQuery = false` "FX" part in a client folder; move an `Attachment` to the hit position and emit from it.
- **Flipbooks** (`FlipbookLayout`, `FlipbookMode`, `FlipbookFramerate`) make smoke, slashes and explosions look authored instead of blobby. Use 4x4 or 8x8 sheets.
- **Trails** for swings and dashes: `Lifetime` 0.15-0.3 s, width tapering to 0, `LightEmission` 0.5-1.
- **Beams** for tethers, lasers and shockwave rings.
- **Hit flash**: a `Highlight` on the target model with `FillTransparency` tweened 0.2 -> 1 over 0.15 s (`DepthMode = Occluded`). Remember the 31 simultaneous Highlight limit; reuse one per target.
- **Scale with magnitude**: crits get 2x particles, a bigger number, a deeper sound layer and +0.1 trauma.

See `vfx.md` for property tables and budgets.

---

## 6. Sound layering

Every meaningful action has a sound; important ones have layers:

- **Transient** (click, crack, the first 30 ms) + **body** (thud, whoosh) + **tail** (debris, ring-out, coin jingle).
- Randomise pitch +/-5-10% and volume +/-10% per play; rotate between 2-4 variants for repeated actions (footsteps, coins).
- Duck music 3-6 dB for big moments (boss, reward reveal).
- Rising pitch on combos and streaks (each consecutive pickup +1 semitone, reset after 1 s).

API details and mixing live in `audio.md`.

---

## 7. UI micro-animation

Press and hover with `UIScale` (does not fight layouts):

```lua
local TweenService = game:GetService("TweenService")

local function addPressFeel(button: GuiButton)
	local scale = button:FindFirstChildOfClass("UIScale") or Instance.new("UIScale")
	scale.Parent = button
	local function to(v: number, t: number, style: Enum.EasingStyle)
		TweenService:Create(scale, TweenInfo.new(t, style, Enum.EasingDirection.Out), { Scale = v }):Play()
	end
	button.MouseEnter:Connect(function() to(1.05, 0.1, Enum.EasingStyle.Quad) end)
	button.MouseLeave:Connect(function() to(1, 0.1, Enum.EasingStyle.Quad) end)
	button.MouseButton1Down:Connect(function() to(0.92, 0.06, Enum.EasingStyle.Quad) end)
	button.MouseButton1Up:Connect(function() to(1, 0.25, Enum.EasingStyle.Back) end)
end
```

`MouseButton1Down/Up` fire for touch too; keep game logic on `Activated`.

Counter roll-up (numbers count instead of jumping):

```lua
local function rollNumber(label: TextLabel, from: number, to: number, duration: number)
	local value = Instance.new("NumberValue")
	value.Value = from
	value:GetPropertyChangedSignal("Value"):Connect(function()
		label.Text = string.format("%d", math.floor(value.Value + 0.5))
	end)
	local tween = TweenService:Create(value, TweenInfo.new(duration, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Value = to })
	tween.Completed:Once(function() value:Destroy() end)
	tween:Play()
end
```

Currency fly-to-counter (world pickup -> HUD counter):

```lua
local camera = workspace.CurrentCamera

-- iconTemplate: ImageLabel with AnchorPoint (0.5, 0.5).
-- flyLayer: a full-size, transparent Frame in the SAME ScreenGui as the counter, so both
-- AbsolutePositions share one coordinate space. WorldToScreenPoint accounts for the top-bar inset.
-- Verify alignment once with a screen_capture; ScreenInsets settings can shift the space.
local function flyToCounter(worldPos: Vector3, counter: GuiObject, iconTemplate: ImageLabel, flyLayer: Frame, count: number, onArrive: () -> ())
	local screen, onScreen = camera:WorldToScreenPoint(worldPos)
	if not onScreen then onArrive() return end
	local origin = flyLayer.AbsolutePosition
	local start = Vector2.new(screen.X, screen.Y) - origin
	local target = counter.AbsolutePosition + counter.AbsoluteSize / 2 - origin
	for i = 1, count do
		local icon = iconTemplate:Clone()
		icon.Position = UDim2.fromOffset(start.X + math.random(-30, 30), start.Y + math.random(-30, 30))
		icon.Parent = flyLayer
		task.delay((i - 1) * 0.04, function()
			local t = TweenService:Create(icon, TweenInfo.new(0.45, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
				{ Position = UDim2.fromOffset(target.X, target.Y), Size = icon.Size - UDim2.fromOffset(8, 8) })
			t.Completed:Once(function()
				icon:Destroy()
				if i == count then onArrive() end -- pulse the counter + play a tick sound here
			end)
			t:Play()
		end)
	end
end
```

Keep 5-12 icons per pickup; more turns into noise. On arrival, pop the counter (`UIScale` 1 -> 1.15 -> 1) and roll the number.

Damage/number popups: a pooled `BillboardGui` (`AlwaysOnTop = true`, `MaxDistance` ~80) with a `TextLabel`; tween `StudsOffset` up 2-3 studs and `TextTransparency` to 1 over 0.6-0.8 s; start at 1.3x scale and settle to 1x in 0.1 s. Crits: bigger, warmer colour, slight rotation.

---

## 8. Screen-space feedback

- **Damage vignette**: full-screen `ImageLabel` with a radial red texture, `ImageTransparency` 0.6 -> 1 over 0.4 s. Strength by damage fraction.
- **Low health**: tween `ColorCorrectionEffect.Saturation` toward -0.5 and add a slow heartbeat sound under 25% HP. Restore smoothly on heal.
- **Pickup flash**: tiny white flash on the counter, not the whole screen.
- **Never** full-screen white flashes for routine events; reserve for explosions and keep under 0.15 s.

---

## 9. Haptics

`HapticEffect` is the current API (works across gamepads and supported phones); `HapticService:SetMotor` is legacy.

```lua
local effect = Instance.new("HapticEffect")
effect.Type = Enum.HapticEffectType.GameplayCollision -- also UIHover, UIClick, UINotification, GameplayExplosion, Custom
effect.Parent = workspace
effect:Play()
```

- Custom waveforms: `Type = Custom` then `SetWaveformKeys({ FloatCurveKey.new(ms, intensity0to1, Enum.KeyInterpolationMode.Linear), ... })`.
- UI buttons have `HoverHapticEffect` / `PressHapticEffect` properties for no-code haptics.
- Keep haptics short (under 300 ms for hits), reserve strong ones for big events, and expose an off switch.

https://create.roblox.com/docs/en-us/reference/engine/classes/HapticEffect.md

---

## 10. Client prediction with server authority

Default (no Server Authority mode):

1. Client: on input, play animation, swing sound, trail; send intent (`AttackRemote:FireServer()`).
2. Server: validate cooldown/state/range, run the hitbox, apply damage, tell relevant clients.
3. Clients: play impact layers on confirmation.
4. Optimistic UI: for a purchase, show a "pending" state, not a fake success; for currency gains you can tick the counter immediately and correct to the server value when it arrives.

With `Workspace.AuthorityMode = Server` (Server Authority, full release July 2026): movement and simulation logic run inside `RunService:BindToSimulation()` on both sides with rollback; cosmetic effects go in `RenderStepped` and must be undoable if mispredicted (do not spawn permanent debris from a predicted hit). Inputs that affect simulation must come through `InputAction`s. See `architecture.md` and https://create.roblox.com/docs/en-us/projects/server-authority.md

---

## Juice checklist per action

- [ ] Local visual response in the same frame
- [ ] Sound with pitch/volume variation
- [ ] Particles or a flash at the point of contact
- [ ] Camera response proportional to importance (or none)
- [ ] UI response (counter, popup, bar) with easing
- [ ] Server confirmation path and graceful rejection
- [ ] Reduced-motion setting honoured

---

## CHANGELOG

- 2026-11-03: New file.
