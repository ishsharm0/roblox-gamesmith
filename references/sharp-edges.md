# Sharp edges: symptoms, causes, fixes

Look up the symptom. Each row is something that actually goes wrong in Roblox projects; the ones
marked **(verified)** were hit and fixed while building Lily Pad Leap (`reference-game.md`).

## Gameplay and physics
- **Reflective terrain water goes white.** With a low gameplay camera, `WaterReflectance` above about 0.05
  mirrors the sky and the pond becomes a pale sheet that hides everything floating on it. Keep it near 0.03
  and get the colour from `WaterColor`.
- **A low sun over a pond is mud.** At ClockTime 17+ with hills around the water, their shadows cover the
  whole surface and a warm grade turns the water brown. For "golden hour" over water stay near 16 and keep
  the water itself turquoise.
- **Clear water over pale sand washes out.** Open water with nothing around it and `WaterTransparency` above
  about 0.25 reads white-mint, and pale pads vanish on it. Keep open water deeper in colour (0.15-0.22).
- **A chase camera needs a latch.** "Follow the ball while it is fast and far from the target" comes true
  again when the ball flies out the far side, and the camera dives under the table. Chase only until the
  first arrival, then stay on the wide shot for the rest of the shot.
- **ClockTime past about 18 is night**, not dusk, and a Sky with fixed textures ignores the time of day. For
  sunset and dusk stay at 17.3-17.7 and do the colour with ColorCorrection tint and Atmosphere.

| Symptom | Cause | Fix |
|---|---|---|
| Pose code does nothing **(verified)** | newer avatars use `AnimationConstraint` joints, not `Motor6D` | find joints by name and accept either class |
| A scripted leap brakes or stops mid-air **(verified)** | Humanoid air control fights the velocity | put the Humanoid in `HumanoidStateType.Physics` for the flight, hold it upright with `AlignOrientation`, restore on landing |
| The player "lands" in mid-air and drops **(verified)** | the landing raycast hit scenery under the arc | raycast only against landable parts, and only while descending |
| A press right after landing is ignored **(verified)** | the landing bounce reads as airborne | ray-based grounded check plus an input buffer (~0.35 s) |
| A swimming player never respawns **(verified)** | a swimmer's root floats near the surface, above a low fall threshold | put the fall line just under standing height, or check the Swimming state |
| A reset platform is still sunk **(verified)** | a running tween finished after the reset | keep each object's tweens; `:Cancel()` them when restoring |
| A quick press after landing hops in place **(verified)** | the client aims at "the next objective" from server-published progress, which lags the landing by ~0.3 s | let the client count its own landing for targeting (the server still decides progress) |
| A moving target is luck to hit **(verified)** | aim assist aims at where it is, not where it will be | lead by sampled velocity x flight time |
| First action after a respawn goes the wrong way | the camera still faces where the player fell | reframe the camera on every teleport |
| Touched fires many times or not at all | Touched fires per part contact, and not for anchored-to-anchored or CFrame moves | debounce per character; use spatial queries (`GetPartsInPart`) for zones |
| Characters fling or jitter on moving platforms | platform moved by CFrame each frame | move with `AlignPosition`/`PrismaticConstraint`, or carry the character's offset yourself |
| NPCs stutter | network ownership flips between nearby players | `part:SetNetworkOwner(nil)` on NPC assemblies |
| Parts fall through the map on join | unanchored parts before terrain/streaming loaded | anchor scenery; spawn players above solid ground |

## Scripts and data model

| Symptom | Cause | Fix |
|---|---|---|
| Results screen shows old numbers **(verified)** | the client switched screens on `Phase` before the other attributes arrived | set the phase attribute last |
| `WaitForChild` warning, then nil | name typo, or the instance is streamed out | check names; with streaming, wait with a timeout and handle absence |
| A LocalScript never runs | it's in Workspace or ServerStorage | LocalScripts run in StarterPlayerScripts, StarterCharacterScripts, StarterGui, a tool, or the character |
| UI disappears on respawn | ScreenGui `ResetOnSpawn = true` (default) | set it false for UI built from code |
| Server freezes | an unyielding loop or a `RemoteFunction` invoked on a client that never returns | yield in loops; never invoke clients |
| Memory climbs all session | connections and per-player tables never cleaned | disconnect on `PlayerRemoving`; destroy clones |
| `attempt to index nil` on a player | they left during a yield | re-check `player.Parent` after every yield |
| Two scripts fight over a property | no single owner | one module owns each system's state |
| `require` hangs | circular requires | pass dependencies to `init()` instead |
| A global appears from nowhere **(verified)** | assigning to a name declared further down the file | declare locals before use; Selene flags it |

## Data and money

| Symptom | Cause | Fix |
|---|---|---|
| Items duplicate or vanish on fast rejoin | two servers wrote the same key | session-locked profiles (`data.md`) |
| Save silently lost | `SetAsync` failed during an outage, no retry | autosave with retries; ProfileStore |
| A product granted twice, or never | `ProcessReceipt` not idempotent, or returned before saving | the receipt pattern (`receipts.md`) |
| Game pass perk only after rejoin | only checked at join | also grant on `PromptGamePassPurchaseFinished` |
| DataStore errors in Studio | API access off or place unpublished | enable Studio API access, or use the mock |

## UI
- **One shared "latest toast" ticket hides nothing.** A stage banner and a PERFECT popup shared one
  counter for "am I still the newest message"; the popup bumped it, so the banner's hide never ran and it
  covered the course for a whole stage. Give each message slot its own ticket. The play sheet catches this;
  a UI tour does not, because it shows one message at a time.

| Symptom | Cause | Fix |
|---|---|---|
| Text stops growing past 100 **(verified)** | `TextSize` and `TextScaled` cap at 100 | 100, then a `UIScale` on the label |
| A world label never shows in captures **(verified)** | a BillboardGui under PlayerGui | parent client world GUIs to the camera or a client folder in Workspace |
| Buttons too small on phones | offset sizes without a global scale | one reference canvas + UIScale (`ui-engineering.md`) |
| Buttons hidden under the notch | full-bleed ScreenGui for interactive UI | `ScreenInsets = DeviceSafeInsets` |
| Clicks go through a modal to the world | nothing sinks input | full-screen transparent button behind modals |
| Gamepad can't reach a button | `Selectable` false or no `SelectedObject` | set selection when a screen opens |
| UI shows a stale count ("17 dewdrops" for 23) **(verified)** | a number typed into UI text | compute every count and threshold shown in UI from config or layout data |
| A full-width panel is cut off on small screens **(verified)** | the global UIScale had a floor (0.6) above what the screen needs | floor no higher than 0.45; check a 568x320 viewport |
| A world sign prints over the HUD title **(verified)** | a BillboardGui on a gate or arch sits at top centre when you face it | no world label where the HUD already says it; `MaxDistance` under 30 for the rest |
| A collapse shows a pile of unreadable "+30"s **(verified)** | one popup per scored object | merge scores that land within about 0.25 s into one popup with the total |
| Popups rise into a fixed HUD label **(verified)** | world-anchored popups clamp only to the screen edge | clamp their start below the label's zone, and keep the rise short |
| A level banner names the previous level **(verified)** | it read attributes when `Phase` changed, before the new level's attributes arrived | update the banner from each attribute's own changed signal |
| A tour stalls on a phone screen **(verified)** | Studio's simulated taps can miss on the device simulator | after a click step, fire the same remote as a fallback (ignored if the click worked) |

## Studio and tooling

| Symptom | Cause | Fix |
|---|---|---|
| `Lighting.Technology` errors **(verified)** | not scriptable from plugins or MCP | set it in `default.project.json` |
| Save of a big map fails **(verified)** | MCP text results are cut at ~100k characters | the `studio` CLI exports in 60k chunks |
| MCP call times out **(verified)** | the call ran over ~5 minutes | `task.spawn` the work, poll an attribute |
| Studio disconnects mid-build | an unyielding loop | `task.wait()` between chunks |
| World edits lost | Studio closed without exporting | `rbxgame save` (open does it first) |
| Animations work in Studio, not live | the animation belongs to another owner | upload under the place's owner |
| Sounds silent live | audio asset not permitted for the experience | use Roblox/owned audio; check asset permissions |

## Content and policy

| Symptom | Cause | Fix |
|---|---|---|
| Game moderated | unfiltered player text, off-platform links, wrong maturity rating | filter all shown text; fill the questionnaire honestly |
| Inserted model does strange things | a hidden script (backdoor) | audit every inserted asset (`security.md`) |
- **StreamingEnabled on a small arena.** The template turns streaming on (right for big worlds). On a
  small single-arena game it buys nothing and makes distant parts absent on the client, so a client bot,
  a scripted camera or an aim raycast can find nil where the server sees a part. For an arena under
  about 1,000 studs across, set `"StreamingEnabled": false` in `default.project.json`, or `WaitForChild`
  and `Player:RequestStreamAroundAsync` before reading far instances. (Found in the Topple Toys cold build.)
- **Captures while another Studio window is playing.** With two Studio windows on one machine, a
  `screen_capture` of one window hangs while the other is in Play (seen repeatedly on 2026-11-11/12:
  every shot of a tour timed out). Run playtests and tours for one project at a time per machine; tours
  now time each shot out after 120 s instead of waiting forever.
