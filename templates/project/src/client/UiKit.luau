--!strict
-- The game's UI kit: one theme, one set of components, one motion language.
-- Every screen is built from these so the whole game reads as one designed thing:
-- cream panels with an ink outline and a drop shadow, chunky buttons with a lip that
-- presses down, drawn icons (no uploaded images), pills for numbers, a switch for settings.
-- Layout is authored at a 1100x620 reference and scaled by one UIScale per screen, so a
-- phone in landscape (about 844x390) keeps 44-point touch targets and nothing overflows.
local GuiService = game:GetService("GuiService")
local TweenService = game:GetService("TweenService")

local Kit = {}

Kit.Theme = {
	Ink = Color3.fromRGB(16, 52, 64),
	InkSoft = Color3.fromRGB(44, 92, 104),
	Cream = Color3.fromRGB(255, 249, 232),
	CreamShade = Color3.fromRGB(232, 220, 190),
	Lime = Color3.fromRGB(196, 242, 92),
	LimeShade = Color3.fromRGB(122, 178, 48),
	Coral = Color3.fromRGB(255, 122, 132),
	CoralShade = Color3.fromRGB(206, 74, 92),
	Aqua = Color3.fromRGB(86, 214, 204),
	AquaShade = Color3.fromRGB(40, 150, 150),
	Sun = Color3.fromRGB(255, 200, 70),
	SunShade = Color3.fromRGB(214, 140, 30),
	Muted = Color3.fromRGB(196, 202, 186),
	Display = Font.new("rbxasset://fonts/families/FredokaOne.json"),
	Body = Font.new("rbxasset://fonts/families/BuilderSans.json", Enum.FontWeight.Bold),
	BodyHeavy = Font.new("rbxasset://fonts/families/BuilderSans.json", Enum.FontWeight.ExtraBold),
	Radius = 18,
	Stroke = 3,
	Lip = 6,
	Ref = Vector2.new(1100, 620),
}
local T = Kit.Theme

Kit.reducedMotion = false
Kit.onClick = nil :: (() -> ())?

local function make(class: string, props: { [string]: any }, children: { Instance }?): any
	local inst = Instance.new(class)
	for k, v in props do
		if k ~= "Parent" then
			(inst :: any)[k] = v
		end
	end
	for _, c in children or {} do
		c.Parent = inst
	end
	if props.Parent then
		inst.Parent = props.Parent
	end
	return inst
end
Kit.make = make

local function corner(r: number?): UICorner
	return make("UICorner", { CornerRadius = UDim.new(0, r or T.Radius) })
end
local function stroke(color: Color3?, thickness: number?): UIStroke
	return make("UIStroke", {
		Color = color or T.Ink,
		Thickness = thickness or T.Stroke,
		ApplyStrokeMode = Enum.ApplyStrokeMode.Border,
	})
end
Kit.corner, Kit.stroke = corner, stroke

local function tween(
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
		return
	end
	TweenService
		:Create(obj, TweenInfo.new(t, style or Enum.EasingStyle.Quad, dir or Enum.EasingDirection.Out), props)
		:Play()
end
Kit.tween = tween

-- A screen: a ScreenGui whose root is scaled from the 1100x620 reference.
function Kit.screen(
	parent: Instance,
	name: string,
	order: number,
	insets: Enum.ScreenInsets?
): (ScreenGui, Frame)
	local gui = make("ScreenGui", {
		Name = name,
		ResetOnSpawn = false,
		IgnoreGuiInset = false,
		DisplayOrder = order,
		ScreenInsets = insets or Enum.ScreenInsets.CoreUISafeInsets,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
		Parent = parent,
	})
	local root = make("Frame", { Name = "Root", BackgroundTransparency = 1, Parent = gui })
	local scale = make("UIScale", { Parent = root })
	local function fit()
		local size = gui.AbsoluteSize
		if size.X < 1 then
			return
		end
		local s = math.clamp(math.min(size.X / T.Ref.X, size.Y / T.Ref.Y), 0.6, 1.35)
		scale.Scale = s
		root.Size = UDim2.fromOffset(size.X / s, size.Y / s)
	end
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(fit)
	task.defer(fit)
	fit()
	return gui, root
end

function Kit.text(parent: Instance, props: { [string]: any }): TextLabel
	local p = {
		BackgroundTransparency = 1,
		FontFace = if props.display then T.Display else T.Body,
		TextColor3 = T.Ink,
		TextSize = 20,
		Size = UDim2.fromOffset(200, 30),
		TextWrapped = true,
		Parent = parent,
	}
	for k, v in props do
		if k ~= "display" and k ~= "outline" then
			p[k] = v
		end
	end
	-- TextSize stops at 100; past that, keep 100 and scale the label (its frame shrinks to match)
	local factor = 1
	if p.TextSize > 100 then
		factor = p.TextSize / 100
		p.TextSize = 100
		local sz: UDim2 = p.Size
		p.Size = UDim2.new(sz.X.Scale, sz.X.Offset / factor, sz.Y.Scale, sz.Y.Offset / factor)
	end
	local l = make("TextLabel", p)
	if factor ~= 1 then
		l:SetAttribute("BaseScale", factor)
		make("UIScale", { Scale = factor, Parent = l })
	end
	if props.outline then
		make(
			"UIStroke",
			{ Color = T.Ink, Thickness = props.outline, LineJoinMode = Enum.LineJoinMode.Round, Parent = l }
		)
	end
	return l
end

-- A panel: cream face, ink outline, a soft shadow below.
function Kit.panel(parent: Instance, props: { [string]: any }): Frame
	local holder = make("Frame", {
		Name = props.Name or "Panel",
		Size = props.Size,
		Position = props.Position or UDim2.fromScale(0.5, 0.5),
		AnchorPoint = props.AnchorPoint or Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Parent = parent,
	})
	make("Frame", {
		Name = "Shadow",
		Size = UDim2.fromScale(1, 1),
		Position = UDim2.fromOffset(0, 8),
		BackgroundColor3 = T.Ink,
		BackgroundTransparency = 0.72,
		ZIndex = 0,
		Parent = holder,
	}, { corner(props.radius) })
	local face = make("Frame", {
		Name = "Face",
		Size = UDim2.fromScale(1, 1),
		BackgroundColor3 = props.color or T.Cream,
		ZIndex = 1,
		Parent = holder,
	}, { corner(props.radius), stroke(T.Ink, props.stroke) })
	if props.gradient ~= false then
		make("UIGradient", {
			Rotation = 90,
			Color = ColorSequence.new(Color3.new(1, 1, 1), Color3.fromRGB(238, 238, 238)),
			Parent = face,
		})
	end
	return face
end

local STYLES = {
	primary = { T.Lime, T.LimeShade, T.Ink },
	secondary = { T.Cream, T.CreamShade, T.Ink },
	accent = { T.Aqua, T.AquaShade, T.Ink },
	danger = { T.Coral, T.CoralShade, T.Ink },
	reward = { T.Sun, T.SunShade, T.Ink },
}

-- A chunky button: the face sits on a darker lip and presses down onto it.
function Kit.button(parent: Instance, props: { [string]: any }): TextButton
	local fill, shade, ink = table.unpack(STYLES[props.style or "primary"])
	local lip = props.lip or T.Lip
	local btn = make("TextButton", {
		Name = props.Name or "Button",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Size = props.Size or UDim2.fromOffset(240, 64),
		Position = props.Position or UDim2.new(),
		AnchorPoint = props.AnchorPoint or Vector2.zero,
		Selectable = true,
		Parent = parent,
	})
	make("Frame", {
		Name = "Lip",
		Size = UDim2.fromScale(1, 1),
		Position = UDim2.fromOffset(0, lip),
		BackgroundColor3 = shade,
		ZIndex = 1,
		Parent = btn,
	}, { corner(props.radius or 16), stroke(ink, T.Stroke) })
	local face = make("Frame", {
		Name = "Face",
		Size = UDim2.fromScale(1, 1),
		BackgroundColor3 = fill,
		ZIndex = 2,
		Parent = btn,
	}, { corner(props.radius or 16), stroke(ink, T.Stroke) })
	make("UIGradient", {
		Rotation = 90,
		Color = ColorSequence.new(Color3.new(1, 1, 1), Color3.fromRGB(226, 226, 226)),
		Parent = face,
	})
	local row = make(
		"Frame",
		{ Name = "Row", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), ZIndex = 3, Parent = face },
		{
			make("UIListLayout", {
				FillDirection = Enum.FillDirection.Horizontal,
				HorizontalAlignment = Enum.HorizontalAlignment.Center,
				VerticalAlignment = Enum.VerticalAlignment.Center,
				Padding = UDim.new(0, 10),
				SortOrder = Enum.SortOrder.LayoutOrder,
			}),
		}
	)
	if props.icon then
		local ic = Kit.icon(row, props.icon, ink, props.iconSize or 28)
		ic.LayoutOrder = 1
	end
	if props.text then
		local label = Kit.text(row, {
			Name = "Label",
			Text = props.text,
			display = true,
			TextSize = props.TextSize or 28,
			TextColor3 = ink,
			AutomaticSize = Enum.AutomaticSize.X,
			Size = UDim2.fromScale(0, 1),
			TextWrapped = false,
			LayoutOrder = 2,
			ZIndex = 3,
		})
		label.Name = "Label"
	end
	if props.hint then -- a key/button hint chip, e.g. "Space"
		local chip = make("Frame", {
			Name = "Hint",
			BackgroundColor3 = T.Ink,
			BackgroundTransparency = 0.15,
			AutomaticSize = Enum.AutomaticSize.X,
			Size = UDim2.fromOffset(0, 26),
			LayoutOrder = 3,
			ZIndex = 3,
			Parent = row,
		}, { corner(8), make("UIPadding", { PaddingLeft = UDim.new(0, 8), PaddingRight = UDim.new(0, 8) }) })
		Kit.text(chip, {
			Name = "Key",
			Text = props.hint,
			TextSize = 15,
			TextColor3 = T.Cream,
			AutomaticSize = Enum.AutomaticSize.X,
			Size = UDim2.fromScale(0, 1),
			TextWrapped = false,
			ZIndex = 4,
		})
	end
	local scale = make("UIScale", { Parent = btn })
	local sel = make("Frame", {
		Name = "Selection",
		BackgroundTransparency = 1,
		Size = UDim2.new(1, 12, 1, 12 + lip),
		Position = UDim2.fromOffset(-6, -6),
	}, { corner((props.radius or 16) + 6), stroke(T.Sun, 4) })
	btn.SelectionImageObject = sel
	local down = false
	local function set(pressed: boolean)
		down = pressed
		tween(face, 0.06, { Position = UDim2.fromOffset(0, if pressed then lip - 1 else 0) })
	end
	btn.MouseEnter:Connect(function()
		tween(scale, 0.12, { Scale = 1.04 }, Enum.EasingStyle.Back)
	end)
	btn.MouseLeave:Connect(function()
		tween(scale, 0.12, { Scale = 1 })
		if down then
			set(false)
		end
	end)
	btn.SelectionGained:Connect(function()
		tween(scale, 0.12, { Scale = 1.04 }, Enum.EasingStyle.Back)
	end)
	btn.SelectionLost:Connect(function()
		tween(scale, 0.12, { Scale = 1 })
	end)
	btn.MouseButton1Down:Connect(function()
		set(true)
	end)
	btn.MouseButton1Up:Connect(function()
		set(false)
	end)
	btn.Activated:Connect(function()
		if Kit.onClick then
			Kit.onClick()
		end
		if props.onActivated then
			props.onActivated()
		end
	end)
	return btn
end

-- A square icon button (pause, settings, close).
function Kit.iconButton(parent: Instance, props: { [string]: any }): TextButton
	local size = props.size or 56
	return Kit.button(parent, {
		Name = props.Name,
		style = props.style or "secondary",
		icon = props.icon,
		iconSize = math.floor(size * 0.5),
		Size = UDim2.fromOffset(size, size),
		Position = props.Position,
		AnchorPoint = props.AnchorPoint,
		radius = 14,
		lip = 5,
		onActivated = props.onActivated,
	})
end

-- Icons drawn from frames, so the game needs no uploaded images.
function Kit.icon(parent: Instance, kind: string, color: Color3, size: number): Frame
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
		local t = Kit.text(
			box,
			{ Text = "▶", TextSize = size, Size = UDim2.fromScale(1, 1), TextColor3 = color, ZIndex = 4 }
		)
		t.FontFace = T.Body
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

-- A pill showing a number with an icon (HUD counters).
function Kit.pill(parent: Instance, props: { [string]: any }): (Frame, TextLabel)
	local pill = make("Frame", {
		Name = props.Name or "Pill",
		AutomaticSize = Enum.AutomaticSize.X,
		Size = UDim2.fromOffset(0, props.height or 48),
		Position = props.Position or UDim2.new(),
		AnchorPoint = props.AnchorPoint or Vector2.zero,
		BackgroundColor3 = props.color or T.Cream,
		Parent = parent,
	}, {
		corner(24),
		stroke(T.Ink, T.Stroke),
		make("UIPadding", { PaddingLeft = UDim.new(0, 8), PaddingRight = UDim.new(0, 16) }),
		make("UIListLayout", {
			FillDirection = Enum.FillDirection.Horizontal,
			VerticalAlignment = Enum.VerticalAlignment.Center,
			Padding = UDim.new(0, 8),
			SortOrder = Enum.SortOrder.LayoutOrder,
		}),
	})
	if props.icon then
		local badge = make("Frame", {
			Name = "Badge",
			Size = UDim2.fromOffset(34, 34),
			BackgroundColor3 = props.iconBg or T.Ink,
			LayoutOrder = 1,
			Parent = pill,
		}, { corner(17) })
		local ic = Kit.icon(badge, props.icon, props.iconColor or T.Cream, 22)
		ic.AnchorPoint = Vector2.new(0.5, 0.5)
		ic.Position = UDim2.fromScale(0.5, 0.5)
	end
	local label = Kit.text(pill, {
		Name = "Value",
		Text = props.text or "",
		display = true,
		TextSize = props.TextSize or 26,
		AutomaticSize = Enum.AutomaticSize.X,
		Size = UDim2.fromScale(0, 1),
		TextWrapped = false,
		LayoutOrder = 2,
	})
	return pill, label
end

-- An on/off switch. Returns the row and a setter.
function Kit.switch(parent: Instance, props: { [string]: any }): (TextButton, (boolean) -> ())
	local value = props.value == true
	local row = make("TextButton", {
		Name = props.Name or "Switch",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Size = props.Size or UDim2.new(1, 0, 0, 64),
		LayoutOrder = props.LayoutOrder or 0,
		Selectable = true,
		Parent = parent,
	})
	Kit.text(row, {
		Name = "Label",
		Text = props.text,
		TextSize = 24,
		Size = UDim2.new(1, -110, 1, 0),
		TextXAlignment = Enum.TextXAlignment.Left,
		FontFace = T.BodyHeavy,
	})
	local track = make("Frame", {
		Name = "Track",
		AnchorPoint = Vector2.new(1, 0.5),
		Position = UDim2.fromScale(1, 0.5),
		Size = UDim2.fromOffset(86, 44),
		BackgroundColor3 = T.Muted,
		Parent = row,
	}, { corner(22), stroke(T.Ink, T.Stroke) })
	local knob = make("Frame", {
		Name = "Knob",
		AnchorPoint = Vector2.new(0, 0.5),
		Position = UDim2.new(0, 4, 0.5, 0),
		Size = UDim2.fromOffset(36, 36),
		BackgroundColor3 = T.Cream,
		Parent = track,
	}, { corner(18), stroke(T.Ink, 2) })
	local sel = make(
		"Frame",
		{ BackgroundTransparency = 1, Size = UDim2.new(1, 12, 1, 4), Position = UDim2.fromOffset(-6, -2) },
		{ corner(14), stroke(T.Sun, 4) }
	)
	row.SelectionImageObject = sel
	local function set(v: boolean)
		value = v
		tween(
			knob,
			0.18,
			{ Position = if v then UDim2.new(1, -40, 0.5, 0) else UDim2.new(0, 4, 0.5, 0) },
			Enum.EasingStyle.Back
		)
		tween(track, 0.18, { BackgroundColor3 = if v then T.Lime else T.Muted })
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

-- Show and hide with a pop: modal panels grow from 0.88 with a slight overshoot.
function Kit.pop(obj: GuiObject, visible: boolean, delay: number?)
	local scale = obj:FindFirstChildOfClass("UIScale") or make("UIScale", { Parent = obj })
	if visible then
		obj.Visible = true
		scale.Scale = if Kit.reducedMotion then 1 else 0.88
		task.delay(delay or 0, function()
			tween(scale, 0.28, { Scale = 1 }, Enum.EasingStyle.Back)
		end)
	else
		obj.Visible = false
	end
end

-- Punch a value change (a counter ticking up): scale 1.25 back to 1.
function Kit.punch(obj: GuiObject, amount: number?)
	if Kit.reducedMotion then
		return
	end
	local base = obj:GetAttribute("BaseScale") or 1
	local scale = obj:FindFirstChildOfClass("UIScale") or make("UIScale", { Parent = obj })
	scale.Scale = base * (amount or 1.22)
	tween(scale, 0.3, { Scale = base }, Enum.EasingStyle.Back)
end

return Kit
