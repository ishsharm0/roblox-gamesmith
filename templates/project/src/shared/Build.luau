--!strict
-- Build: a construction kit for Part-built worlds. Raw sharp boxes are what make generated Roblox
-- builds look cheap. These helpers give rounded corners, pills, arches, tapers, roofs with overhang
-- and seeded organic clusters, so an asset is a few deliberate masses instead of a pile of cubes.
-- Every helper returns the Part(s) it made, parented to `parent`, anchored and smooth by default.
-- Collision: decorative helpers set CanCollide/CanQuery/CanTouch false unless props say otherwise;
-- give walkable surfaces one simple collider (Build.collider) instead of colliding every detail.
--
--   Build.part(parent, cframe, size, props?)                   one Part with house defaults
--   Build.roundedBlock(parent, cframe, size, r, props?)        slab with rounded vertical corners (radius r)
--   Build.pill(parent, cframe, length, radius, props?)         capsule along the CFrame's X axis
--   Build.cylinder(parent, cframe, height, radius, props?)     upright cylinder (Y axis), height first
--   Build.taper(parent, cframe, bottom, top, height, steps, props?)  stacked rounded slices narrowing upward
--   Build.arch(parent, cframe, span, rise, thickness, depth, segments, props?)  curved arch in the XY plane
--   Build.roof(parent, cframe, width, depth, rise, overhang, props?)  gable roof (two wedges) with eaves
--   Build.blob(parent, cframe, radius, count, seed, props?)    seeded cluster of balls (bushes, clouds, rocks)
--   Build.around(count, radius, fn)                            calls fn(i, CFrame) for a ring of positions
--   Build.collider(parent, cframe, size)                       invisible walkable/colliding block
--   Build.rng(seed)                                            deterministic Random for repeatable worlds

local Build = {}

local DECOR = { CanCollide = false, CanQuery = false, CanTouch = false }

local function apply(p: BasePart, props: { [string]: any }?)
	if props then
		for k, v in props do
			(p :: any)[k] = v
		end
	end
end

function Build.rng(seed: number): Random
	return Random.new(seed)
end

function Build.part(parent: Instance, cframe: CFrame, size: Vector3, props: { [string]: any }?): Part
	local p = Instance.new("Part")
	p.Anchored = true
	p.Material = Enum.Material.SmoothPlastic
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Size = size
	p.CFrame = cframe
	apply(p, DECOR)
	apply(p, props)
	p.Parent = parent
	return p
end

local function shaped(parent, cframe, size, shape: Enum.PartType, props): Part
	local p = Build.part(parent, cframe, size, props)
	p.Shape = shape
	p.Size = size -- setting Shape can change Size; set it back
	return p
end

function Build.cylinder(
	parent: Instance,
	cframe: CFrame,
	height: number,
	radius: number,
	props: { [string]: any }?
): Part
	-- a Cylinder part's axis is X: turn it to stand on Y
	return shaped(
		parent,
		cframe * CFrame.Angles(0, 0, math.rad(90)),
		Vector3.new(height, radius * 2, radius * 2),
		Enum.PartType.Cylinder,
		props
	)
end

function Build.roundedBlock(
	parent: Instance,
	cframe: CFrame,
	size: Vector3,
	r: number,
	props: { [string]: any }?
): { BasePart }
	r = math.clamp(r, 0, math.min(size.X, size.Z) / 2 - 0.01)
	local out = {}
	-- a cross of two blocks plus a cylinder in each corner reads as one slab with rounded corners
	table.insert(out, Build.part(parent, cframe, Vector3.new(size.X - r * 2, size.Y, size.Z), props))
	table.insert(out, Build.part(parent, cframe, Vector3.new(size.X, size.Y, size.Z - r * 2), props))
	for _, s in { { 1, 1 }, { 1, -1 }, { -1, 1 }, { -1, -1 } } do
		local at = cframe * CFrame.new(s[1] * (size.X / 2 - r), 0, s[2] * (size.Z / 2 - r))
		table.insert(out, Build.cylinder(parent, at, size.Y, r, props))
	end
	return out
end

function Build.pill(
	parent: Instance,
	cframe: CFrame,
	length: number,
	radius: number,
	props: { [string]: any }?
): { BasePart }
	local body =
		shaped(parent, cframe, Vector3.new(length, radius * 2, radius * 2), Enum.PartType.Cylinder, props)
	local a = shaped(
		parent,
		cframe * CFrame.new(length / 2, 0, 0),
		Vector3.one * radius * 2,
		Enum.PartType.Ball,
		props
	)
	local b = shaped(
		parent,
		cframe * CFrame.new(-length / 2, 0, 0),
		Vector3.one * radius * 2,
		Enum.PartType.Ball,
		props
	)
	return { body, a, b }
end

function Build.taper(
	parent: Instance,
	cframe: CFrame,
	bottom: number,
	top: number,
	height: number,
	steps: number,
	props: { [string]: any }?
): { BasePart }
	local out = {}
	local h = height / steps
	for i = 0, steps - 1 do
		local u = (i + 0.5) / steps
		local r = (bottom + (top - bottom) * u) / 2
		-- slices overlap a little so no seam shows between them
		table.insert(
			out,
			Build.cylinder(parent, cframe * CFrame.new(0, h * (i + 0.5), 0), h * 1.08, r, props)
		)
	end
	return out
end

function Build.arch(
	parent: Instance,
	cframe: CFrame,
	span: number,
	rise: number,
	thickness: number,
	depth: number,
	segments: number,
	props: { [string]: any }?
): { BasePart }
	-- an elliptical arch from (-span/2, 0) over (0, rise) to (span/2, 0); each segment a block whose
	-- length slightly overshoots the chord so the joints close
	local out = {}
	local function at(t: number): Vector3
		local a = math.pi * (1 - t)
		return Vector3.new(math.cos(a) * span / 2, math.sin(a) * rise, 0)
	end
	for i = 0, segments - 1 do
		local a, b = at(i / segments), at((i + 1) / segments)
		local mid = (a + b) / 2
		local len = (b - a).Magnitude + thickness * 0.35
		local cf = cframe * CFrame.lookAt(mid, mid + Vector3.zAxis, (b - a).Unit:Cross(Vector3.zAxis))
		table.insert(out, Build.part(parent, cf, Vector3.new(len, thickness, depth), props))
	end
	return out
end

function Build.roof(
	parent: Instance,
	cframe: CFrame,
	width: number,
	depth: number,
	rise: number,
	overhang: number,
	props: { [string]: any }?
): { BasePart }
	-- two wedges back to back along X, ridge along Z; overhang extends past the walls on every side
	local w, d = width / 2 + overhang, depth + overhang * 2
	local out = {}
	for _, side in { 1, -1 } do
		local wedge = Instance.new("WedgePart")
		wedge.Anchored = true
		wedge.Material = Enum.Material.SmoothPlastic
		wedge.TopSurface, wedge.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
		apply(wedge, DECOR)
		apply(wedge, props)
		-- a WedgePart is tall at its back (+Z); turn each half so its tall side meets the ridge
		wedge.Size = Vector3.new(d, rise, w)
		wedge.CFrame = cframe
			* CFrame.new(side * w / 2, rise / 2, 0)
			* CFrame.Angles(0, -side * math.rad(90), 0)
		wedge.Parent = parent
		table.insert(out, wedge)
	end
	return out
end

function Build.blob(
	parent: Instance,
	cframe: CFrame,
	radius: number,
	count: number,
	seed: number,
	props: { [string]: any }?
): { BasePart }
	-- one big core ball plus seeded satellites on its upper surface: reads as a single soft mass
	local r = Build.rng(seed)
	local out = { shaped(parent, cframe, Vector3.one * radius * 1.6, Enum.PartType.Ball, props) }
	for _ = 1, count do
		local dir = Vector3.new(r:NextNumber(-1, 1), r:NextNumber(-0.2, 1), r:NextNumber(-1, 1)).Unit
		local s = radius * r:NextNumber(0.7, 1.05)
		table.insert(
			out,
			shaped(
				parent,
				cframe * CFrame.new(dir * radius * 0.6),
				Vector3.one * s,
				Enum.PartType.Ball,
				props
			)
		)
	end
	return out
end

function Build.around(count: number, radius: number, fn: (number, CFrame) -> ())
	for i = 1, count do
		local a = (i - 1) / count * math.pi * 2
		fn(i, CFrame.Angles(0, a, 0) * CFrame.new(0, 0, -radius))
	end
end

function Build.collider(parent: Instance, cframe: CFrame, size: Vector3): Part
	return Build.part(parent, cframe, size, {
		Transparency = 1,
		CanCollide = true,
		CanQuery = true,
		CanTouch = true,
		CastShadow = false,
		Name = "Collider",
	})
end

return Build
