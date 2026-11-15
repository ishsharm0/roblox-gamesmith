--!strict
-- Token-driven UI, authored at 844x390; 16px text and 48px interactive targets never scale down.
local GuiService = game:GetService("GuiService")
local TweenService = game:GetService("TweenService")
local Themes = require(game:GetService("ReplicatedStorage"):WaitForChild("Shared").Themes)
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
local function drop(parent: GuiObject, offset: number?)
	shadow(parent, "Shadow", function()
		return {
			color = Color3.new(),
			y = offset or active.shape.shadow,
			alpha = 1 - active.shape.shadowAlpha,
			enabled = active.shape.shadowAlpha > 0,
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
	local function fit()
		local v = gui.AbsoluteSize
		if v.X < 1 then
			return
		end
		local s = math.clamp(math.min(v.X / T.Ref.X, v.Y / T.Ref.Y), 1, 2)
		scale.Scale = s
		root.Size = UDim2.fromOffset(v.X / s, v.Y / s)
	end
	local conn = gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(fit)
	gui.Destroying:Once(function()
		conn:Disconnect()
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
	local face = make(
		"Frame",
		{ Name = "Face", Size = UDim2.fromScale(1, 1), BorderSizePixel = 0, ZIndex = 2, Parent = holder },
		{ Kit.corner(props.radius), Kit.stroke() }
	)
	bind(face, function()
		local c = active.color
		gradient(
			face,
			c.surfaceTop or c.surface,
			props.color or c.surface,
			c.surfaceTop ~= nil and props.color == nil
		)
	end)
	drop(face)
	glow(face)
	if props.title then
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
function Kit.button(parent: Instance, props: { [string]: any }): TextButton
	local btn = make("TextButton", {
		Name = props.Name or "Button",
		ZIndex = props.ZIndex or 1,
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Size = props.Size or UDim2.fromOffset(260, 64),
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
	local down = false
	local function colors()
		return buttonColors(props.style or "primary", not btn:GetAttribute("Disabled"))
	end
	local row = make(
		"Frame",
		{ Name = "Row", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, ZIndex = 3, Parent = face },
		{
			make("UIListLayout", {
				FillDirection = Enum.FillDirection.Horizontal,
				HorizontalAlignment = Enum.HorizontalAlignment.Center,
				VerticalAlignment = Enum.VerticalAlignment.Center,
				Padding = UDim.new(0, 8),
				SortOrder = Enum.SortOrder.LayoutOrder,
			}),
		}
	)
	local icon: GuiObject? = nil
	if props.icon then
		local _, _, on = colors()
		icon = Kit.icon(row, props.icon, on, props.iconSize or 28)
		icon.ZIndex, icon.LayoutOrder = 4, 1
	end
	local label: TextLabel? = nil
	if props.text then
		label = Kit.text(row, {
			Name = "Label",
			Text = props.text,
			TextSize = props.TextSize or 28,
			button = true,
			TextWrapped = false,
			AutomaticSize = Enum.AutomaticSize.X,
			Size = UDim2.fromScale(0, 1),
			LayoutOrder = 2,
			ZIndex = 4,
			themeColor = function()
				local _, _, on = colors()
				return on
			end,
		})
	end
	local applyDrop = Shadows.create(face, "Shadow")
	local applyLipOutline = Shadows.create(face, "LipOutline")
	local applyLip = Shadows.create(face, "Lip")
	local applyInset = Shadows.create(face, "Pressed")
	glow(face)
	local function update()
		local fill, shade, on = colors()
		local s = active.shape
		local lip = props.lip or s.lip
		btn:SetAttribute("Fill", fill)
		corner.CornerRadius = UDim.new(0, s.buttonRadius)
		-- Absolute colour gradient, matching CSS white-mixed top -> untouched token fill.
		local top = fill:Lerp(Color3.new(1, 1, 1), s.gradient)
		local g = face:FindFirstChild("ThemeGradient")
			or make("UIGradient", { Name = "ThemeGradient", Rotation = 90, Parent = face })
		face.BackgroundColor3 = if down then fill:Lerp(Color3.new(), 0.12) else fill
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
		gloss.Visible = s.gradient > 0 and not down and not btn:GetAttribute("Disabled")
		applyDrop({
			color = Color3.new(),
			y = lip + s.shadow,
			alpha = 1 - s.shadowAlpha,
			enabled = s.shadowAlpha > 0,
			order = 0,
		})
		applyLipOutline({
			color = active.color.outline,
			y = lip + s.stroke,
			enabled = lip > 0 and s.stroke > 0 and not down,
			order = 1,
		})
		applyLip({ color = shade, y = lip, enabled = lip > 0 and not down, order = 2 })
		applyInset({
			color = Color3.new(),
			y = 4,
			blur = 6,
			alpha = 0.55,
			inset = true,
			enabled = down,
			order = 3,
		})
		if label then
			label.TextColor3 = on
		end
		if icon then
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
		Kit.tween(face, if value then 0.06 else 0.15, {
			Position = UDim2.fromOffset(
				0,
				if value then math.max(0, (props.lip or active.shape.lip) - 1) else 0
			),
		})
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
	bind(frame, function()
		frame.BackgroundColor3 = props.color or active.color.surface
	end)
	drop(frame, 4)
	glow(frame)
	if props.icon then
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
	local label = Kit.text(frame, {
		Name = "Value",
		preserveCase = true,
		Text = props.text or "",
		TextSize = props.TextSize or 26,
		display = true,
		Position = UDim2.fromOffset(if props.icon then 37 else 8, 0),
		Size = UDim2.new(1, if props.icon then -45 else -16, 1, 0),
		TextWrapped = false,
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
	bind(frame, function()
		frame.BackgroundColor3 = active.color.toast
	end)
	Kit.text(frame, {
		Text = props.text or "",
		display = true,
		role = "onToast",
		preserveCase = true,
		TextSize = props.TextSize or 18,
		Size = UDim2.fromScale(1, 1),
	})
	return frame
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
