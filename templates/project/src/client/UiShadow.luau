--!strict
-- One renderer boundary: native shadows on current clients, stacked shapes on older builds.
local Shadows = {}
local available, sample = pcall(Instance.new, "UIShadow")
if available then
	sample:Destroy()
end
Shadows.available = available

export type Options = {
	color: Color3,
	alpha: number?,
	x: number?,
	y: number?,
	blur: number?,
	spread: number?,
	inset: boolean?,
	text: boolean?,
	enabled: boolean?,
	order: number?,
}

function Shadows.create(parent: GuiObject, name: string): (Options) -> ()
	local shadow: any
	local fallback: GuiObject?
	local options: Options = { color = Color3.new() }
	if available then
		shadow = Instance.new("UIShadow")
		shadow.Name = name
		shadow.Parent = parent
	end
	local function update()
		if shadow then
			-- UIShadow pixel units do not inherit UIScale. Include nested button/pop scales too.
			local scale = 1
			local node: Instance? = parent
			while node do
				local uiScale = node:FindFirstChildOfClass("UIScale")
				if uiScale then
					scale *= uiScale.Scale
				end
				node = node.Parent
			end
			shadow.Color = options.color
			shadow.Transparency = options.alpha or 0
			shadow.BlurRadius = UDim.new(0, (options.blur or 0) * scale)
			shadow.Offset = UDim2.fromOffset((options.x or 0) * scale, (options.y or 0) * scale)
			shadow.Spread = UDim2.fromOffset((options.spread or 0) * scale, (options.spread or 0) * scale)
			shadow.Enabled = options.enabled ~= false
			shadow.ZIndex = options.order or 1
			-- A build may have shape shadows but predate the upgraded text/inset properties.
			local upgraded = pcall(function()
				shadow.Inset = options.inset == true
				shadow.Mode = if options.text then Enum.ApplyShadowMode.Text else Enum.ApplyShadowMode.Shape
			end)
			if upgraded or not (options.inset or options.text) then
				return
			end
			shadow.Enabled = false
		end
		-- Older clients retain Kit.text's UIStroke. A glyph copy would participate in UIListLayout.
		if options.text then
			return
		end
		-- Compatibility only: stacked hard shapes approximate the native shape shadows.
		if not fallback then
			local frame = Instance.new("Frame")
			frame.BorderSizePixel = 0
			fallback = frame
			fallback.Name = name .. "Fallback"
		end
		local sourceCorner = parent:FindFirstChildOfClass("UICorner")
		if sourceCorner then
			local corner = fallback:FindFirstChildOfClass("UICorner") or sourceCorner:Clone()
			corner.CornerRadius = sourceCorner.CornerRadius
			corner.Parent = fallback
		end
		local f = fallback :: any
		f.Parent = if options.inset then parent else parent.Parent
		f.ZIndex = math.max(1, parent.ZIndex - 1)
		f.Visible = options.enabled ~= false and parent.Visible
		f.AnchorPoint = if options.inset then Vector2.zero else parent.AnchorPoint
		f.Size = if options.inset then UDim2.new(1, 0, 0, math.max(2, options.y or 4)) else parent.Size
		f.Position = if options.inset
			then UDim2.new()
			else parent.Position + UDim2.fromOffset(options.x or 0, options.y or 0)
		f.BackgroundColor3, f.BackgroundTransparency = options.color, options.alpha or 0
	end
	-- AbsoluteSize changes with every ancestor UIScale, including animated press/pop scales.
	local connections = {}
	for _, prop in { "AbsoluteSize", "Position", "Size", "Visible" } do
		table.insert(connections, parent:GetPropertyChangedSignal(prop):Connect(update))
	end
	table.insert(connections, parent.AncestryChanged:Connect(update))
	parent.Destroying:Once(function()
		for _, connection in connections do
			connection:Disconnect()
		end
		if fallback then
			fallback:Destroy()
		end
	end)
	return function(nextOptions: Options)
		options = nextOptions
		update()
	end
end
return Shadows
