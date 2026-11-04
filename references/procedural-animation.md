# Animation that sells the verb

Every core action needs a body that does it: an anticipation (wind-up), the action, and a follow-through
(landing, recoil). A character that slides into a jump with its default pose reads as cheap even when
the mechanic is good. The test game's leap uses a crouch while charging, a stretch at take-off, a tuck
in the air, a front flip on long leaps and blossom bounces, and a squash on landing, all procedural.

## Three ways to animate, in order of friction

1. **Procedural poses (no assets, use first).** Overwrite joint `Transform`s every frame in
   `RunService.Stepped` (it runs after the Animator, so the pose wins for that frame). Blend named
   poses by weight. `src/client/Poser.luau` in every project does this (crouch, stretch, tuck, flip,
   wave; add your own). It is client-side and visual only; the server never needs it.
2. **Tweens on parts and models** for everything that isn't a humanoid: pads bob and sink, turtles
   dive, coins spin, doors swing, UI and camera. `TweenService` on the server replicates; cosmetic
   motion belongs on the client.
3. **Keyframed Animation assets** (walk cycles, emotes, NPC idles): authored in Studio's Animation
   Editor and published as an asset to the person's account, then loaded with
   `Animator:LoadAnimation`. Publishing uses their account: ask first. Use Roblox's catalogue
   animations by id where they fit.

## Joints on today's avatars

R15 joints: `LowerTorso.Root`, `UpperTorso.Waist`, `Head.Neck`, `*UpperArm.*Shoulder`,
`*LowerArm.*Elbow`, `*UpperLeg.*Hip`, `*LowerLeg.*Knee`. Newer avatars use **AnimationConstraint**
joints instead of Motor6Ds; both have `Transform`. Code that only looks for `Motor6D` finds nothing and
silently does nothing (the test game lost an hour to this). Find joints by name and accept either class.

Joint space (R15): `CFrame.Angles(+x)` on a hip swings the thigh forward, `-x` on a knee bends it, `+x`
on a shoulder raises the arm forward, `CFrame.new(0, -y, 0)` on Root lowers the body (a crouch).
Rotating Root about X flips the whole body around the hips.

## Making a pose look right

- Anticipation is about 0.15-0.25 s and scales with the action (a bigger charge crouches deeper).
- Stretch at take-off for the first quarter of the flight, then tuck; untuck before landing.
- Flip only on big moments (long leaps, bounces); a flip every jump stops meaning anything.
- Squash for 0.2 s on landing (`sin` in, `sin` out), with a landing sound and a little dust.
- Ease everything (`1 - (1 - x)^3` out, `x^2` in); linear motion reads as robotic.
- Respect `GuiService.ReducedMotionEnabled` and the game's own reduced-motion setting.

## Checking it

A leap lasts 0.6 s, which is too short to catch by timing a capture from the shell. Hold the pose
instead: `Poser` (and the test game's Leap module) reads a `PoseTest` attribute on the player
("crouch", "stretch", "tuck", "flip") and shows that pose until it is cleared. Set it from
`studio luau --ctx Client`, point a scriptable camera at the character's side
(`CFrame.lookAt(root.Position - root.CFrame.RightVector * 8 + root.CFrame.LookVector * 3, root.Position)`),
`studio shot`, and look. Check for bent-backwards knees, arms through the body, and a flip turning the
wrong way. Clear the attribute and return the camera to `Custom` afterwards.
