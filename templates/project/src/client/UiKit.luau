--!strict
-- Phone-first toy UI. Generic components; call configureIcons with a public asset map.
-- Author at 844x390. On narrower viewports the canvas reflows at scale 1, preserving 16px text / 48px taps.
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
	Common = Color3.fromRGB(184, 192, 200),
	Uncommon = Color3.fromRGB(111, 209, 107),
	Rare = Color3.fromRGB(77, 163, 255),
	Epic = Color3.fromRGB(168, 107, 255),
	Legendary = Color3.fromRGB(255, 200, 70),
	Display = Font.new("rbxasset://fonts/families/FredokaOne.json"),
	Body = Font.new("rbxasset://fonts/families/BuilderSans.json", Enum.FontWeight.Bold),
	BodyHeavy = Font.new("rbxasset://fonts/families/BuilderSans.json", Enum.FontWeight.ExtraBold),
	Radius = 20,
	Stroke = 3,
	Lip = 6,
	Ref = Vector2.new(844, 390),
}
local T = Kit.Theme
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
	for _, c in children or {} do
		c.Parent = inst
	end
	inst.Parent = props.Parent
	return inst
end
local make = Kit.make
function Kit.corner(radius: number?): UICorner
	return make("UICorner", { CornerRadius = UDim.new(0, radius or T.Radius) })
end
function Kit.stroke(color: Color3?, thickness: number?): UIStroke
	return make("UIStroke", {
		Color = color or T.Ink,
		Thickness = thickness or 3,
		ApplyStrokeMode = Enum.ApplyStrokeMode.Border,
		LineJoinMode = Enum.LineJoinMode.Round,
	})
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
		FontFace = if props.display then T.Display else T.Body,
		TextColor3 = T.Ink,
		TextSize = 18,
		TextWrapped = true,
		Size = UDim2.fromOffset(200, 28),
		Parent = parent,
	}
	for k, v in props do
		if k ~= "display" and k ~= "outline" then
			p[k] = v
		end
	end
	p.TextSize = math.clamp(p.TextSize, 16, 100)
	local l = make("TextLabel", p)
	if props.outline then
		make(
			"UIStroke",
			{ Color = T.Ink, Thickness = props.outline, LineJoinMode = Enum.LineJoinMode.Round, Parent = l }
		)
	end
	return l
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
		Size = props.Size or UDim2.fromOffset(620, 300),
		Position = props.Position or UDim2.fromScale(0.5, 0.5),
		AnchorPoint = props.AnchorPoint or Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Parent = parent,
	})
	make("Frame", {
		Name = "Shadow",
		Size = UDim2.fromScale(1, 1),
		Position = UDim2.fromOffset(0, 10),
		BackgroundColor3 = T.Ink,
		BackgroundTransparency = 0.72,
		Parent = holder,
	}, { Kit.corner(props.radius) })
	local face = make("Frame", {
		Name = "Face",
		Size = UDim2.fromScale(1, 1),
		BackgroundColor3 = props.color or T.Cream,
		Parent = holder,
	}, { Kit.corner(props.radius), Kit.stroke(T.Ink, 4) })
	if props.title then
		local ribbon = make("Frame", {
			Name = "Ribbon",
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.fromScale(0.5, 0),
			Size = UDim2.new(0.7, 0, 0, 52),
			BackgroundColor3 = props.headerColor or T.Aqua,
			ZIndex = 3,
			Parent = face,
		}, { Kit.corner(14), Kit.stroke() })
		Kit.text(
			ribbon,
			{ Text = props.title, display = true, TextSize = 30, Size = UDim2.fromScale(1, 1), ZIndex = 4 }
		)
	end
	return face
end
local styles = {
	primary = { T.Lime, T.LimeShade },
	secondary = { T.Cream, T.CreamShade },
	accent = { T.Aqua, T.AquaShade },
	danger = { T.Coral, T.CoralShade },
	reward = { T.Sun, T.SunShade },
}
function Kit.setButton(btn: TextButton, enabled: boolean, text: string?)
	btn.Interactable = enabled
	btn.Selectable = enabled
	btn:SetAttribute("Disabled", not enabled)
	local face = btn:FindFirstChild("Face") :: Frame
	face.BackgroundColor3 = if enabled then btn:GetAttribute("Fill") else T.Muted
	local gloss = face:FindFirstChild("Gloss") :: Frame
	gloss.Visible = enabled
	local label = face:FindFirstChild("Label", true) :: TextLabel?
	if label then
		label.TextTransparency = if enabled then 0 else 0.35
		if text then
			label.Text = text
		end
	end
end
function Kit.button(parent: Instance, props: { [string]: any }): TextButton
	local colors = styles[props.style or "primary"] or styles.primary
	local lip = props.lip or 6
	local btn = make("TextButton", {
		Name = props.Name or "Button",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Size = props.Size or UDim2.fromOffset(260, 64),
		Position = props.Position or UDim2.new(),
		AnchorPoint = props.AnchorPoint or Vector2.zero,
		Selectable = true,
		Parent = parent,
	})
	btn:SetAttribute("Fill", colors[1])
	make("UISizeConstraint", { MinSize = Vector2.new(48, 48), Parent = btn })
	make("Frame", {
		Name = "Shadow",
		Size = UDim2.fromScale(1, 1),
		Position = UDim2.fromOffset(0, 10),
		BackgroundColor3 = T.Ink,
		BackgroundTransparency = 0.7,
		Parent = btn,
	}, { Kit.corner(16) })
	make("Frame", {
		Name = "Lip",
		Size = UDim2.fromScale(1, 1),
		Position = UDim2.fromOffset(0, lip),
		BackgroundColor3 = colors[2],
		Parent = btn,
	}, { Kit.corner(16), Kit.stroke() })
	local face = make("Frame", {
		Name = "Face",
		Size = UDim2.fromScale(1, 1),
		BackgroundColor3 = colors[1],
		ZIndex = 2,
		Parent = btn,
	}, { Kit.corner(16), Kit.stroke() })
	make("UIGradient", {
		Rotation = 90,
		Color = ColorSequence.new(Color3.new(1, 1, 1), Color3.fromRGB(226, 226, 226)),
		Parent = face,
	})
	make("Frame", {
		Name = "Gloss",
		Position = UDim2.fromOffset(6, 5),
		Size = UDim2.new(1, -12, 0.4, -3),
		BackgroundColor3 = Color3.new(1, 1, 1),
		BackgroundTransparency = 0.8,
		ZIndex = 2,
		Parent = face,
	}, { Kit.corner(10) })
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
	if props.icon then
		local ic = Kit.icon(row, props.icon, T.Ink, props.iconSize or 28)
		ic.ZIndex = 4
		ic.LayoutOrder = 1
	end
	if props.text then
		Kit.text(row, {
			Name = "Label",
			Text = props.text,
			TextSize = props.TextSize or 28,
			display = true,
			TextWrapped = false,
			AutomaticSize = Enum.AutomaticSize.X,
			Size = UDim2.fromScale(0, 1),
			LayoutOrder = 2,
			ZIndex = 4,
		})
	end
	local scale = make("UIScale", { Parent = btn })
	local function press(down: boolean)
		if btn:GetAttribute("Disabled") then
			return
		end
		Kit.tween(
			face,
			if down then 0.06 else 0.15,
			{ Position = UDim2.fromOffset(0, if down then 5 else 0) },
			if down then Enum.EasingStyle.Quad else Enum.EasingStyle.Back
		)
		Kit.tween(
			scale,
			if down then 0.06 else 0.15,
			{ Scale = if down then 0.97 else 1 },
			Enum.EasingStyle.Back
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
	btn.MouseEnter:Connect(function()
		if btn.Interactable then
			Kit.tween(scale, 0.12, { Scale = 1.04 }, Enum.EasingStyle.Back)
		end
	end)
	btn.SelectionGained:Connect(function()
		Kit.tween(scale, 0.12, { Scale = 1.04 }, Enum.EasingStyle.Back)
	end)
	btn.SelectionLost:Connect(function()
		press(false)
	end)
	local sel = make(
		"Frame",
		{ BackgroundTransparency = 1, Size = UDim2.new(1, 10, 1, 16), Position = UDim2.fromOffset(-5, -5) },
		{ Kit.corner(20), Kit.stroke(T.Sun, 4) }
	)
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
	return btn
end
function Kit.iconButton(parent: Instance, props: { [string]: any }): TextButton
	local n = math.max(48, props.size or 52)
	return Kit.button(parent, {
		Name = props.Name,
		Size = UDim2.fromOffset(n, n),
		Position = props.Position,
		AnchorPoint = props.AnchorPoint,
		style = props.style or "secondary",
		icon = props.icon,
		iconSize = props.iconSize or 28,
		onActivated = props.onActivated,
	})
end
function Kit.pill(parent: Instance, props: { [string]: any }): (Frame, TextLabel)
	local h = props.height or 44
	local frame = make("Frame", {
		Name = props.Name or "Pill",
		Size = UDim2.fromOffset(props.width or 148, h),
		Position = props.Position or UDim2.new(),
		AnchorPoint = props.AnchorPoint or Vector2.zero,
		BackgroundColor3 = props.color or T.Cream,
		Parent = parent,
	}, { Kit.corner(h / 2), Kit.stroke() })
	if props.icon then
		local badge = make("Frame", {
			Name = "Badge",
			Size = UDim2.fromOffset(36, 36),
			Position = UDim2.new(0, -3, 0.5, 0),
			AnchorPoint = Vector2.new(0, 0.5),
			BackgroundColor3 = props.iconBg or T.Sun,
			Parent = frame,
		}, { Kit.corner(18), Kit.stroke(T.Ink, 2) })
		local ic = Kit.icon(badge, props.icon, props.iconColor or T.Ink, 26)
		ic.Position = UDim2.fromOffset(5, 5)
	end
	local text = Kit.text(frame, {
		Name = "Value",
		Text = props.text or "",
		TextSize = props.TextSize or 26,
		display = true,
		Position = UDim2.fromOffset(if props.icon then 37 else 8, 0),
		Size = UDim2.new(1, if props.icon then -45 else -16, 1, 0),
		TextWrapped = false,
	})
	return frame, text
end
function Kit.card(parent: Instance, props: { [string]: any }): Frame
	local card = make("Frame", {
		Name = props.Name or "Card",
		Size = props.Size or UDim2.fromOffset(136, 180),
		Position = props.Position or UDim2.new(),
		BackgroundColor3 = T.Cream,
		Parent = parent,
	}, { Kit.corner(14), Kit.stroke() })
	local band = make("Frame", {
		Name = "Band",
		Size = UDim2.new(1, 0, 0, 32),
		BackgroundColor3 = props.color or T.Common,
		Parent = card,
	}, { Kit.corner(14) })
	Kit.text(
		band,
		{ Name = "Rarity", Text = props.rarity or "", Size = UDim2.fromScale(1, 1), TextSize = 16 }
	)
	if props.icon then
		local ic = Kit.icon(card, props.icon, props.iconColor or T.Ink, 60)
		ic.Position = UDim2.new(0.5, -30, 0, 40)
	end
	Kit.text(card, {
		Name = "Name",
		Text = props.text or "",
		TextSize = 16,
		Position = UDim2.fromOffset(6, 104),
		Size = UDim2.new(1, -12, 0, 44),
	})
	return card
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
	Kit.text(row, {
		Text = props.text,
		Size = UDim2.new(1, -110, 1, 0),
		TextXAlignment = Enum.TextXAlignment.Left,
		TextSize = 20,
	})
	local track = make("Frame", {
		Name = "Track",
		Position = UDim2.new(1, -88, 0.5, -22),
		Size = UDim2.fromOffset(88, 44),
		BackgroundColor3 = T.Muted,
		Parent = row,
	}, { Kit.corner(22), Kit.stroke() })
	local knob = make("Frame", {
		Name = "Knob",
		Position = UDim2.fromOffset(4, 4),
		Size = UDim2.fromOffset(36, 36),
		BackgroundColor3 = T.Cream,
		Parent = track,
	}, { Kit.corner(18), Kit.stroke(T.Ink, 2) })
	local function set(v: boolean)
		value = v
		Kit.tween(knob, 0.18, { Position = UDim2.fromOffset(if v then 48 else 4, 4) }, Enum.EasingStyle.Back)
		Kit.tween(track, 0.18, { BackgroundColor3 = if v then T.Lime else T.Muted })
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
function Kit.pop(obj: GuiObject, visible: boolean, delay: number?)
	local scale = obj:FindFirstChildOfClass("UIScale") or make("UIScale", { Parent = obj })
	obj.Visible = visible
	if visible then
		scale.Scale = if Kit.reducedMotion or GuiService.ReducedMotionEnabled then 1 else 0.88
		task.delay(delay or 0, function()
			if obj.Parent then
				Kit.tween(scale, 0.28, { Scale = 1 }, Enum.EasingStyle.Back)
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
	Kit.tween(scale, 0.3, { Scale = 1 }, Enum.EasingStyle.Back)
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
