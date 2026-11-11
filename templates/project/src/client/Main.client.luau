--!strict
-- Client entry: start the modules in order and wire them together. Input sends the verb, Hud shows the
-- state, and the server's one-shot "Grade" events fan out to sound, effects and the popup.
-- A new game keeps this wiring and swaps what each event does.
if not game:IsLoaded() then
	game.Loaded:Wait()
end
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Net = require(ReplicatedStorage.Shared.Net)
local Audio = require(script.Parent.Audio)
local Effects = require(script.Parent.Effects)
local Hud = require(script.Parent.Hud)
local Input = require(script.Parent.Input)
local Kit = require(script.Parent.UiKit)

local player = Players.LocalPlayer

Audio.start()
Kit.onClick = function()
	Audio.play("click")
end
Effects.start()
Hud.start({
	charge = Input.charge,
	onStar = function(index)
		Audio.play("star", 1 + (index - 1) * 0.25)
	end,
})

Input.onRelease = function(amount)
	Hud.released(amount)
	Audio.play("release", 0.8 + amount * 0.6)
end
Input.start()

-- light the orb the server picked
local function showTarget()
	if player:GetAttribute("Phase") == Net.Phase.Play then
		Effects.target(player:GetAttribute("Target") :: number?)
	else
		Effects.target(nil)
	end
end
player:GetAttributeChangedSignal("Target"):Connect(showTarget)
player:GetAttributeChangedSignal("Phase"):Connect(function()
	showTarget()
	if player:GetAttribute("Phase") == Net.Phase.Results then
		Audio.play("finish")
	end
end)
showTarget()

Net.Event.OnClientEvent:Connect(
	function(kind: unknown, grade: unknown, orb: unknown, points: unknown, combo: unknown)
		if
			kind ~= "Grade"
			or type(grade) ~= "string"
			or type(orb) ~= "number"
			or type(points) ~= "number"
		then
			return
		end
		Hud.grade(grade, points)
		Effects.hit(orb, grade)
		Audio.play(string.lower(grade), Audio.comboPitch(if type(combo) == "number" then combo else 0))
	end
)
print("[client] start")
