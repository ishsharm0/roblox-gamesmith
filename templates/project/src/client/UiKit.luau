--!strict
-- Token-driven UI, authored at 844x390 for touch; mouse and keyboard lay out on a 1280x640 canvas so a
-- laptop does not get the phone layout magnified (Canvas). 16px text and 48px targets never scale down.
local GuiService = game:GetService("GuiService")
local TweenService = game:GetService("TweenService")
local UIS = game:GetService("UserInputService")
local Shared = game:GetService("ReplicatedStorage"):WaitForChild("Shared")
local Themes = require(Shared.Themes)
local Canvas = require(Shared:WaitForChild("Canvas"))
local Shadows = require(script.Parent.UiShadow)
local Kit = {}
local active: any = Themes.Toybox
Kit.tokens = active
Kit.themeName = "Toybox"
Kit.Theme = {} :: { [string]: any }
local T = Kit.Theme
local bindings: { [Instance]: { () -> () } } = {}
local bindingOrder: { { owner: Instance?, updates: { () -> () } } } = {}
local function bind(owner: Instance, update: () -> ())
	if not bindings[owner] then
		bindings[owner] = {}
		local record: { owner: Instance?, updates: { () -> () } } =
			{ owner = owner, updates = bindings[owner] }
		table.insert(bindingOrder, record)
		owner.Destroying:Once(function()
			bindings[owner] = nil
			record.owner = nil
			record.updates = {}
		end)
	end
	table.insert(bindings[owner], update)
	update()
end
local function merge(base: any, overrides: any): any
	local result = {}
	for k, v in base do
		result[k] = if type(v) == "table" then merge(v, nil) else v
	end
	for k, v in overrides or {} do
		result[k] = if type(v) == "table" and type(base[k]) == "table" then merge(base[k], v) else v
	end
	return result
end
function Kit.setTheme(name: string, overrides: { [string]: any }?)
	local theme = (Themes :: any)[name]
	assert(theme, "Unknown UI theme: " .. name)
	active = merge(theme, overrides)
	Kit.tokens, Kit.themeName = active, name
	local c, s, ty, r = active.color, active.shape, active.type, active.rarity
	-- Keep the table identity and the shipped kit's public aliases for existing game code.
	local aliases = {
		Ink = c.text,
		InkSoft = c.textSoft,
		Cream = c.surface,
		CreamShade = c.surfaceAlt,
		Lime = c.primary,
		LimeShade = c.primaryShade,
		Aqua = c.secondary,
		AquaShade = c.secondaryShade,
		Coral = c.danger,
		CoralShade = c.dangerShade,
		Sun = c.accent,
		SunShade = c.accentShade,
		Muted = c.muted,
		Common = r.common,
		Uncommon = r.uncommon,
		Rare = r.rare,
		Epic = r.epic,
		Legendary = r.legendary,
		Display = ty.display,
		Body = ty.body,
		BodyHeavy = ty.body,
		Radius = s.radius,
		Stroke = s.stroke,
		Lip = s.lip,
		Ref = Vector2.new(844, 390),
	}
	for k, v in aliases do
		T[k] = v
	end
	local live = {}
	for _, record in bindingOrder do
		if record.owner then
			table.insert(live, record)
			for _, update in record.updates do
				update()
			end
		end
	end
	bindingOrder = live
end
Kit.setTheme("Toybox")
Kit.reducedMotion = false
Kit.onClick = nil :: (() -> ())?
local icons: { [string]: string } = {}
function Kit.configureIcons(map: { [string]: string })
	icons = table.clone(map)
end

-- Sizing rules for content-led controls (references/ui-image-assets.md): the label's cap height is half the
-- visible face, side padding is 0.4 x the button height, icons are 0.6 x the face. 48 px is the target floor.
Kit.metrics = { button = 52, small = 48, large = 60, cap = 0.5, padX = 0.4, icon = 0.6, gap = 0.16 }

-- Image art. Theme roles (panel, card, buttonPrimary[Pressed|Disabled], chip, barTrack, barFill, ribbon, pattern,
-- backdrop, close) come from the theme's `art` tokens; anything else (titles, mascots, icon-<kind>, backgrounds)
-- by name from Kit.configureArt(require(UiArt)). A component with no art for its role draws natively.
local named: { [string]: any } = {}
function Kit.configureArt(map: { [string]: any })
	named = table.clone(map)
end
local function roleArt(role: string): any
	local a = active.art
	local entry = a and a[role]
	return if entry and entry.image ~= "" then entry else nil
end
function Kit.artFor(name: string): any
	local entry = named[name] or roleArt(name)
	return if entry and entry.image ~= "" then entry else nil
end
function Kit.applyArt(img: ImageLabel | ImageButton, entry: any)
	img.Image = entry.image
	if entry.slice then
		img.ScaleType = Enum.ScaleType.Slice
		img.SliceCenter = entry.slice
		img.SliceScale = entry.sliceScale or 1
	elseif entry.tile then
		img.ScaleType = Enum.ScaleType.Tile
		img.TileSize = UDim2.fromOffset(entry.tile.X, entry.tile.Y)
	else
		img.ScaleType = Enum.ScaleType.Fit
	end
end
-- An ImageLabel of a named art piece at its design size (times props.scale), e.g. Kit.art(panel, "mascot-cheer").
function Kit.art(parent: Instance, name: string, props: { [string]: any }?): ImageLabel?
	local entry = Kit.artFor(name)
	if not entry then
		return nil
	end
	local p = props or {}
	local s = p.scale or 1
	local img = Kit.make("ImageLabel", {
		Name = p.Name or name,
		BackgroundTransparency = 1,
		Size = p.Size or UDim2.fromOffset(entry.size.X * s, entry.size.Y * s),
		Position = p.Position or UDim2.new(),
		AnchorPoint = p.AnchorPoint or Vector2.zero,
		Rotation = p.Rotation or 0,
		ZIndex = p.ZIndex or 1,
		Parent = parent,
	})
	Kit.applyArt(img, entry)
	if p.ScaleType then
		img.ScaleType = p.ScaleType
	end
	return img
end
local function capitalise(s: string): string
	return string.upper(string.sub(s, 1, 1)) .. string.sub(s, 2)
end
function Kit.make(class: string, props: { [string]: any }, children: { Instance }?): any
	local inst = Instance.new(class)
	for k, v in props do
		if k ~= "Parent" then
			(inst :: any)[k] = v
		end
	end
	for _, child in children or {} do
		child.Parent = inst
	end
	inst.Parent = props.Parent
	return inst
end
local make = Kit.make
function Kit.corner(radius: number?, corners: { [string]: number }?): UICorner
	local corner = make("UICorner", {})
	bind(corner, function()
		corner.CornerRadius = UDim.new(0, radius or active.shape.radius)
		for k, v in corners or {} do
			-- Optional per-corner overrides on current builds; uniform radius on old clients.
			pcall(function()
				(corner :: any)[k] = UDim.new(0, v)
			end)
		end
	end)
	return corner
end
function Kit.stroke(color: Color3?, thickness: number?): UIStroke
	local stroke = make(
		"UIStroke",
		{ ApplyStrokeMode = Enum.ApplyStrokeMode.Border, LineJoinMode = Enum.LineJoinMode.Round }
	)
	bind(stroke, function()
		stroke.Color = color or active.color.outline
		stroke.Thickness = thickness or active.shape.stroke
		stroke.Enabled = stroke.Thickness > 0
	end)
	return stroke
end
local function shadow(parent: GuiObject, name: string, options: () -> Shadows.Options)
	local apply = Shadows.create(parent, name)
	bind(parent, function()
		apply(options())
	end)
	return apply
end
local function glow(parent: GuiObject)
	shadow(parent, "Glow", function()
		return {
			color = active.color.outline,
			blur = active.shape.glow,
			alpha = 0.25,
			enabled = active.shape.glow > 0,
			order = 0,
		}
	end)
end
local function gradient(parent: GuiObject, top: Color3, bottom: Color3, enabled: boolean)
	local g = parent:FindFirstChild("ThemeGradient")
		or make("UIGradient", { Name = "ThemeGradient", Rotation = 90, Parent = parent })
	parent.BackgroundColor3 = if enabled then Color3.new(1, 1, 1) else bottom
	g.Color = ColorSequence.new(top, bottom)
	g.Enabled = enabled
end
local function ease(): Enum.EasingStyle
	return (Enum.EasingStyle :: any)[active.motion.ease]
end
function Kit.tween(
	obj: Instance,
	t: number,
	props: { [string]: any },
	style: Enum.EasingStyle?,
	dir: Enum.EasingDirection?
)
	if Kit.reducedMotion or GuiService.ReducedMotionEnabled then
		for k, v in props do
			(obj :: any)[k] = v
		end
	else
		TweenService
			:Create(
				obj,
				TweenInfo.new(t, style or Enum.EasingStyle.Quad, dir or Enum.EasingDirection.Out),
				props
			)
			:Play()
	end
end
-- Touch-first screens use the phone canvas; a phone with a keyboard attached switches with PreferredInput.
function Kit.isTouch(): boolean
	return UIS.PreferredInput == Enum.PreferredInput.Touch
end
function Kit.screen(
	parent: Instance,
	name: string,
	order: number,
	insets: Enum.ScreenInsets?
): (ScreenGui, Frame)
	local gui = make("ScreenGui", {
		Name = name,
		ResetOnSpawn = false,
		DisplayOrder = order,
		ScreenInsets = insets or Enum.ScreenInsets.CoreUISafeInsets,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
		Parent = parent,
	})
	local root = make(
		"Frame",
		{ Name = "Root", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), Parent = gui }
	)
	local scale = make("UIScale", { Parent = root })
	-- ForceViewport / ForceTouch (attributes on the ScreenGui) let a scenario lay the UI out for another screen.
	local function fit()
		local forced = gui:GetAttribute("ForceViewport")
		local v = if typeof(forced) == "Vector2" then forced else gui.AbsoluteSize
		if v.X < 1 then
			return
		end
		local touch = gui:GetAttribute("ForceTouch")
		if type(touch) ~= "boolean" then
			touch = Kit.isTouch()
		end
		local s, w, h = Canvas.fit(v.X, v.Y, touch :: boolean)
		scale.Scale = s
		root.Size = UDim2.fromOffset(w, h)
		gui:SetAttribute("UiScale", s)
	end
	local conns = {
		gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(fit),
		gui.AttributeChanged:Connect(function(attr)
			if attr == "ForceViewport" or attr == "ForceTouch" then
				fit()
			end
		end),
		UIS:GetPropertyChangedSignal("PreferredInput"):Connect(fit),
	}
	gui.Destroying:Once(function()
		for _, conn in conns do
			conn:Disconnect()
		end
	end)
	fit()
	task.defer(fit)
	return gui, root
end
function Kit.text(parent: Instance, props: { [string]: any }): TextLabel
	local p: { [string]: any } = {
		BackgroundTransparency = 1,
		TextSize = 18,
		TextWrapped = true,
		Size = UDim2.fromOffset(200, 28),
		Parent = parent,
	}
	for k, v in props do
		if
			k ~= "display"
			and k ~= "outline"
			and k ~= "role"
			and k ~= "button"
			and k ~= "themeColor"
			and k ~= "preserveCase"
		then
			p[k] = v
		end
	end
	p.TextSize = math.clamp(p.TextSize, 16, 100)
	local label = make("TextLabel", p)
	local sourceText = label.Text
	local styledText = label.Text
	local stroke = make("UIStroke", {
		ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual,
		LineJoinMode = Enum.LineJoinMode.Round,
		Parent = label,
	})
	bind(label, function()
		local fontScale = if props.FontFace
			then 1
			elseif props.button then active.type.buttonScale or 1
			elseif props.display then active.type.displayScale or 1
			else 1
		label.TextSize = math.clamp(p.TextSize * fontScale, 16, 100)
		label.FontFace = props.FontFace
			or (
				if props.button
					then active.type.button
					elseif props.display then active.type.display
					else active.type.body
			)
		label.TextColor3 = if props.themeColor
			then props.themeColor()
			else props.TextColor3 or active.color[props.role or "text"]
		stroke.Color = active.color.outline
		stroke.Thickness = props.outline
			or (if props.display or props.button then active.type.textStroke else 0)
		stroke.Enabled = stroke.Thickness > 0
		-- Only titles/buttons change case. Counter strings and body copy retain their content.
		if (props.display or props.button) and props.Text and not props.preserveCase then
			if label.Text ~= styledText then
				sourceText = label.Text
			end
			styledText = if active.type.titleUpper then string.upper(sourceText) else sourceText
			label.Text = styledText
		end
	end)
	shadow(label, "TextShadow", function()
		local n = props.outline or (if props.display or props.button then active.type.textStroke else 0)
		return { color = active.color.outline, text = true, y = n, enabled = n > 0 }
	end)
	return label
end
local function fallbackIcon(parent: Instance, kind: string, color: Color3, size: number): Frame
	local box = make("Frame", {
		Name = "Icon_" .. kind,
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(size, size),
		Parent = parent,
	})
	local function bar(x: number, y: number, w: number, h: number, rot: number?, r: number?)
		return make("Frame", {
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.fromScale(x, y),
			Size = UDim2.fromScale(w, h),
			Rotation = rot or 0,
			BackgroundColor3 = color,
			ZIndex = 4,
			Parent = box,
		}, { make("UICorner", { CornerRadius = UDim.new(r or 0.5, 0) }) })
	end
	if kind == "pause" then
		bar(0.34, 0.5, 0.2, 0.74, 0, 0.3)
		bar(0.66, 0.5, 0.2, 0.74, 0, 0.3)
	elseif kind == "circle" then
		bar(0.5, 0.5, 0.65, 0.65)
	elseif kind == "coin" then
		local coin = bar(0.5, 0.52, 0.9, 0.6)
		for i = 1, 3 do
			local cut = bar(0.2 + i * 0.15, 0.68, 0.06, 0.18)
			cut.BackgroundTransparency = 0.6
		end
		coin.Rotation = -8
	elseif kind == "bomb" then
		bar(0.48, 0.6, 0.7, 0.7)
		bar(0.7, 0.26, 0.18, 0.3, 35)
		bar(0.84, 0.14, 0.24, 0.1, -20)
	elseif kind == "bolt" then
		bar(0.46, 0.38, 0.35, 0.58, 35, 0.05)
		bar(0.56, 0.64, 0.3, 0.58, 35, 0.05)
	elseif kind == "barbell" then
		bar(0.5, 0.5, 1, 0.14)
		for _, x in { 0.18, 0.35, 0.65, 0.82 } do
			bar(x, 0.5, 0.12, if x == 0.35 or x == 0.65 then 0.78 else 0.5, 0, 0.1)
		end
	elseif kind == "fork" then
		bar(0.5, 0.65, 0.12, 0.5)
		bar(0.3, 0.45, 0.12, 0.4, -35)
		bar(0.7, 0.45, 0.12, 0.4, 35)
		for _, x in { 0.18, 0.82 } do
			bar(x, 0.24, 0.24, 0.24)
		end
		bar(0.5, 0.86, 0.24, 0.24)
	elseif kind == "book" then
		bar(0.27, 0.5, 0.4, 0.74, 0, 0.05)
		bar(0.73, 0.5, 0.4, 0.74, 0, 0.05)
		bar(0.5, 0.85, 0.1, 0.22, 0, 0.05)
	elseif kind == "shield" then
		bar(0.5, 0.4, 0.7, 0.55, 0, 0.12)
		bar(0.5, 0.65, 0.52, 0.52, 45, 0.12)
	elseif kind == "store" then
		bar(0.2, 0.7, 0.12, 0.46, 0, 0.05)
		bar(0.8, 0.7, 0.12, 0.46, 0, 0.05)
		bar(0.5, 0.88, 0.7, 0.12, 0, 0.05)
		for i = 1, 3 do
			bar(0.12 + i * 0.19, 0.24, 0.22, 0.28, 0, 0.15)
		end
	elseif kind == "refresh" then
		make("Frame", {
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.fromScale(0.5, 0.5),
			Size = UDim2.fromScale(0.65, 0.65),
			BackgroundTransparency = 1,
			ZIndex = 4,
			Parent = box,
		}, {
			make("UICorner", { CornerRadius = UDim.new(0.5, 0) }),
			make("UIStroke", { Color = color, Thickness = math.max(2, size * 0.09) }),
		})
		bar(0.78, 0.22, 0.32, 0.12, 45, 0.05)
		bar(0.81, 0.35, 0.12, 0.34, 0, 0.05)
		bar(0.22, 0.78, 0.32, 0.12, 45, 0.05)
	elseif kind == "sliders" then
		for i, kx in { 0.32, 0.68, 0.45 } do
			local y = 0.2 + (i - 1) * 0.3
			bar(0.5, y, 0.9, 0.12)
			local knob = bar(kx, y, 0.3, 0.3)
			make("UIStroke", { Color = Kit.Theme.Cream, Thickness = 2, Parent = knob })
		end
	elseif kind == "close" then
		bar(0.5, 0.5, 0.18, 0.9, 45)
		bar(0.5, 0.5, 0.18, 0.9, -45)
	elseif kind == "check" then
		bar(0.36, 0.62, 0.18, 0.46, -45)
		bar(0.6, 0.48, 0.18, 0.78, 38)
	elseif kind == "play" then
		-- Filled triangle from short scanlines; no missing/small Unicode glyph on decorative fonts.
		for i = 0, 11 do
			local y = (i + 0.5) / 12
			local width = (1 - math.abs(y - 0.5) * 2) * 0.75
			bar(0.18 + width / 2, 0.12 + y * 0.76, width, 0.08, 0, 0)
		end
	elseif kind == "drop" then
		local tip = bar(0.5, 0.42, 0.5, 0.5, 45, 0.12)
		tip.ZIndex = 4
		local bulb = bar(0.5, 0.6, 0.66, 0.66)
		bulb.ZIndex = 5
		local shine = bar(0.4, 0.55, 0.16, 0.22, -20)
		shine.BackgroundColor3 = Color3.new(1, 1, 1)
		shine.BackgroundTransparency = 0.25
		shine.ZIndex = 6
	elseif kind == "clock" then
		local ring = make("Frame", {
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.fromScale(0.5, 0.5),
			Size = UDim2.fromScale(0.82, 0.82),
			BackgroundTransparency = 1,
			ZIndex = 4,
			Parent = box,
		}, {
			make("UICorner", { CornerRadius = UDim.new(0.5, 0) }),
			make("UIStroke", { Color = color, Thickness = math.max(2, size * 0.11) }),
		})
		local h1 = bar(0.5, 0.36, 0.11, 0.3)
		local h2 = bar(0.62, 0.52, 0.11, 0.26, 90)
		h1.ZIndex, h2.ZIndex = 5, 5
		local _ = ring
	elseif kind == "star" then
		Kit.text(box, {
			Text = "★",
			TextSize = size * 1.15,
			Size = UDim2.fromScale(1, 1),
			TextColor3 = color,
			display = true,
			ZIndex = 4,
		})
	elseif kind == "heart" then
		bar(0.33, 0.38, 0.48, 0.48)
		bar(0.67, 0.38, 0.48, 0.48)
		bar(0.5, 0.58, 0.5, 0.5, 45, 0.12)
	elseif kind == "home" then
		local roof = bar(0.5, 0.42, 0.6, 0.6, 45, 0.12)
		roof.Size = UDim2.fromScale(0.58, 0.58)
		local body = bar(0.5, 0.68, 0.64, 0.44, 0, 0.12)
		local door = bar(0.5, 0.78, 0.18, 0.26, 0, 0.2)
		door.BackgroundColor3 = T.Cream
		door.ZIndex, body.ZIndex = 6, 5
	end
	return box
end

function Kit.icon(parent: Instance, kind: string, color: Color3, size: number): GuiObject
	local drawn = not icons[kind] and Kit.artFor("icon-" .. kind)
	if drawn then
		-- Full-colour drawn icon: never tinted, so callers that recolour icons skip it (Colored attribute).
		local img = Kit.art(
			parent,
			"icon-" .. kind,
			{ Name = "Icon_" .. kind, Size = UDim2.fromOffset(size, size) }
		) :: ImageLabel
		img:SetAttribute("Colored", true)
		return img
	end
	if not icons[kind] and not icons.info then
		return fallbackIcon(parent, kind, color, size)
	end
	return make("ImageLabel", {
		Name = "Icon_" .. kind,
		Image = icons[kind] or icons.info or "",
		ImageColor3 = color,
		ScaleType = Enum.ScaleType.Fit,
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(size, size),
		Parent = parent,
	})
end
function Kit.panel(parent: Instance, props: { [string]: any }): Frame
	local holder = make("Frame", {
		Name = props.Name or "Panel",
		ZIndex = props.ZIndex or 3,
		Size = props.Size or UDim2.fromOffset(620, 300),
		Position = props.Position or UDim2.fromScale(0.5, 0.5),
		AnchorPoint = props.AnchorPoint or Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Parent = parent,
	})
	local faceStroke = Kit.stroke()
	local face = make(
		"Frame",
		{ Name = "Face", Size = UDim2.fromScale(1, 1), BorderSizePixel = 0, ZIndex = 2, Parent = holder },
		{ Kit.corner(props.radius), faceStroke }
	)
	-- Image frame (9-slice) and a low-opacity surface pattern when the theme has them.
	local plate = make("ImageLabel", {
		Name = "Plate",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = -1,
		Visible = false,
		Parent = face,
	})
	local pattern = make("ImageLabel", {
		Name = "Pattern",
		BackgroundTransparency = 1,
		ImageTransparency = props.patternAlpha or 0.9,
		ZIndex = 0,
		Visible = false,
		Parent = face,
	})
	local function frameArt(): any
		return if props.color == nil and props.plain ~= true then roleArt(props.art or "panel") else nil
	end
	bind(face, function()
		local c = active.color
		local a = frameArt()
		gradient(
			face,
			c.surfaceTop or c.surface,
			props.color or c.surface,
			c.surfaceTop ~= nil and props.color == nil
		)
		face.BackgroundTransparency = if a then 1 else 0
		faceStroke.Enabled = a == nil and active.shape.stroke > 0
		plate.Visible = a ~= nil
		if a then
			Kit.applyArt(plate, a)
			local inset = a.content or { 12, 12, 12, 12 }
			face:SetAttribute("Inset", inset[1])
			local pa = roleArt("pattern")
			pattern.Visible = pa ~= nil and props.pattern ~= false
			if pa then
				Kit.applyArt(pattern, pa)
				pattern.Position = UDim2.fromOffset(inset[1] - 6, inset[2] - 6)
				pattern.Size = UDim2.new(1, -(inset[1] + inset[3]) + 12, 1, -(inset[2] + inset[4]) + 12)
			end
		else
			face:SetAttribute("Inset", active.shape.stroke)
			pattern.Visible = false
		end
	end)
	shadow(face, "Shadow", function()
		return {
			color = Color3.new(),
			y = active.shape.shadow,
			alpha = 1 - active.shape.shadowAlpha,
			enabled = active.shape.shadowAlpha > 0 and frameArt() == nil,
		}
	end)
	shadow(face, "Glow", function()
		return {
			color = active.color.outline,
			blur = active.shape.glow,
			alpha = 0.25,
			enabled = active.shape.glow > 0 and frameArt() == nil,
			order = 0,
		}
	end)
	local titleArt = props.titleArt and Kit.artFor(props.titleArt)
	if titleArt then
		-- Text-art title on a ribbon that breaks the top edge (the ribbon falls back to a tab when no art).
		local ribbonArt = Kit.artFor(props.ribbonArt or "ribbon")
		local side = if ribbonArt and ribbonArt.content then ribbonArt.content[1] else 16
		local w = titleArt.size.X + side * 2 + 8
		local h = if ribbonArt then ribbonArt.size.Y else titleArt.size.Y + 8
		local ribbon = make("ImageLabel", {
			Name = "Ribbon",
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = props.titlePosition or UDim2.new(0.5, 0, 0, 2),
			Size = UDim2.fromOffset(w, h),
			BackgroundTransparency = 1,
			ZIndex = 6,
			Parent = face,
		})
		if ribbonArt then
			Kit.applyArt(ribbon, ribbonArt)
		else
			ribbon.BackgroundTransparency = 0
			ribbon.BackgroundColor3 = props.headerColor or active.color.titleBand
			Kit.corner(10).Parent = ribbon
			Kit.stroke().Parent = ribbon
		end
		local bottom = if ribbonArt and ribbonArt.content then ribbonArt.content[4] else 0
		Kit.art(ribbon, props.titleArt, {
			Name = "Title",
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.new(0.5, 0, 0.5, -bottom / 2),
			ZIndex = 7,
		})
	end
	if props.onClose then
		Kit.closeButton(face, props.onClose)
	end
	if props.title and not titleArt then
		local ribbon = make("Frame", {
			Name = "Ribbon",
			AnchorPoint = Vector2.new(0.5, 0),
			Size = UDim2.fromOffset(props.titleWidth or 240, 46),
			ZIndex = 3,
			BorderSizePixel = 0,
			Parent = face,
		}, { Kit.corner(), Kit.stroke() })
		local title = Kit.text(ribbon, {
			Text = props.title,
			display = true,
			TextSize = props.titleSize or 26,
			Size = UDim2.fromScale(1, 1),
			ZIndex = 4,
			themeColor = function()
				return if active.shape.title == "plain"
					then active.color.text
					elseif active.shape.title == "tab" then active.color.onSecondary
					else active.color.onTitleBand
			end,
		})
		local titleDrop = Shadows.create(ribbon, "TitleShadow")
		bind(ribbon, function()
			local style, c = active.shape.title, active.color
			ribbon.Position = props.titlePosition
				or UDim2.new(0.5, 0, 0, if style == "plain" then 10 else -22)
			ribbon.BackgroundTransparency = if style == "plain" then 1 else 0
			ribbon.BackgroundColor3 = props.headerColor
				or (if style == "tab" then props.titleColor or c.secondary else c.titleBand)
			local corner = ribbon:FindFirstChildOfClass("UICorner") :: UICorner
			corner.CornerRadius = UDim.new(0, if style == "banner" then 8 else active.shape.buttonRadius)
			local stroke = ribbon:FindFirstChildOfClass("UIStroke") :: UIStroke
			stroke.Enabled = style ~= "plain" and active.shape.stroke > 0
			titleDrop({
				color = Color3.new(),
				y = 4,
				alpha = 1 - active.shape.shadowAlpha,
				enabled = style ~= "plain",
			})
			title.TextStrokeTransparency = 1
		end)
	end
	return face
end
local function buttonColors(style: string, enabled: boolean): (Color3, Color3, Color3)
	local c = active.color
	if not enabled then
		return c.muted, c.mutedShade, c.textSoft
	end
	if style == "neutral" then
		return c.surface, c.surfaceAlt, c.text
	end
	if style == "reward" then
		style = "accent"
	end
	if c[style .. "Shade"] == nil then
		style = "primary"
	end
	return c[style],
		c[style .. "Shade"],
		c["on" .. string.upper(string.sub(style, 1, 1)) .. string.sub(style, 2)]
end
function Kit.setButton(btn: TextButton, enabled: boolean, text: string?)
	btn.Interactable, btn.Selectable = enabled, enabled
	btn:SetAttribute("Disabled", not enabled)
	if text then
		local label = btn:FindFirstChild("Label", true) :: TextLabel?
		if label then
			label.Text = text
			for _, update in bindings[label] or {} do
				update()
			end
		end
	end
end
-- Plate art for a button style and state: rest, Pressed, Disabled (falls back to buttonDisabled, then rest).
local function buttonArt(style: string, enabled: boolean, down: boolean): (any, any)
	if style == "reward" then
		style = "accent"
	end
	local key = "button" .. capitalise(style)
	local rest = roleArt(key)
	if not rest then
		return nil, nil
	end
	if not enabled then
		return roleArt(key .. "Disabled") or roleArt("buttonDisabled") or rest, rest
	end
	return if down then roleArt(key .. "Pressed") or rest else rest, rest
end
-- Text size whose cap height is Kit.metrics.cap of the face (plate height minus lip).
function Kit.labelSize(height: number, lip: number?): number
	local face = height - (lip or 0)
	local capRatio = active.type.capHeight or 0.72
	return math.clamp(math.floor(face * Kit.metrics.cap / capRatio + 0.5), 16, 100)
end
-- Buttons hug their content: give `height` (default Kit.metrics.button) and no Size, and the width becomes
-- label + icon + 0.4 x height of padding on each side. `fill = true` makes a full-width primary. An explicit
-- Size keeps the old fixed box.
function Kit.button(parent: Instance, props: { [string]: any }): TextButton
	local h = props.height or (if props.Size then props.Size.Y.Offset else Kit.metrics.button)
	local compact = props.Size == nil
	local btn = make("TextButton", {
		Name = props.Name or "Button",
		ZIndex = props.ZIndex or 1,
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Size = props.Size or (if props.fill then UDim2.new(1, 0, 0, h) else UDim2.fromOffset(h * 2, h)),
		Position = props.Position or UDim2.new(),
		AnchorPoint = props.AnchorPoint or Vector2.zero,
		Selectable = true,
		Parent = parent,
	})
	make("UISizeConstraint", { MinSize = Vector2.new(48, 48), Parent = btn })
	local scale = make("UIScale", { Parent = btn })
	local face = make(
		"Frame",
		{ Name = "Face", Size = UDim2.fromScale(1, 1), BorderSizePixel = 0, ZIndex = 2, Parent = btn },
		{ Kit.corner(), Kit.stroke() }
	)
	local corner = face:FindFirstChildOfClass("UICorner") :: UICorner
	local faceStroke = face:FindFirstChildOfClass("UIStroke") :: UIStroke
	local plate = make("ImageLabel", {
		Name = "Plate",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = 1,
		Visible = false,
		Parent = face,
	})
	local down = false
	local function colors()
		return buttonColors(props.style or "primary", not btn:GetAttribute("Disabled"))
	end
	-- Native plates draw their lip below the box; image plates carry it inside, so their face is shorter.
	local artNow = buttonArt(props.style or "primary", true, false)
	local lipNow = if artNow and artNow.content then artNow.content[4] - artNow.content[2] else 0
	local row = make(
		"Frame",
		{ Name = "Row", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, ZIndex = 3, Parent = face },
		{
			make("UIListLayout", {
				FillDirection = Enum.FillDirection.Horizontal,
				HorizontalAlignment = Enum.HorizontalAlignment.Center,
				VerticalAlignment = Enum.VerticalAlignment.Center,
				Padding = UDim.new(0, math.max(4, math.floor(h * Kit.metrics.gap))),
				SortOrder = Enum.SortOrder.LayoutOrder,
			}),
		}
	)
	local icon: GuiObject? = nil
	local iconSize = props.iconSize or (if compact then math.floor((h - lipNow) * Kit.metrics.icon) else 28)
	if props.icon then
		local _, _, on = colors()
		icon = Kit.icon(row, props.icon, on, iconSize)
		icon.ZIndex, icon.LayoutOrder = 4, 1
	end
	local label: TextLabel? = nil
	if props.text then
		label = Kit.text(row, {
			Name = "Label",
			Text = props.text,
			TextSize = props.TextSize or (if compact or props.autoText then Kit.labelSize(h, lipNow) else 28),
			button = true,
			TextWrapped = false,
			AutomaticSize = Enum.AutomaticSize.X,
			Size = UDim2.fromScale(0, 1),
			LayoutOrder = 2,
			ZIndex = 4,
			outline = props.outline,
			themeColor = function()
				local _, _, on = colors()
				return on
			end,
		})
	end
	local function hug()
		if not compact or props.fill then
			return
		end
		local content = 0
		local showIcon = icon ~= nil and icon.Visible
		if showIcon then
			content += iconSize
		end
		if label then
			content += label.TextBounds.X + (if showIcon
				then math.max(4, math.floor(h * Kit.metrics.gap))
				else 0)
		end
		btn.Size = UDim2.fromOffset(math.max(h, math.ceil(content + 2 * h * Kit.metrics.padX)), h)
	end
	if label then
		label:GetPropertyChangedSignal("TextBounds"):Connect(hug)
	end
	if icon then
		icon:GetPropertyChangedSignal("Visible"):Connect(hug)
	end
	hug()
	local applyDrop = Shadows.create(face, "Shadow")
	local applyLipOutline = Shadows.create(face, "LipOutline")
	local applyLip = Shadows.create(face, "Lip")
	local applyInset = Shadows.create(face, "Pressed")
	glow(face)
	local function update()
		local fill, shade, on = colors()
		local s = active.shape
		local lip = props.lip or s.lip
		local enabled = not btn:GetAttribute("Disabled")
		local art, restArt = buttonArt(props.style or "primary", enabled, down)
		btn:SetAttribute("Fill", fill)
		btn:SetAttribute("Art", art ~= nil)
		corner.CornerRadius = UDim.new(0, s.buttonRadius)
		-- Absolute colour gradient, matching CSS white-mixed top -> untouched token fill.
		local top = fill:Lerp(Color3.new(1, 1, 1), s.gradient)
		local g = face:FindFirstChild("ThemeGradient")
			or make("UIGradient", { Name = "ThemeGradient", Rotation = 90, Parent = face })
		face.BackgroundColor3 = if down then fill:Lerp(Color3.new(), 0.12) else fill
		face.BackgroundTransparency = if art then 1 else 0
		faceStroke.Enabled = art == nil and s.stroke > 0
		g.Color = ColorSequence.new(Color3.new(1, 1, 1), Color3.new(1, 1, 1))
		-- UIGradient multiplies its parent's colour, so use the absolute colours on a white Gloss overlay.
		local gloss = face:FindFirstChild("Gloss")
			or make("Frame", {
				Name = "Gloss",
				Size = UDim2.fromScale(1, 1),
				BorderSizePixel = 0,
				ZIndex = 2,
				Parent = face,
			}, { make("UICorner", {}) })
		gloss.BackgroundColor3 = Color3.new(1, 1, 1)
		local gc = gloss:FindFirstChildOfClass("UICorner") :: UICorner
		gc.CornerRadius = corner.CornerRadius
		local gg = gloss:FindFirstChildOfClass("UIGradient")
			or make("UIGradient", { Rotation = 90, Parent = gloss })
		gg.Color = ColorSequence.new(top, fill)
		gloss.Visible = art == nil and s.gradient > 0 and not down and enabled
		plate.Visible = art ~= nil
		if art then
			-- The plate image carries its own lip, stroke and pressed pose; the label rides the face inside it.
			Kit.applyArt(plate, art)
			local c = art.content or { 0, 0, 0, lip }
			local rc = restArt.content or c
			row.Position = UDim2.fromOffset(c[1], c[2])
			row.Size = UDim2.new(1, -(c[1] + c[3]), 1, -(rc[2] + rc[4]))
		else
			row.Position = UDim2.new()
			row.Size = UDim2.fromScale(1, 1)
		end
		applyDrop({
			color = Color3.new(),
			y = lip + s.shadow,
			alpha = 1 - s.shadowAlpha,
			enabled = art == nil and s.shadowAlpha > 0,
			order = 0,
		})
		applyLipOutline({
			color = active.color.outline,
			y = lip + s.stroke,
			enabled = art == nil and lip > 0 and s.stroke > 0 and not down,
			order = 1,
		})
		applyLip({ color = shade, y = lip, enabled = art == nil and lip > 0 and not down, order = 2 })
		applyInset({
			color = Color3.new(),
			y = 4,
			blur = 6,
			alpha = 0.55,
			inset = true,
			enabled = art == nil and down,
			order = 3,
		})
		if label then
			label.TextColor3 = on
		end
		if icon and not icon:GetAttribute("Colored") then
			for _, child in icon:GetDescendants() do
				if child:IsA("Frame") then
					child.BackgroundColor3 = on
				elseif child:IsA("UIStroke") then
					child.Color = on
				elseif child:IsA("TextLabel") then
					child.TextColor3 = on
				end
			end
			if icon:IsA("ImageLabel") then
				icon.ImageColor3 = on
			end
		end
	end
	bind(btn, update)
	btn:GetAttributeChangedSignal("Disabled"):Connect(function()
		down = false
		face.Position = UDim2.new()
		scale.Scale = 1
		update()
	end)
	local function press(value: boolean)
		if btn:GetAttribute("Disabled") then
			return
		end
		down = value
		update()
		if not btn:GetAttribute("Art") then
			Kit.tween(face, if value then 0.06 else 0.15, {
				Position = UDim2.fromOffset(
					0,
					if value then math.max(0, (props.lip or active.shape.lip) - 1) else 0
				),
			})
		end
		Kit.tween(
			scale,
			if value then 0.06 else 0.15,
			{ Scale = if value then active.motion.press else 1 },
			ease()
		)
	end
	btn.MouseButton1Down:Connect(function()
		press(true)
	end)
	btn.MouseButton1Up:Connect(function()
		press(false)
	end)
	btn.MouseLeave:Connect(function()
		press(false)
	end)
	local function hover()
		if btn.Interactable then
			Kit.tween(scale, 0.12, { Scale = 1.04 }, ease())
		end
	end
	btn.MouseEnter:Connect(hover)
	btn.SelectionGained:Connect(hover)
	btn.SelectionLost:Connect(function()
		press(false)
	end)
	local sel = make(
		"Frame",
		{ BackgroundTransparency = 1, Size = UDim2.new(1, 10, 1, 16), Position = UDim2.fromOffset(-5, -5) },
		{ Kit.corner(), Kit.stroke(nil, 4) }
	)
	bind(sel, function()
		(sel:FindFirstChildOfClass("UIStroke") :: UIStroke).Color = active.color.accent
	end)
	btn.SelectionImageObject = sel
	btn.Destroying:Once(function()
		sel:Destroy()
	end)
	btn.Activated:Connect(function()
		press(false)
		if Kit.onClick then
			Kit.onClick()
		end
		if props.onActivated then
			props.onActivated()
		end
	end)
	if props.enabled == false then
		Kit.setButton(btn, false)
	end
	return btn
end
function Kit.iconButton(parent: Instance, props: { [string]: any }): TextButton
	local p = table.clone(props)
	p.Size = UDim2.fromOffset(math.max(48, props.size or 52), math.max(48, props.size or 52))
	p.style = props.style or "neutral"
	return Kit.button(parent, p)
end
function Kit.pill(parent: Instance, props: { [string]: any }): (Frame, TextLabel)
	local h = props.height or 44
	local frame = make("Frame", {
		Name = props.Name or "Pill",
		Size = UDim2.fromOffset(props.width or 148, h),
		Position = props.Position or UDim2.new(),
		AnchorPoint = props.AnchorPoint or Vector2.zero,
		BorderSizePixel = 0,
		ZIndex = 2,
		Parent = parent,
	}, { Kit.corner(props.radius or h / 2), Kit.stroke() })
	-- `bare = true`: no plate at all, just the icon and an outlined number (the HUD rule in top games).
	local chipPlate = make("ImageLabel", {
		Name = "Plate",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = 0,
		Visible = false,
		Parent = frame,
	})
	local pillStroke = frame:FindFirstChildOfClass("UIStroke") :: UIStroke
	local function native(): boolean
		return not props.bare and roleArt("chip") == nil
	end
	bind(frame, function()
		frame.BackgroundColor3 = props.color or active.color.surface
		local a = if props.bare then nil else roleArt("chip")
		frame.BackgroundTransparency = if native() then 0 else 1
		pillStroke.Enabled = native() and active.shape.stroke > 0
		chipPlate.Visible = a ~= nil
		if a then
			Kit.applyArt(chipPlate, a)
		end
	end)
	shadow(frame, "Shadow", function()
		return {
			color = Color3.new(),
			y = 4,
			alpha = 1 - active.shape.shadowAlpha,
			enabled = native() and active.shape.shadowAlpha > 0,
		}
	end)
	glow(frame)
	if props.icon and props.bare then
		local ic =
			Kit.icon(frame, props.icon, props.iconColor or active.color.accent, props.iconSize or h + 4)
		ic.Name = "Badge"
		ic.AnchorPoint = Vector2.new(0, 0.5)
		ic.Position = UDim2.new(0, -4, 0.5, 0)
		ic.ZIndex = 3
	elseif props.icon then
		local badge = make("Frame", {
			Name = "Badge",
			Size = UDim2.fromOffset(40, 40),
			Position = UDim2.new(0, -3, 0.5, 0),
			AnchorPoint = Vector2.new(0, 0.5),
			BorderSizePixel = 0,
			Parent = frame,
		}, { Kit.corner(20), Kit.stroke() })
		local ic = Kit.icon(badge, props.icon, props.iconColor or active.color.onAccent, 26)
		ic.Position = UDim2.fromOffset(7, 7)
		bind(badge, function()
			badge.BackgroundColor3 = props.iconBg or active.color.accent
			local color = props.iconColor or active.color.onAccent
			if ic:GetAttribute("Colored") then
				return
			end
			if ic:IsA("ImageLabel") then
				ic.ImageColor3 = color
			end
			for _, child in ic:GetDescendants() do
				if child:IsA("Frame") then
					child.BackgroundColor3 = color
				elseif child:IsA("UIStroke") then
					child.Color = color
				end
			end
		end)
	end
	local iconRoom = if props.bare and props.icon
		then (props.iconSize or h + 4) + 2
		elseif props.icon then 37
		else 8
	local label = Kit.text(frame, {
		Name = "Value",
		preserveCase = true,
		Text = props.text or "",
		TextSize = props.TextSize or 26,
		display = true,
		Position = UDim2.fromOffset(iconRoom, 0),
		Size = UDim2.new(1, -iconRoom - 8, 1, 0),
		TextXAlignment = if props.bare then Enum.TextXAlignment.Left else Enum.TextXAlignment.Center,
		TextWrapped = false,
		outline = if props.bare then math.max(2, math.floor((props.TextSize or 26) * 0.11 + 0.5)) else nil,
		TextColor3 = if props.bare then Color3.new(1, 1, 1) else nil,
	})
	return frame, label
end
function Kit.rarityCard(parent: Instance, props: { [string]: any }): Frame
	local function rarity(): Color3
		return props.color or active.rarity[string.lower(props.rarity or "common")] or active.rarity.common
	end
	local card = make("Frame", {
		Name = props.Name or "Card",
		Size = props.Size or UDim2.fromOffset(162, 206),
		Position = props.Position or UDim2.new(),
		BorderSizePixel = 0,
		Parent = parent,
	}, { Kit.corner(), Kit.stroke() })
	local band = make("Frame", {
		Name = "Band",
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0),
		Size = UDim2.fromOffset(120, 24),
		ZIndex = 3,
		BorderSizePixel = 0,
		Parent = card,
	}, { Kit.corner(9), Kit.stroke(nil, 2) })
	local rarityLabel = Kit.text(band, {
		Name = "Rarity",
		TextWrapped = false,
		Text = string.upper(props.rarity or "common"),
		Size = UDim2.fromScale(1, 1),
		TextSize = 16,
		TextColor3 = Color3.new(1, 1, 1),
		ZIndex = 4,
	})
	local function fitTag()
		band.Size = UDim2.fromOffset(math.max(56, rarityLabel.TextBounds.X + 20), 24)
	end
	rarityLabel:GetPropertyChangedSignal("TextBounds"):Connect(fitTag)
	fitTag()

	local art = make("Frame", {
		Name = "Art",
		Position = UDim2.fromOffset(12, 12),
		Size = UDim2.new(1, -24, 0, 74),
		BorderSizePixel = 0,
		Parent = card,
	}, { Kit.corner(12) })
	local ic: GuiObject? = nil
	if props.icon then
		ic = Kit.icon(art, props.icon, props.iconColor or rarity(), 44)
		ic.Position = UDim2.new(0.5, -22, 0.5, -22)
	end
	Kit.text(card, {
		Name = "Name",
		preserveCase = true,
		Text = props.text or "",
		display = true,
		TextSize = 18,
		Position = UDim2.fromOffset(0, 92),
		Size = UDim2.new(1, 0, 0, 24),
	})
	Kit.text(card, {
		Name = "Subtitle",
		Text = props.subtitle or "",
		role = "textSoft",
		TextSize = 16,
		Position = UDim2.fromOffset(0, 116),
		Size = UDim2.new(1, 0, 0, 24),
	})
	local buy: TextButton? = nil
	if props.price then
		buy = Kit.button(card, {
			Name = "Buy",
			text = props.price,
			icon = "coin",
			iconSize = 18,
			TextSize = 18,
			style = props.style or "primary",
			Size = UDim2.new(1, -24, 0, 48),
			enabled = props.enabled,
			onActivated = props.onActivated,
		})
	end
	bind(card, function()
		card.BackgroundColor3 = active.color.surfaceAlt
		local cardCorner = card:FindFirstChildOfClass("UICorner") :: UICorner
		cardCorner.CornerRadius = UDim.new(0, math.max(0, active.shape.radius - 4))
		local cardStroke = card:FindFirstChildOfClass("UIStroke") :: UIStroke
		cardStroke.Color = rarity()
		band.BackgroundColor3 = rarity()
		art.BackgroundColor3 = active.color.surface:Lerp(rarity(), 0.28)
		if buy then
			buy.Position = UDim2.new(0, 12, 1, -60 - active.shape.lip)
		end
		if ic then
			local color = props.iconColor or rarity()
			if ic:IsA("ImageLabel") then
				ic.ImageColor3 = color
			end
			for _, child in ic:GetDescendants() do
				if child:IsA("Frame") then
					child.BackgroundColor3 = color
				elseif child:IsA("UIStroke") then
					child.Color = color
				elseif child:IsA("TextLabel") then
					child.TextColor3 = color
				end
			end
		end
	end)
	return card
end
-- Existing games keep Kit.card; it now has the same rarity styling as the shop card.
function Kit.card(parent: Instance, props: { [string]: any }): Frame
	local p = table.clone(props)
	p.Size = props.Size or UDim2.fromOffset(136, 180)
	return Kit.rarityCard(parent, p)
end
function Kit.switch(parent: Instance, props: { [string]: any }): (TextButton, (boolean) -> ())
	local value = props.value == true
	local row = make("TextButton", {
		Name = props.Name or "Switch",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Size = props.Size or UDim2.new(1, 0, 0, 56),
		Position = props.Position or UDim2.new(),
		Selectable = true,
		Parent = parent,
	})
	make("UISizeConstraint", { MinSize = Vector2.new(48, 48), Parent = row })
	local w, h = if props.compact then 64 else 88, if props.compact then 34 else 44
	local knobSize = h - 10
	Kit.text(row, {
		Text = props.text or "",
		Size = UDim2.new(1, -w - 8, 1, 0),
		TextXAlignment = Enum.TextXAlignment.Left,
		TextSize = props.TextSize or 20,
	})
	local track = make("Frame", {
		Name = "Track",
		Position = UDim2.new(1, -w, 0.5, -h / 2),
		Size = UDim2.fromOffset(w, h),
		BorderSizePixel = 0,
		Parent = row,
	}, { Kit.corner(props.radius or h / 2), Kit.stroke() })
	local knob = make(
		"Frame",
		{ Name = "Knob", Size = UDim2.fromOffset(knobSize, knobSize), BorderSizePixel = 0, Parent = track },
		{ Kit.corner(knobSize / 2), Kit.stroke() }
	)
	bind(track, function()
		track.BackgroundColor3 = if value then active.color.primary else active.color.muted
		knob.BackgroundColor3 = Color3.new(1, 1, 1)
	end)
	local function set(v: boolean)
		value = v
		Kit.tween(knob, 0.18, { Position = UDim2.fromOffset(if v then w - knobSize - 5 else 5, 5) })
		Kit.tween(track, 0.12, { BackgroundColor3 = if v then active.color.primary else active.color.muted })
		row:SetAttribute("On", v)
	end
	set(value)
	row.Activated:Connect(function()
		set(not value)
		if Kit.onClick then
			Kit.onClick()
		end
		if props.onChanged then
			props.onChanged(value)
		end
	end)
	return row, set
end
function Kit.scrim(parent: Instance, props: { [string]: any }?): Frame
	local p = props or {}
	local frame = make("Frame", {
		Name = p.Name or "Scrim",
		ZIndex = p.ZIndex or 2,
		Size = UDim2.fromScale(1, 1),
		BorderSizePixel = 0,
		Parent = parent,
	})
	bind(frame, function()
		frame.BackgroundColor3 = p.color or active.color.scrim
		frame.BackgroundTransparency = 1 - (p.alpha or active.color.scrimAlpha)
	end)
	return frame
end
function Kit.toast(parent: Instance, props: { [string]: any }): Frame
	local frame = make("Frame", {
		Name = props.Name or "Toast",
		Position = props.Position or UDim2.new(0.5, 0, 0, 70),
		AnchorPoint = props.AnchorPoint or Vector2.new(0.5, 0),
		Size = props.Size or UDim2.fromOffset(280, 48),
		BorderSizePixel = 0,
		ZIndex = 2,
		Parent = parent,
	}, { Kit.corner(14), Kit.stroke() })
	-- With chip art the toast is a light sticker plate with ink text instead of a dark box.
	local plate = make("ImageLabel", {
		Name = "Plate",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = 1,
		Visible = false,
		Parent = frame,
	})
	bind(frame, function()
		local a = roleArt("chip")
		frame.BackgroundColor3 = active.color.toast
		frame.BackgroundTransparency = if a then 1 else 0
		(frame:FindFirstChildOfClass("UIStroke") :: UIStroke).Enabled = a == nil
		plate.Visible = a ~= nil
		if a then
			Kit.applyArt(plate, a)
		end
	end)
	Kit.text(frame, {
		Text = props.text or "",
		display = true,
		ZIndex = 2,
		themeColor = function()
			return if roleArt("chip") then active.color.text else active.color.onToast
		end,
		preserveCase = true,
		TextSize = props.TextSize or 18,
		Size = UDim2.fromScale(1, 1),
	})
	return frame
end
-- Close: an oversized art button over the top-right corner (a third outside), native danger icon otherwise.
function Kit.closeButton(parent: Instance, onActivated: () -> (), size: number?): GuiButton
	local n = math.max(48, size or 48)
	local entry = Kit.artFor("close") or Kit.artFor("icon-close")
	local btn: GuiButton
	if entry then
		btn = make("ImageButton", {
			Name = "Close",
			BackgroundTransparency = 1,
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.new(1, -n / 6, 0, n / 6),
			Size = UDim2.fromOffset(n, n),
			ZIndex = 8,
			Selectable = true,
			Parent = parent,
		})
		Kit.applyArt(btn :: ImageButton, entry)
		local scale = make("UIScale", { Parent = btn })
		btn.MouseButton1Down:Connect(function()
			Kit.tween(scale, 0.06, { Scale = active.motion.press })
		end)
		btn.MouseButton1Up:Connect(function()
			Kit.tween(scale, 0.15, { Scale = 1 }, ease())
		end)
		btn.MouseLeave:Connect(function()
			Kit.tween(scale, 0.15, { Scale = 1 }, ease())
		end)
		btn.Activated:Connect(function()
			if Kit.onClick then
				Kit.onClick()
			end
			onActivated()
		end)
	else
		btn = Kit.iconButton(
			parent,
			{ Name = "Close", icon = "close", style = "danger", size = n, onActivated = onActivated }
		)
		btn.AnchorPoint = Vector2.new(0.5, 0.5)
		btn.Position = UDim2.new(1, -n / 6, 0, n / 6)
		btn.ZIndex = 8
	end
	return btn
end
-- A meter: recessed track and a fill that slides. Returns the track and a setter (fraction 0..1).
function Kit.bar(parent: Instance, props: { [string]: any }): (Frame, (number) -> ())
	local h = props.height or 24
	local track = make("Frame", {
		Name = props.Name or "Bar",
		Size = props.Size or UDim2.fromOffset(props.width or 220, h),
		Position = props.Position or UDim2.new(),
		AnchorPoint = props.AnchorPoint or Vector2.zero,
		BorderSizePixel = 0,
		Parent = parent,
	}, { Kit.corner(h / 2), Kit.stroke() })
	local trackPlate = make(
		"ImageLabel",
		{ Name = "Plate", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), Parent = track }
	)
	local fill = make("ImageLabel", {
		Name = "Fill",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(0, 1),
		ZIndex = 2,
		Parent = track,
	}, { Kit.corner(h / 2) })
	local minWidth = make("UISizeConstraint", { Parent = fill })
	local fraction = props.value or 0
	local function layout()
		local a, f = roleArt("barTrack"), roleArt("barFill")
		local inset = if a then 0 else 3
		track.BackgroundTransparency = if a then 1 else 0
		track.BackgroundColor3 = active.color.surfaceAlt;
		(track:FindFirstChildOfClass("UIStroke") :: UIStroke).Enabled = a == nil
		trackPlate.Visible = a ~= nil
		if a then
			Kit.applyArt(trackPlate, a)
		end
		fill.Position = UDim2.fromOffset(inset, inset)
		fill.BackgroundTransparency = if f then 1 else 0
		fill.BackgroundColor3 = props.color or active.color.secondary
		fill.Image = ""
		if f then
			-- Draw the fill art light (near white): ImageColor3 then tints it to the bar's colour.
			Kit.applyArt(fill, f)
			fill.ImageColor3 = props.color or active.color.secondary
		end
		-- Scale-sized so ancestor UIScales don't matter; a sliced fill never gets narrower than its two caps.
		fill.Size = UDim2.new(fraction, -inset * 2 * fraction, 1, -inset * 2)
		minWidth.MinSize = Vector2.new(if f and f.slice and fraction > 0 then h else 0, 0)
		fill.Visible = fraction > 0
	end
	bind(track, layout)
	local function set(v: number)
		fraction = math.clamp(v, 0, 1)
		layout()
	end
	return track, set
end
-- A full-screen illustrated background (named art or the theme's `backdrop`), cropped to fill and dimmed by
-- `dim` (0..1). Without art it is the theme scrim. Parent it to a ScreenGui whose ScreenInsets is None.
function Kit.backdrop(parent: Instance, props: { [string]: any }?): GuiObject
	local p = props or {}
	local entry = Kit.artFor(p.art or "backdrop")
	if not entry then
		return Kit.scrim(parent, p)
	end
	local img = make("ImageLabel", {
		Name = p.Name or "Backdrop",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ScaleType = Enum.ScaleType.Crop,
		Image = entry.image,
		ZIndex = p.ZIndex or 1,
		Parent = parent,
	})
	if (p.dim or 0) > 0 then
		make("Frame", {
			Name = "Dim",
			Size = UDim2.fromScale(1, 1),
			BackgroundColor3 = active.color.scrim,
			BackgroundTransparency = 1 - p.dim,
			BorderSizePixel = 0,
			ZIndex = 2,
			Parent = img,
		})
	end
	return img
end
function Kit.pop(obj: GuiObject, visible: boolean, delay: number?)
	local scale = obj:FindFirstChildOfClass("UIScale") or make("UIScale", { Parent = obj })
	obj.Visible = visible
	if visible then
		scale.Scale = if Kit.reducedMotion or GuiService.ReducedMotionEnabled
			then 1
			else active.motion.popFrom
		task.delay(delay or 0, function()
			if obj.Parent then
				Kit.tween(scale, active.motion.popTime, { Scale = 1 }, ease())
			end
		end)
	end
end
function Kit.punch(obj: GuiObject, amount: number?)
	if Kit.reducedMotion or GuiService.ReducedMotionEnabled then
		return
	end
	local scale = obj:FindFirstChildOfClass("UIScale") or make("UIScale", { Parent = obj })
	scale.Scale = amount or 1.25
	Kit.tween(scale, active.motion.popTime, { Scale = 1 }, ease())
end
function Kit.roll(label: TextLabel, value: number, format: ((number) -> string)?)
	local old = label:FindFirstChild("Roll")
	if old then
		old:Destroy()
	end
	local n =
		make("NumberValue", { Name = "Roll", Value = label:GetAttribute("Number") or 0, Parent = label })
	label:SetAttribute("Number", value)
	n.Changed:Connect(function(v)
		label.Text = if format then format(v) else tostring(math.floor(v))
	end)
	Kit.tween(n, 0.8, { Value = value })
	label.Text = if format then format(n.Value) else tostring(math.floor(n.Value))
end
return Kit
