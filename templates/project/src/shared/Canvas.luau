--!strict
-- The UI reference canvas. Touch screens lay out on the 844x390 phone canvas; mouse and keyboard use a
-- larger 1280x640 canvas so a laptop does not get the phone layout magnified (owner, 17 Nov 2026: "UI is
-- huge"). One UIScale on the root: scale = clamp(min(vw/refX, vh/refY), 1, 1.5). Pure, so Lune tests it.
local Canvas = {}

Canvas.TOUCH = { x = 844, y = 390 }
Canvas.DESKTOP = { x = 1280, y = 640 }
Canvas.MAX = 1.5

function Canvas.ref(touch: boolean): (number, number)
	local r = if touch then Canvas.TOUCH else Canvas.DESKTOP
	return r.x, r.y
end

-- Root scale and the root's size in design px for a viewport.
function Canvas.fit(vx: number, vy: number, touch: boolean): (number, number, number)
	local rx, ry = Canvas.ref(touch)
	local s = math.clamp(math.min(vx / rx, vy / ry), 1, Canvas.MAX)
	return s, vx / s, vy / s
end

return Canvas
