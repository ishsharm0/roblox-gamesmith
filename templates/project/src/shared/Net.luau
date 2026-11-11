--!strict
-- The network contract in one place: the `Action` RemoteEvent (intents Start, Act, Menu), state as player attributes
-- (Phase, Score, Combo, Lives, TimeLeft, Best, Stars, Target, Zone) and the `Event` RemoteEvent for one-shot feedback.
-- A new game keeps this shape, renames the intents and adds attributes here.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local function remote(name: string): RemoteEvent
	local existing = ReplicatedStorage:FindFirstChild(name)
	if existing then
		return existing :: RemoteEvent
	end
	if RunService:IsServer() then
		local created = Instance.new("RemoteEvent")
		created.Name = name
		created.Parent = ReplicatedStorage
		return created
	end
	return ReplicatedStorage:WaitForChild(name) :: RemoteEvent
end

local Net = {
	Action = remote("Action"),
	Event = remote("Event"),
	Intent = { Start = "Start", Act = "Act", Menu = "Menu" },
	Phase = { Title = "Title", Play = "Play", Results = "Results" },
}

return Net
