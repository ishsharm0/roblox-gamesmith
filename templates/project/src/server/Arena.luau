--!strict
-- Builds the placeholder arena once at startup from Build.luau helpers: a floor, a ring of orbs standing
-- upright facing the camera, a halo, a backdrop and the (off-camera) spawn. Clients find the orbs at
-- workspace.Arena.Orbs.Orb<n> and animate them locally. A new game replaces the build function and
-- keeps "build once, idempotent, parented under workspace.Arena".
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Build = require(ReplicatedStorage.Shared.Build)
local Config = require(ReplicatedStorage.Shared.Config)

local RING_CENTRE = Vector3.new(0, 11, 0)
local RING_RADIUS = 8
local ORB_SIZE = 3.4

local Arena = {}

function Arena.build()
	local old = workspace:FindFirstChild("Arena")
	if old then
		old:Destroy()
	end
	local root = Instance.new("Folder")
	root.Name = "Arena"
	local orbs = Instance.new("Folder")
	orbs.Name = "Orbs"
	orbs.Parent = root

	-- floor with a glowing rim
	Build.cylinder(root, CFrame.new(0, -0.5, 0), 1, 34, {
		Name = "Floor",
		Color = Config.color("Floor"),
		CanCollide = true,
		CanQuery = true,
	})
	Build.cylinder(root, CFrame.new(0, -0.8, 0), 1, 35, {
		Name = "FloorRim",
		Color = Config.color("FloorRim"),
		Material = Enum.Material.Neon,
	})

	-- backdrop: a wall, two pillars and the halo the orbs sit on
	Build.roundedBlock(root, CFrame.new(0, 24, -12), Vector3.new(170, 64, 2), 3, {
		Name = "Backdrop",
		Color = Config.color("Backdrop"),
	})
	for _, x in { -30, 30 } do
		Build.cylinder(
			root,
			CFrame.new(x, 15, -8),
			30,
			2.4,
			{ Name = "Pillar", Color = Config.color("Floor") }
		)
		Build.cylinder(root, CFrame.new(x, 30.4, -8), 0.8, 3, {
			Name = "PillarCap",
			Color = Config.color("FloorRim"),
			Material = Enum.Material.Neon,
		})
	end
	local halo = { Name = "Halo", Color = Config.color("OrbIdle"), Material = Enum.Material.Metal }
	local haloCentre = CFrame.new(RING_CENTRE + Vector3.new(0, 0, -1.5))
	Build.arch(root, haloCentre, RING_RADIUS * 2, RING_RADIUS, 0.7, 0.7, 24, halo)
	Build.arch(
		root,
		haloCentre * CFrame.Angles(0, 0, math.pi),
		RING_RADIUS * 2,
		RING_RADIUS,
		0.7,
		0.7,
		24,
		halo
	)

	-- the orbs, clockwise from the top
	for i = 1, Config.TargetCount do
		local angle = (i - 1) / Config.TargetCount * math.pi * 2
		local offset = Vector3.new(math.sin(angle), math.cos(angle), 0) * RING_RADIUS
		local orb = Build.part(orbs, CFrame.new(RING_CENTRE + offset), Vector3.one * ORB_SIZE, {
			Name = "Orb" .. i,
			Color = Config.color("OrbIdle"),
			Material = Enum.Material.Neon,
			Transparency = 0.35,
		})
		orb.Shape = Enum.PartType.Ball
		orb.Size = Vector3.one * ORB_SIZE
		orb:SetAttribute("BaseSize", ORB_SIZE)
		local light = Instance.new("PointLight")
		light.Range = 9
		light.Brightness = 0
		light.Color = Config.color("Orb")
		light.Parent = orb
	end

	-- spawn: behind the camera, so the avatar never stands in front of an orb
	local spawn = Instance.new("SpawnLocation")
	spawn.Anchored = true
	spawn.Neutral = true
	spawn.Duration = 0
	spawn.Transparency = 1
	spawn.CanCollide = true
	spawn.Size = Vector3.new(8, 1, 8)
	spawn.CFrame = CFrame.new(0, -0.5, 40)
	spawn.Parent = root

	root.Parent = workspace
end

return Arena
