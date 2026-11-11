--!strict
-- What the world does when you play: the fixed camera and its nudge on every hit, the lit target orb, the pop and
-- sparks on a hit, the evening look. Parts, tweens and particles only, all local to this client.
-- A new game replaces target/hit and the look, and keeps the camera pose function.
local Debris = game:GetService("Debris")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Config = require(ReplicatedStorage.Shared.Config)
local Mood = require(script.Parent.Mood)

local CAMERA_POS = Vector3.new(0, 11.5, 25)
local CAMERA_AIM = Vector3.new(0, 11.5, 0)
local EVENING: Mood.Look = {
	clock = 17.8,
	brightness = 2.2,
	exposure = 0.2,
	shift = Color3.fromRGB(150, 170, 255),
	air = Color3.fromRGB(90, 105, 160),
	decay = Color3.fromRGB(80, 90, 150),
	haze = 1.2,
	density = 0.3,
	tint = Color3.fromRGB(225, 235, 255),
	saturation = 0.15,
	contrast = 0.1,
}

local Effects = {}
local orbs: { Part } = {}
local lit: Part? = nil
local kick = Vector3.zero

local function tween(inst: Instance, seconds: number, goal: { [string]: any }, style: Enum.EasingStyle?)
	TweenService:Create(inst, TweenInfo.new(seconds, style or Enum.EasingStyle.Quad), goal):Play()
end

local function setOrb(orb: Part, on: boolean)
	local base = orb:GetAttribute("BaseSize") :: number
	local light = orb:FindFirstChildOfClass("PointLight")
	tween(orb, 0.2, {
		Size = Vector3.one * base * (if on then 1.25 else 1),
		Transparency = if on then 0 else 0.35,
		Color = Config.color(if on then "Orb" else "OrbIdle"),
	})
	if light then
		tween(light, 0.2, { Brightness = if on then 1.2 else 0 })
	end
end

local function spark(orb: Part, color: Color3, count: number)
	local emitter = Instance.new("ParticleEmitter")
	emitter.Texture = "rbxasset://textures/particles/sparkles_main.dds"
	emitter.Rate = 0
	emitter.Lifetime = NumberRange.new(0.4, 0.9)
	emitter.Speed = NumberRange.new(10, 22)
	emitter.SpreadAngle = Vector2.new(180, 180)
	emitter.Color = ColorSequence.new(color)
	emitter.LightEmission = 1
	emitter.Size =
		NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.9), NumberSequenceKeypoint.new(1, 0) })
	emitter.Parent = orb
	emitter:Emit(count)
	Debris:AddItem(emitter, 1.5)
end

function Effects.start()
	Mood.Apply(EVENING, 0)
	local arena = workspace:WaitForChild("Arena")
	local folder = arena:WaitForChild("Orbs")
	for i = 1, Config.TargetCount do
		table.insert(orbs, folder:WaitForChild("Orb" .. i) :: Part)
	end
	-- a fixed camera with a decaying nudge; set every frame because the default camera script resets CameraType
	RunService:BindToRenderStep("PopCamera", Enum.RenderPriority.Camera.Value + 1, function(dt)
		local camera = workspace.CurrentCamera
		if not camera then
			return
		end
		kick = kick:Lerp(Vector3.zero, 1 - math.exp(-9 * dt))
		camera.CameraType = Enum.CameraType.Scriptable
		camera.FieldOfView = 70
		camera.Focus = CFrame.new(CAMERA_AIM)
		camera.CFrame = CFrame.lookAt(CAMERA_POS, CAMERA_AIM) * CFrame.new(kick)
	end)
end

-- Light the orb the player must hit now (0 or nil dims them all).
function Effects.target(index: number?)
	if lit then
		setOrb(lit, false)
		lit = nil
	end
	local orb = if index then orbs[index] else nil
	if orb then
		setOrb(orb, true)
		lit = orb
	end
end

-- The orb pops and the camera nudges: forward and up for a hit (more for PERFECT), a sideways shake for a miss.
function Effects.hit(index: number, grade: string)
	local orb = orbs[index]
	if grade == "MISS" then
		kick = Vector3.new(0.6, -0.2, 0)
		return
	end
	kick = if grade == "PERFECT" then Vector3.new(0, 0.5, -1.4) else Vector3.new(0, 0.25, -0.7)
	if orb then
		local perfect = grade == "PERFECT"
		spark(orb, Config.color(if perfect then "Perfect" else "Good"), if perfect then 40 else 18)
		-- a ghost ball swells and fades where the orb was, so the pop never fights the orb's own retarget tween
		local ghost = Instance.new("Part")
		ghost.Shape = Enum.PartType.Ball
		ghost.Anchored, ghost.CanCollide, ghost.CanQuery, ghost.CanTouch = true, false, false, false
		ghost.Material = Enum.Material.Neon
		ghost.Color = Config.color(if perfect then "Perfect" else "Good")
		ghost.Size = orb.Size
		ghost.CFrame = orb.CFrame
		ghost.Transparency = 0.2
		ghost.Parent = workspace
		tween(ghost, 0.4, { Size = orb.Size * 2.6, Transparency = 1 })
		Debris:AddItem(ghost, 0.6)
	end
end

return Effects
