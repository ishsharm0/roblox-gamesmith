--!strict
-- Three buses (Music, Sfx, Ui) and a table of named sounds. Every sound here is a built-in
-- rbxasset:// placeholder pitched into a small family; swap an entry's `id` for a Creator Store
-- "rbxassetid://<id>" when the game is real (references/audio.md), and set MUSIC_ID for a music bed.
-- A new game renames the sounds to its own verbs and keeps play(name, pitch?).
local SoundService = game:GetService("SoundService")
local Debris = game:GetService("Debris")

local MUSIC_ID = "" -- a Creator Store track as "rbxassetid://<id>"; empty means no music
local MUSIC_VOLUME = 0.35

type Entry = { id: string, bus: string, volume: number, pitch: number }

local SOUNDS: { [string]: Entry } = {
	click = { id = "rbxasset://sounds/volume_slider.ogg", bus = "Ui", volume = 0.5, pitch = 1.3 },
	release = { id = "rbxasset://sounds/action_get_up.mp3", bus = "Sfx", volume = 0.35, pitch = 1.8 },
	perfect = { id = "rbxasset://sounds/action_jump.mp3", bus = "Sfx", volume = 0.6, pitch = 1.5 },
	good = { id = "rbxasset://sounds/action_jump_land.mp3", bus = "Sfx", volume = 0.5, pitch = 1.2 },
	miss = { id = "rbxasset://sounds/impact_water.mp3", bus = "Sfx", volume = 0.5, pitch = 0.8 },
	star = { id = "rbxasset://sounds/volume_slider.ogg", bus = "Ui", volume = 0.7, pitch = 1 },
	finish = { id = "rbxasset://sounds/impact_explosion_03.mp3", bus = "Sfx", volume = 0.25, pitch = 1.6 },
}

local Audio = {}
local buses: { [string]: SoundGroup } = {}

function Audio.start()
	for _, name in { "Music", "Sfx", "Ui" } do
		local group = Instance.new("SoundGroup")
		group.Name = name
		group.Parent = SoundService
		buses[name] = group
	end
	if MUSIC_ID ~= "" then
		local music = Instance.new("Sound")
		music.Name = "MusicBed"
		music.SoundId = MUSIC_ID
		music.Looped = true
		music.Volume = MUSIC_VOLUME
		music.SoundGroup = buses.Music
		music.Parent = SoundService
		music:Play()
	end
end

-- 0..1 per bus, for a settings screen.
function Audio.setVolume(bus: string, volume: number)
	local group = buses[bus]
	if group then
		group.Volume = math.clamp(volume, 0, 1)
	end
end

-- Play a named sound once. `pitch` multiplies the entry's own (1 = as listed).
function Audio.play(name: string, pitch: number?)
	local entry = SOUNDS[name]
	if not entry then
		return
	end
	local sound = Instance.new("Sound")
	sound.SoundId = entry.id
	sound.Volume = entry.volume
	sound.PlaybackSpeed = math.clamp(entry.pitch * (pitch or 1), 0.5, 2.5)
	sound.SoundGroup = buses[entry.bus]
	sound.Parent = SoundService
	sound:Play()
	Debris:AddItem(sound, 4)
end

-- The multiplier for a streak: each hit in a row is a little higher, up to an octave.
function Audio.comboPitch(combo: number): number
	return 1 + math.min(combo, 10) * 0.1
end

return Audio
