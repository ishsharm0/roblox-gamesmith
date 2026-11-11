--!strict
-- The core verb. ONE function (setHeld) begins and ends a charge; mouse, touch, Space, gamepad A and the BotHook all
-- call it, and the release amount goes to the server as an "Act". A new game replaces what setHeld means and keeps
-- the BotHook contract: Invoke("busy"), Invoke("act", amount), Invoke("state").
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local Config = require(ReplicatedStorage.Shared.Config)
local Net = require(ReplicatedStorage.Shared.Net)
local Rules = require(ReplicatedStorage.Shared.Rules)

local player = Players.LocalPlayer

local Input = {}
-- set by Main: called the instant the player lets go, before the server answers (immediate feedback)
Input.onRelease = nil :: ((amount: number) -> ())?

local heldAt: number? = nil
local holder: InputObject? = nil -- the press that began the charge; only its release ends it
local cooldownUntil = 0
local botHolding = false

local function playing(): boolean
	return player:GetAttribute("Phase") == Net.Phase.Play
end

-- The meter 0..1 while the player is holding, or nil when not.
function Input.charge(): number?
	local since = heldAt
	if since == nil then
		return nil
	end
	return Rules.meter(os.clock() - since, Config)
end

-- Begin (held = true) or end (held = false) a charge. `forced` replaces the measured meter value on
-- release; only the test hook uses it, so a bot hits exactly the amount it means to.
local function setHeld(held: boolean, forced: number?)
	if held then
		if heldAt == nil and playing() and os.clock() >= cooldownUntil then
			heldAt = os.clock()
		end
		return
	end
	if heldAt == nil then
		return
	end
	local amount = forced or Rules.meter(os.clock() - heldAt, Config)
	heldAt = nil
	holder = nil
	cooldownUntil = os.clock() + Config.ActInterval
	if not playing() then
		return
	end
	Net.Action:FireServer(Net.Intent.Act, amount)
	if Input.onRelease then
		Input.onRelease(amount)
	end
end

local function isPress(input: InputObject): boolean
	return input.UserInputType == Enum.UserInputType.MouseButton1
		or input.UserInputType == Enum.UserInputType.Touch
		or input.KeyCode == Enum.KeyCode.Space
		or input.KeyCode == Enum.KeyCode.ButtonA
end

local function num(name: string): number
	return (player:GetAttribute(name) :: number?) or 0
end

function Input.start()
	UserInputService.InputBegan:Connect(function(input, processed)
		if processed then
			return -- a button or the chat took it
		end
		if isPress(input) and heldAt == nil then
			setHeld(true)
			if heldAt ~= nil then
				holder = input
			end
		end
	end)
	UserInputService.InputEnded:Connect(function(input)
		local began = holder
		if
			began
			and isPress(input)
			and (
				input == began
				or (
					input.UserInputType ~= Enum.UserInputType.Touch
					and input.UserInputType == began.UserInputType
					and input.KeyCode == began.KeyCode
				)
			)
		then
			setHeld(false)
		end
	end)

	-- a new phase drops any charge in progress, so a missed release can never leave the verb stuck
	player:GetAttributeChangedSignal("Phase"):Connect(function()
		heldAt, holder = nil, nil
	end)
	-- losing the window mid-hold would never deliver the release: drop the charge instead
	UserInputService.WindowFocusReleased:Connect(function()
		heldAt, holder = nil, nil
	end)

	-- the test hook: scenarios/human-bot.luau and the tours call this
	local hook = Instance.new("BindableFunction")
	hook.Name = "BotHook"
	hook.OnInvoke = function(call: any, amount: any): any
		if call == "busy" then
			return not playing() or heldAt ~= nil or botHolding or os.clock() < cooldownUntil
		elseif call == "act" then
			if botHolding or type(amount) ~= "number" or not playing() then
				return false
			end
			local value = math.clamp(amount, 0, 1)
			setHeld(true)
			if heldAt == nil then
				return false
			end
			botHolding = true
			task.wait(value * Config.ChargeSeconds) -- a real charge, as slow as a person's
			setHeld(false, value)
			botHolding = false
			return true
		elseif call == "state" then
			local zone = player:GetAttribute("Zone")
			local good, perfect = Rules.widths(num("Combo"), Config)
			return {
				phase = player:GetAttribute("Phase"),
				score = num("Score"),
				combo = num("Combo"),
				lives = num("Lives"),
				timeLeft = num("TimeLeft"),
				target = if zone
					then {
						index = num("Target"),
						ideal = zone, -- the release amount that scores PERFECT
						good = good,
						perfect = perfect,
					}
					else nil,
			}
		end
		return nil
	end
	hook.Parent = player
end

return Input
