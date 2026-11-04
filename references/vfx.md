# Visual effects and animation assets

Effects tell the player what just happened. Every important event gets a visual, a sound and, where it
fits, a camera response; unimportant events get nothing, so the important ones read.
`game-feel.md` covers timing and juice; `procedural-animation.md` covers posing characters from code.
This file is the toolbox.

## Particles

- `ParticleEmitter` on an `Attachment`. For bursts: `Enabled = false`, then `:Emit(n)`.
- Keep `Rate` low and `Lifetime` short (0.3-1 s for impacts); use `Size` and `Transparency`
  `NumberSequence`s to grow and fade instead of more particles.
- `LightEmission` 0.3-1 for glows, 0 for dust and water. `LightInfluence` 0 makes them ignore scene
  light (good for magic, bad for smoke).
- `Squash` (stretch along velocity) and `FlipbookLayout` (animated textures) make a few particles look
  like many.
- A burst pool: one attachment with emitters under the camera or a client folder, moved to the event
  position and emitted, instead of creating instances per event.

## Trails and beams

- `Trail` between two attachments on a moving part (sword arc, dash). `Lifetime` 0.1-0.3 s;
  `WidthScale` tapering to 0; enable only during the action.
- `Beam` between attachments for lasers, ropes, aim previews and connections; `CurveSize0/1` for arcs,
  `Segments` 10-20, `TextureSpeed` for flow.

## Highlights, lights and post

- `Highlight` outlines an object through walls (selection, objectives). Few at once; there is a limit
  and they cost on phones.
- `PointLight` / `SpotLight` for a flash: tween `Brightness` up and back in 0.15 s.
- Post effects (`ColorCorrectionEffect`, `BloomEffect`, `BlurEffect`, `DepthOfFieldEffect`) on
  `Lighting` or the camera: a quick tint on damage, a blur behind modals. Tween them, never toggle.

## Tweens

- `TweenService:Create(obj, TweenInfo.new(t, style, direction), goals)`. Back-out for pops, Quad
  in-out for moves, Sine for loops, Elastic rarely.
- Track tweens per object and `:Cancel()` them before starting a conflicting one or when resetting
  the object (a sink tween finishing after a reset left a platform underwater).
- Animate models with `PivotTo` from `RenderStepped` / `Heartbeat` (a tween on a CFrameValue) or tween
  the primary part of a welded, unanchored model.

## Character animation assets

- `Animator:LoadAnimation(animation)` returns an `AnimationTrack`; `:Play(fadeTime, weight, speed)`.
  Load once per character and reuse.
- Priorities: Core < Idle < Movement < Action (Action2-4 above). A higher priority overrides lower
  ones on the joints it animates.
- `AnimationTrack:GetMarkerReachedSignal("Hit")` syncs damage and sounds to the animation.
- Animations must be owned by the experience's owner (user or group) or they fail silently in the
  published game. Upload them under the same owner as the place.
- No assets yet? Pose the joints from code (`procedural-animation.md`); it ships today and is easy to
  tune.

## Camera effects

- Shake: offset the camera CFrame by small noise for 0.1-0.3 s, scaled by intensity; stack requests
  and decay. Respect reduced motion.
- FOV punch: tween `FieldOfView` +5-10 and back for speed or impact.
- Never fight the player's camera during play except for a short framing tween after a teleport or
  landing.

## Budget

Effects are client-side. Cap simultaneous emitters, pool everything, and check a busy moment in the
MicroProfiler on a phone (`performance.md`). If a moment is unreadable in a capture, it's too much.
