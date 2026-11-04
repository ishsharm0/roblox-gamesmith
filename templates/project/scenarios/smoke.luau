-- Runs on the server during a playtest (rbxgame test scenarios/smoke.luau). Return a short report.
local Players = game:GetService("Players")
local t0 = os.clock()
while #Players:GetPlayers() == 0 and os.clock() - t0 < 10 do
	task.wait(0.2)
end
local p = Players:GetPlayers()[1]
if not p then
	return "FAIL no player joined"
end
local char = p.Character or p.CharacterAdded:Wait()
return ("ok player=%s at %s"):format(p.Name, tostring(char:GetPivot().Position))
