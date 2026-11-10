-- Edit-context scenario: builds worked examples of the Build kit in Workspace.BuildExamples so you can
-- capture them (rbxgame shots / studio shot) and read them as recipes. Delete the folder afterwards.
--   studio luau scenarios/build-examples.luau
-- Each example is 3-6 primary masses at deliberate ratios, parts seated into each other, a small
-- palette, and one collider for anything walkable. Compare with the same object built from raw boxes.
local RS = game:GetService("ReplicatedStorage")
local Build = require(RS:WaitForChild("Shared"):WaitForChild("Build"))

local old = workspace:FindFirstChild("BuildExamples")
if old then
	old:Destroy()
end
local root = Instance.new("Folder")
root.Name = "BuildExamples"
root.Parent = workspace

local C = {
	bark = Color3.fromRGB(122, 84, 58),
	leaf = Color3.fromRGB(104, 178, 86),
	leafDark = Color3.fromRGB(70, 140, 72),
	wood = Color3.fromRGB(196, 146, 98),
	cloth = Color3.fromRGB(232, 96, 92),
	clothLight = Color3.fromRGB(250, 236, 214),
	stone = Color3.fromRGB(176, 172, 164),
	iron = Color3.fromRGB(58, 62, 72),
	glow = Color3.fromRGB(255, 220, 140),
}
-- built on a plate in open sky so captures show the assets, not the game's world
local base = CFrame.new(0, 200, 0)
Build.part(root, base * CFrame.new(36, -0.5, 0), Vector3.new(96, 1, 28), {
	Name = "Ground",
	Color = Color3.fromRGB(150, 196, 110),
	Material = Enum.Material.Grass,
	CanCollide = true,
})
local function model(name: string, x: number): (Model, CFrame)
	local m = Instance.new("Model")
	m.Name = name
	m.Parent = root
	return m, base * CFrame.new(x, 0, 0)
end

-- tree: tapered trunk (wide foot, slim top) seated into a canopy of three overlapping blobs
do
	local m, at = model("Tree", 0)
	Build.taper(m, at, 2.4, 1.2, 9, 6, { Color = C.bark, Material = Enum.Material.Wood })
	Build.blob(m, at * CFrame.new(0, 11, 0), 4.2, 7, 11, { Color = C.leaf })
	Build.blob(m, at * CFrame.new(2.6, 9.5, 1), 2.8, 4, 12, { Color = C.leafDark })
	Build.blob(m, at * CFrame.new(-2.4, 9.8, -1), 2.6, 4, 13, { Color = C.leaf })
	Build.collider(m, at * CFrame.new(0, 4.5, 0), Vector3.new(2.2, 9, 2.2))
end

-- market stall: rounded counter, four posts that hold up a roof with real overhang, striped awning
do
	local m, at = model("Stall", 18)
	Build.roundedBlock(
		m,
		at * CFrame.new(0, 1.75, 1.5),
		Vector3.new(10, 3.5, 3),
		0.6,
		{ Color = C.wood, Material = Enum.Material.WoodPlanks }
	)
	Build.roundedBlock(
		m,
		at * CFrame.new(0, 3.65, 1.5),
		Vector3.new(10.6, 0.3, 3.6),
		0.7,
		{ Color = C.clothLight }
	)
	for _, x in { -4.6, 4.6 } do
		for _, z in { -2.6, 2.8 } do
			Build.cylinder(m, at * CFrame.new(x, 4, z), 8, 0.3, { Color = C.wood })
		end
	end
	Build.roof(m, at * CFrame.new(0, 8, 0.1), 10.6, 6, 2.2, 0.8, { Color = C.cloth })
	for i = 0, 4 do -- awning scallops along the front eave
		Build.pill(
			m,
			at * CFrame.new(-4.4 + i * 2.2, 7.7, 4.1),
			1.4,
			0.45,
			{ Color = if i % 2 == 0 then C.cloth else C.clothLight }
		)
	end
	Build.collider(m, at * CFrame.new(0, 1.75, 1.5), Vector3.new(10, 3.5, 3))
end

-- lamp post: tapered post on a rounded plinth, an arched arm, a lantern with a glowing core
do
	local m, at = model("Lamp", 32)
	Build.roundedBlock(
		m,
		at * CFrame.new(0, 0.4, 0),
		Vector3.new(2.2, 0.8, 2.2),
		0.5,
		{ Color = C.stone, Material = Enum.Material.Slate }
	)
	Build.taper(
		m,
		at * CFrame.new(0, 0.8, 0),
		0.7,
		0.4,
		10,
		5,
		{ Color = C.iron, Material = Enum.Material.Metal }
	)
	Build.arch(
		m,
		at * CFrame.new(1.2, 10.4, 0),
		2.4,
		1.2,
		0.3,
		0.3,
		6,
		{ Color = C.iron, Material = Enum.Material.Metal }
	)
	local lantern = Build.part(
		m,
		at * CFrame.new(2.4, 9.6, 0),
		Vector3.new(0.9, 1.2, 0.9),
		{ Color = C.glow, Material = Enum.Material.Neon }
	)
	local light = Instance.new("PointLight")
	light.Range, light.Brightness, light.Color = 16, 1.2, C.glow
	light.Parent = lantern
	Build.roundedBlock(m, at * CFrame.new(2.4, 10.3, 0), Vector3.new(1.4, 0.3, 1.4), 0.3, { Color = C.iron })
	Build.collider(m, at * CFrame.new(0, 5, 0), Vector3.new(1, 10, 1))
end

-- bench: rounded seat and back slab, pill legs seated under the seat (never floating)
do
	local m, at = model("Bench", 44)
	Build.roundedBlock(
		m,
		at * CFrame.new(0, 2, 0),
		Vector3.new(7, 0.5, 2.2),
		0.4,
		{ Color = C.wood, Material = Enum.Material.Wood }
	)
	Build.roundedBlock(
		m,
		at * CFrame.new(0, 3.4, -0.95) * CFrame.Angles(math.rad(-12), 0, 0),
		Vector3.new(7, 1.6, 0.35),
		0.15,
		{ Color = C.wood, Material = Enum.Material.Wood }
	)
	for _, x in { -2.8, 2.8 } do
		Build.pill(
			m,
			at * CFrame.new(x, 0.95, 0) * CFrame.Angles(0, 0, math.rad(90)),
			1.6,
			0.28,
			{ Color = C.iron }
		)
	end
	Build.collider(m, at * CFrame.new(0, 1.1, 0), Vector3.new(7, 2.2, 2.2))
end

-- gate: two tapered stone pillars carrying an arch, capped balls on top
do
	local m, at = model("Gate", 58)
	for _, x in { -4, 4 } do
		Build.taper(
			m,
			at * CFrame.new(x, 0, 0),
			2,
			1.6,
			7,
			4,
			{ Color = C.stone, Material = Enum.Material.Slate }
		)
		Build.blob(m, at * CFrame.new(x, 7.9, 0), 0.6, 0, 1, { Color = C.stone })
	end
	Build.arch(
		m,
		at * CFrame.new(0, 6.6, 0),
		8,
		2.6,
		1.1,
		1.6,
		10,
		{ Color = C.stone, Material = Enum.Material.Slate }
	)
	Build.collider(m, at * CFrame.new(-4, 3.5, 0), Vector3.new(2, 7, 2))
	Build.collider(m, at * CFrame.new(4, 3.5, 0), Vector3.new(2, 7, 2))
end

-- cloud and rock: the same blob helper, different seed, scale and material
do
	local m, at = model("Cloud", 72)
	Build.blob(m, at * CFrame.new(0, 12, 0), 3, 8, 21, { Color = Color3.new(1, 1, 1), CastShadow = false })
	Build.blob(m, at * CFrame.new(0, 1, 0), 1.8, 4, 5, { Color = C.stone, Material = Enum.Material.Rock })
end

local count = 0
for _, d in root:GetDescendants() do
	if d:IsA("BasePart") then
		count += 1
	end
end
return ("built %d models, %d parts in Workspace.BuildExamples"):format(#root:GetChildren(), count)
