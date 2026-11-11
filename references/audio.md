# Audio

Load when adding music, sound effects, ambience, voice-aware mixing, or a volume settings menu.

## The 5 rules that matter most

1. **Use the audio object graph for new work.** `AudioPlayer` -> `Wire` -> effects -> `AudioDeviceOutput` (2D) or `AudioEmitter` (3D). Roblox docs now call `Sound`/`SoundGroup`/`SoundEffect` "discouraged" for new work. https://create.roblox.com/docs/en-us/audio/objects.md
2. **Only use audio you have the right to use.** Your own recordings, Roblox and partner audio from the Creator Store, or audio licensed for this use. Never upload commercial music you do not own.
3. **Every interaction makes a sound.** Silent buttons, pickups and hits feel broken. Budget one sound per verb at minimum.
4. **Mix in buses.** Music, SFX, UI, ambience each go through their own fader so players (and you) can balance them. Music sits under SFX.
5. **Music follows place and state.** A bed per zone, crossfaded; layers or stingers for combat, rewards and danger.

---

## 1. Object graph basics

| Object | Role |
|---|---|
| `AudioPlayer` | Plays an asset. Key props: `Asset` (ContentId; `AssetId` is deprecated), `Volume` (0-10), `Looping`, `PlaybackSpeed`, `TimePosition`, `LoopRegion`, `PlaybackRegion`, `AutoPlay`, `IsReady`. Methods `Play()`, `Stop()`. Events `Ended`, `Looped`. |
| `Wire` | Connects `SourceInstance` -> `TargetInstance` (optionally `SourceName`/`TargetName` pins). |
| `AudioDeviceOutput` | The player's speakers/headphones. |
| `AudioEmitter` | Virtual speaker on a part/attachment; positional. Distance falloff via its attenuation curve. |
| `AudioListener` | Virtual microphone (camera or character), wired to an `AudioDeviceOutput`. SoundService's listener location setting (Character/Camera) creates the default one. |
| Effects | `AudioFader` (bus volume), `AudioEqualizer`, `AudioCompressor`, `AudioReverb`, `AudioFilter`, `AudioEcho`, `AudioPitchShifter` and more; insert between player and output. |
| `AudioDeviceInput` | A player's microphone (voice chat). |

https://create.roblox.com/docs/en-us/reference/engine/classes/AudioPlayer.md

### 2D music/UI sound

```lua
-- Client (LocalScript or RunContext=Client). Builds: player -> bus fader -> master fader -> output
local SoundService = game:GetService("SoundService")

local function wire(from: Instance, to: Instance)
	local w = Instance.new("Wire")
	w.SourceInstance = from
	w.TargetInstance = to
	w.Parent = to
	return w
end

local output = Instance.new("AudioDeviceOutput")
output.Parent = SoundService

local master = Instance.new("AudioFader"); master.Name = "Master"; master.Parent = SoundService
wire(master, output)

local buses = {}
for _, name in { "Music", "SFX", "UI", "Ambience" } do
	local fader = Instance.new("AudioFader")
	fader.Name = name
	fader.Parent = SoundService
	wire(fader, master)
	buses[name] = fader
end

local function newPlayer(assetId: string, bus: string, looping: boolean?): AudioPlayer
	local p = Instance.new("AudioPlayer")
	p.Asset = assetId
	p.Looping = looping or false
	p.Parent = buses[bus]
	wire(p, buses[bus])
	return p
end

local theme = newPlayer("rbxassetid://0000000000", "Music", true)
theme.Volume = 0.5
theme:Play()
```

Settings menu: set `buses.Music.Volume` etc. (0-1 for a slider; save to the player's profile).

### 3D positional sound

```lua
-- Attach to a world object (waterfall, machine, NPC). Runs on the client for cosmetic sounds.
local function emitterOn(part: BasePart, assetId: string, looping: boolean): AudioPlayer
	local emitter = Instance.new("AudioEmitter")
	emitter.Parent = part
	local player = Instance.new("AudioPlayer")
	player.Asset = assetId
	player.Looping = looping
	player.Parent = part
	local w = Instance.new("Wire")
	w.SourceInstance = player
	w.TargetInstance = emitter
	w.Parent = emitter
	return player
end
```

Shape falloff with the emitter's distance attenuation curve (volume per distance); keep important gameplay sounds audible to 60-100 studs and ambience to 20-40.

### When `Sound` is still fine

`Sound` (with `SoundGroup`) still works and is what clicking a Creator Store audio asset inserts. For a quick prototype or existing code, keep it: `Sound.SoundId`, `Volume`, `RollOffMinDistance`/`RollOffMaxDistance`, `RollOffMode = InverseTapered`, parent to a part for 3D. Migrate when you need buses, effects chains or precise control. Do not mix both systems for the same category, or your settings sliders will only control half the sounds.

---

## 2. Where audio comes from and licensing

| Source | Allowed | Notes |
|---|---|---|
| Your own recordings/compositions | Yes | Upload via Asset Manager, Creator Dashboard or Open Cloud |
| Creator Store audio by Roblox and its music/SFX partners | Yes, inside Roblox experiences | Over 100,000 tracks/SFX. Check the asset page before using in off-platform trailers |
| Creator Store audio from other creators | Only if distributed publicly | Private audio from others will not play in your experience |
| CC0 / royalty-free libraries (e.g. Kenney audio, Sonniss GDC bundles, freesound CC0) | Yes if the licence allows commercial use and redistribution inside a game | Keep a `CREDITS.md` with source and licence per file |
| Commercial songs, game rips, "no copyright" YouTube music | No | Copyright strikes remove the audio and can action the account |

**Finding a sound from the shell (no upload, no asset id to hand):**

```bash
studio call search_asset '{"query":"wooden block impact","assetType":"Audio","scope":"creator_store","audioMaxDuration":3}'
studio call search_asset '{"query":"calm marimba loop","assetType":"Audio","scope":"creator_store","audioMinDuration":40}'
```

Each hit has a name, creator and id; use it as `rbxassetid://<id>`. Prefer hits by Roblox and its partners
(APM Music, Pro Sound Effects, Monstercat): they are public and licensed for experiences. Take two or
three candidates per sound, and note in NOTES.md that they were chosen by name and need a listen. Search
for the action, not the object ("short pop", "soft thud", "coin pickup bright"); cap effects at 3 s.

**Built-in fallbacks** ship with every client and need no search: `rbxasset://sounds/action_jump.mp3`,
`action_jump_land.mp3`, `action_get_up.mp3`, `action_falling.mp3`, `impact_water.mp3`,
`impact_explosion_03.mp3`, `volume_slider.ogg` (a clean tick). Pitch them with `PlaybackSpeed` (0.5 to
2.5) to get a family of sounds from one file: a rising pitch per combo step, a low thud from a landing.
They are placeholders for a prototype; a finished game uses Creator Store sounds and a music bed.

Upload rules: you must hold the rights; single track `.mp3`/`.ogg`/`.wav`/`.flac`; under 20 MB and 7 minutes; 48 kHz or lower; mono/stereo/3.0/5.1. ID-verified accounts can import 2,000 audio assets per 30 days, unverified 100. Uploaded audio is private to you until you grant use to specific experiences/users. https://create.roblox.com/docs/en-us/audio/assets.md

No AI-generated music or voice for this user unless they opt in (`AudioTextToSpeech` exists; treat it like other generation tools: off by default).

---

## 3. Music by zone and state

- **One bed per zone**: hub, each biome, shop, boss room. Different key/tempo/instrumentation so players feel the transition.
- **Crossfade** 1.5-3 s between beds when the player crosses a zone boundary (client-side, using a region check or tagged `ZoneVolume` parts). Never hard-cut except for deliberate shocks.
- **Layers/stems**: author 2-3 stems of the same length and tempo (base, percussion, intensity). Start all together at volume 0, then fade layers in/out with game state (enemies nearby, timer under 30 s). Keep them in sync by starting them in the same frame and restarting together on `Looped`.
- **Stingers**: 1-4 s cues for level-up, rare drop, round start/end, death. Duck the music bus 4-6 dB under them.
- **Silence is a tool**: horror and tension moments work better with ambience only.
- **Volume**: music bus ~0.4-0.6 of SFX loudness; players should hear footsteps and pickups over it.

```lua
local TweenService = game:GetService("TweenService")
local function crossfade(from: AudioPlayer?, to: AudioPlayer, seconds: number, targetVolume: number)
	to.Volume = 0
	if not to.IsPlaying then to:Play() end
	TweenService:Create(to, TweenInfo.new(seconds), { Volume = targetVolume }):Play()
	if from then
		local t = TweenService:Create(from, TweenInfo.new(seconds), { Volume = 0 })
		t.Completed:Once(function() from:Stop() end)
		t:Play()
	end
end
```

---

## 4. SFX for every interaction

| Interaction | Sound | Notes |
|---|---|---|
| UI hover / click / back | soft tick / click / lower click | Short (<100 ms), UI bus, no reverb |
| Open / close panel | whoosh up / down | 150-300 ms |
| Purchase success / fail | cash register or chime / dull buzz | Fail is quieter than success |
| Currency pickup | bright tick, pitch rising with streak | Variants, +1 semitone per consecutive pickup |
| Footsteps | per material (grass, wood, stone, metal, water) | 3-4 variants each, pitch +/-8% |
| Jump / land | small grunt or cloth / thud scaled by fall speed | |
| Swing / hit / crit / block | whoosh / impact / heavier layered impact / metallic clang | See `game-feel.md` layering |
| Damage taken / low health | hurt + vignette / heartbeat loop | |
| Checkpoint / level-up / unlock | stinger | Duck music |
| Door, chest, lever, prompt | mechanical one-shots | Trigger on `ProximityPrompt.Triggered` client-side for instant feedback |
| Ambience | wind, birds, crowd, machinery | Looping, positional where it has a source |

---

## 5. Mixing guide

| Bus | Relative level | Processing |
|---|---|---|
| SFX (gameplay) | Loudest; reference | Light compression on the bus |
| UI | ~ -6 dB vs SFX | Dry |
| Music | ~ -8 to -12 dB vs SFX | Duck under stingers/dialogue |
| Ambience | ~ -12 to -18 dB vs SFX | Low-pass when indoors/underwater |

- Normalise source files before upload (around -14 to -16 LUFS integrated for music, peaks under -1 dBFS) so in-game `Volume` values stay in a sane 0.3-1 range.
- Never set `Volume` above ~2 to fix a quiet file; re-export it instead.
- Cap simultaneous one-shots per type (e.g. 4 coin sounds at once); skip or steal the oldest.
- Leave headroom for voice chat; do not run constant loud music in social games.
- Reverb per space: small for rooms, large for caves/halls (`AudioReverb` on an ambience/SFX bus switched by zone).

---

## 6. Performance and loading

- Preload critical short sounds (UI, hits) with `ContentProvider:PreloadAsync` during the loading screen; stream long music.
- Reuse players for frequent one-shots (a pool of 4-8 per sound) instead of creating and destroying instances each time.
- Cosmetic sounds play on the client; the server only tells clients that something happened.
- Positional loops far from the player should stop or be streamed out with their model.

---

## Audio checklist

- [ ] All assets owned, Roblox/partner, or licensed; `CREDITS.md` maintained
- [ ] Graph: players -> bus faders -> master -> output; settings sliders wired to buses
- [ ] Every verb has a sound; repeated sounds have variants and pitch variation
- [ ] Zone music beds crossfade; stingers duck music
- [ ] Footsteps per material if the game is walking-heavy
- [ ] Levels balanced: SFX > UI > music > ambience; no clipping
- [ ] Critical sounds preloaded; one-shots pooled

---

## CHANGELOG

- 2026-11-03: New file. Audio object graph (`AudioPlayer.Asset`, `Wire`, `AudioFader` buses) as default; `Sound` documented as discouraged-but-working.
