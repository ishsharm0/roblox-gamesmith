--!strict
-- Procedural poses for the local character, with no animation assets to upload.
-- Each frame (RunService.Stepped, after the Animator) the joints' Transform is overwritten with a
-- blend of named poses. Works on Motor6D and on the AnimationConstraint joints newer avatars use.
--
--   local Poser = require(script.Parent.Poser)
--   local poser = Poser.new(player)
--   poser:set("crouch", 0.8)       -- weight 0..1, change it every frame or tween it
--   poser:set("flip", 0.5)         -- some poses take a progress instead of a weight (see POSES)
--
-- Add poses to POSES: each returns joint -> CFrame for a weight w. Check a new pose by holding it
-- (player:SetAttribute("PoseTest", "<name>")) and capturing the character from the side.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local GuiService = game:GetService("GuiService")

local Poser = {}
Poser.__index = Poser

local JOINTS = {
	"Root",
	"Waist",
	"Neck",
	"LeftShoulder",
	"RightShoulder",
	"LeftHip",
	"RightHip",
	"LeftKnee",
	"RightKnee",
	"LeftElbow",
	"RightElbow",
}

-- R15, joint space: +X rotation on a hip swings the thigh forward, -X on a knee bends it.
local POSES: { [string]: (number) -> { [string]: CFrame } } = {
	crouch = function(w)
		return {
			Root = CFrame.new(0, -0.9 * w, 0) * CFrame.Angles(-0.35 * w, 0, 0),
			Waist = CFrame.Angles(-0.3 * w, 0, 0),
			LeftShoulder = CFrame.Angles(-1.1 * w, 0, 0),
			RightShoulder = CFrame.Angles(-1.1 * w, 0, 0),
			LeftHip = CFrame.Angles(1.3 * w, 0, 0),
			RightHip = CFrame.Angles(1.3 * w, 0, 0),
			LeftKnee = CFrame.Angles(-1.9 * w, 0, 0),
			RightKnee = CFrame.Angles(-1.9 * w, 0, 0),
		}
	end,
	stretch = function(w) -- take-off: arms up, body long
		return {
			Root = CFrame.Angles(0.25 * w, 0, 0),
			LeftShoulder = CFrame.Angles(2.6 * w, 0, -0.3 * w),
			RightShoulder = CFrame.Angles(2.6 * w, 0, 0.3 * w),
		}
	end,
	tuck = function(w) -- mid-air: knees up, arms in
		return {
			Waist = CFrame.Angles(-0.3 * w, 0, 0),
			LeftShoulder = CFrame.Angles(1.2 * w, 0, 0),
			RightShoulder = CFrame.Angles(1.2 * w, 0, 0),
			LeftHip = CFrame.Angles(1.3 * w, 0, 0),
			RightHip = CFrame.Angles(1.3 * w, 0, 0),
			LeftKnee = CFrame.Angles(-1.9 * w, 0, 0),
			RightKnee = CFrame.Angles(-1.9 * w, 0, 0),
		}
	end,
	flip = function(progress) -- a front somersault around the hips, progress 0..1
		return { Root = CFrame.Angles(-math.pi * 2 * progress, 0, 0) }
	end,
	wave = function(w) -- a greeting for title screens and NPCs
		local t = os.clock() * 8
		return { RightShoulder = CFrame.Angles(0, 0, 2.6 * w) * CFrame.Angles(0.25 * math.sin(t) * w, 0, 0) }
	end,
}
Poser.POSES = POSES

function Poser.new(player: Player?)
	local self =
		setmetatable({ weights = {} :: { [string]: number }, joints = {} :: { [string]: any } }, Poser)
	local plr = player or Players.LocalPlayer
	local function grab(c: Model)
		self.joints = {}
		for _, name in JOINTS do
			local j = c:FindFirstChild(name, true)
			if j and (j:IsA("Motor6D") or j:IsA("AnimationConstraint")) then
				self.joints[name] = j
			end
		end
	end
	plr.CharacterAdded:Connect(grab)
	if plr.Character then
		grab(plr.Character)
	end
	self.conn = RunService.Stepped:Connect(function()
		if GuiService.ReducedMotionEnabled then
			return
		end
		local test = plr:GetAttribute("PoseTest")
		local weights = if type(test) == "string" and POSES[test] then { [test] = 1 } else self.weights
		local out: { [string]: CFrame } = {}
		for name, w in weights do
			if w > 0 and POSES[name] then
				for joint, cf in POSES[name](w) do
					out[joint] = (out[joint] or CFrame.identity) * cf
				end
			end
		end
		for joint, cf in out do
			local j = self.joints[joint]
			if j then
				j.Transform = cf
			end
		end
	end)
	return self
end

function Poser:set(name: string, weight: number)
	self.weights[name] = weight
end

function Poser:clear()
	table.clear(self.weights)
end

function Poser:destroy()
	self.conn:Disconnect()
end

return Poser
