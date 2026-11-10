--!strict
-- Zones that look like different places. Give each zone of the game a look (time of day, air, water,
-- grade) and call Mood.Start: when the player's zone attribute changes, the world glides to that look.
-- Without this, "world 2" is the same picture as world 1 with a harder number.
--   require(script.Parent.Mood).Start("Stage", { looks... })   -- attribute name on the LocalPlayer
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")

local Mood = {}

export type Look = {
	clock: number, -- ClockTime: 10-14 clear day, 16.5-17.4 golden hour, 17.5-17.8 dusk; past ~18 is night
	brightness: number,
	exposure: number,
	shift: Color3, -- ColorShift_Top, the sun's colour on lit faces
	air: Color3, -- Atmosphere.Color
	decay: Color3, -- Atmosphere.Decay
	haze: number,
	density: number,
	water: Color3?,
	waterAlpha: number?,
	tint: Color3, -- ColorCorrection.TintColor: the strongest lever when the Sky has fixed textures
	saturation: number,
	contrast: number,
}

local function tween(inst: Instance, seconds: number, goal: { [string]: any })
	TweenService:Create(inst, TweenInfo.new(seconds, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut), goal)
		:Play()
end

function Mood.Apply(look: Look, seconds: number)
	local atmosphere = Lighting:FindFirstChildOfClass("Atmosphere")
	local grade = Lighting:FindFirstChildOfClass("ColorCorrectionEffect")
	tween(Lighting, seconds, {
		ClockTime = look.clock,
		Brightness = look.brightness,
		ExposureCompensation = look.exposure,
		ColorShift_Top = look.shift,
	})
	if atmosphere then
		tween(
			atmosphere,
			seconds,
			{ Color = look.air, Decay = look.decay, Haze = look.haze, Density = look.density }
		)
	end
	if grade then
		tween(
			grade,
			seconds,
			{ TintColor = look.tint, Saturation = look.saturation, Contrast = look.contrast }
		)
	end
	if look.water then
		-- keep reflectance low: at a shallow camera angle reflective water becomes a white sheet of sky
		tween(workspace.Terrain, seconds, {
			WaterColor = look.water,
			WaterTransparency = look.waterAlpha or 0.45,
			WaterReflectance = 0.03,
		})
	end
end

function Mood.Start(attribute: string, looks: { Look })
	local player = Players.LocalPlayer
	local current = 0
	local function refresh()
		local zone = math.clamp(tonumber(player:GetAttribute(attribute)) or 1, 1, #looks)
		if zone ~= current then
			Mood.Apply(looks[zone], current == 0 and 0 or 2.2)
			current = zone
		end
	end
	player:GetAttributeChangedSignal(attribute):Connect(refresh)
	refresh()
end

return Mood
