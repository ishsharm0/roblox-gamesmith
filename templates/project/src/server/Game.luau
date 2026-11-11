--!strict
-- The server-owned rules: one session per player (Title -> Play -> Results -> Play), every intent checked against
-- the phase, every Act rate-limited and judged here, state published as player attributes and one Event.
-- The zone is public, so a cheat can aim; it cannot out-run the meter (Rules.holdPlausible) or skip a phase.
-- A new game keeps this state machine and swaps the Act handler's judgement (Rules.judge, pickTarget).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Shared.Config)
local Net = require(ReplicatedStorage.Shared.Net)
local Rules = require(ReplicatedStorage.Shared.Rules)
local PlayerData = require(script.Parent.PlayerData)

type Session = {
	phase: string,
	score: number,
	combo: number,
	lives: number,
	endsAt: number,
	lastAct: number,
	target: number,
	zone: number,
	timeShown: number,
}

local Game = {}
local sessions: { [Player]: Session } = {}
local rng = Random.new()

local function publish(player: Player, s: Session)
	player:SetAttribute("Score", s.score)
	player:SetAttribute("Combo", s.combo)
	player:SetAttribute("Lives", s.lives)
	player:SetAttribute("Target", s.target)
	player:SetAttribute("Zone", s.zone)
end

local function pickTarget(s: Session)
	s.target, s.zone = Rules.nextTarget(s.target, rng, Config)
end

local function startRound(player: Player, s: Session)
	local now = os.clock()
	s.score, s.combo, s.lives = 0, 0, Config.Lives
	s.endsAt = now + Config.RoundSeconds
	s.lastAct = now
	s.timeShown = Config.RoundSeconds
	s.target = 0
	pickTarget(s)
	local data = PlayerData.get(player)
	if data then
		data.Plays += 1
	end
	publish(player, s)
	player:SetAttribute("TimeLeft", Config.RoundSeconds)
	player:SetAttribute("Stars", 0)
	s.phase = Net.Phase.Play
	player:SetAttribute("Phase", s.phase)
end

local function endRound(player: Player, s: Session)
	local data = PlayerData.get(player)
	if data and s.score > data.Best then
		data.Best = s.score
	end
	player:SetAttribute("TimeLeft", 0)
	player:SetAttribute("Best", if data then data.Best else s.score)
	player:SetAttribute("Stars", Rules.starsFor(s.score, Config))
	s.phase = Net.Phase.Results
	player:SetAttribute("Phase", s.phase) -- last: the client reads the numbers above when this changes
	PlayerData.saveSoon(player)
end

local function act(player: Player, s: Session, amount: any)
	if type(amount) ~= "number" or amount ~= amount then
		return
	end
	local now = os.clock()
	if now >= s.endsAt then
		endRound(player, s) -- the timer loop has not run yet; this Act came too late
		return
	end
	local since = now - s.lastAct
	if since < Config.ActInterval then
		return
	end
	amount = math.clamp(amount, 0, 1)
	if not Rules.holdPlausible(amount, since, Config) then
		return -- released sooner than the meter could have reached that value
	end
	s.lastAct = now
	local grade = Rules.judge(amount, s.zone, s.combo, Config)
	local points = Rules.scoreFor(grade, s.combo, Config)
	local orb = s.target
	if grade == "MISS" then
		s.combo = 0
		s.lives -= 1
	else
		s.combo += 1
		s.score += points
	end
	Net.Event:FireClient(player, "Grade", grade, orb, points, s.combo)
	if s.lives <= 0 then
		publish(player, s)
		endRound(player, s)
	else
		pickTarget(s)
		publish(player, s)
	end
end

-- Every client request lands here. Anything malformed or out of phase is ignored.
function Game.handle(player: Player, intent: any, payload: any)
	local s = sessions[player]
	if not s or type(intent) ~= "string" then
		return
	end
	if intent == Net.Intent.Start then
		if s.phase ~= Net.Phase.Play then
			startRound(player, s)
		end
	elseif intent == Net.Intent.Act then
		if s.phase == Net.Phase.Play then
			act(player, s, payload)
		end
	elseif intent == Net.Intent.Menu then
		if s.phase == Net.Phase.Results then
			s.phase = Net.Phase.Title
			player:SetAttribute("Phase", s.phase)
		end
	end
end

local function onPlayerAdded(player: Player)
	local data = PlayerData.load(player)
	if player.Parent ~= Players then
		PlayerData.release(player)
		return
	end
	sessions[player] = {
		phase = Net.Phase.Title,
		score = 0,
		combo = 0,
		lives = Config.Lives,
		endsAt = 0,
		lastAct = 0,
		target = 0,
		zone = 0.5,
		timeShown = 0,
	}
	player:SetAttribute("Best", data.Best)
	player:SetAttribute("Phase", Net.Phase.Title)
end

local function onCharacterAdded(character: Model)
	local humanoid = character:WaitForChild("Humanoid", 10) :: Humanoid? -- the avatar only watches
	if humanoid then
		humanoid.WalkSpeed = 0
		humanoid.JumpPower = 0
		humanoid.JumpHeight = 0
	end
end

local function track(player: Player)
	player.CharacterAdded:Connect(onCharacterAdded)
	if player.Character then
		task.spawn(onCharacterAdded, player.Character)
	end
	onPlayerAdded(player)
end

function Game.start()
	PlayerData.start()
	Net.Action.OnServerEvent:Connect(Game.handle)
	Players.PlayerAdded:Connect(track)
	Players.PlayerRemoving:Connect(function(player)
		sessions[player] = nil
		PlayerData.release(player)
	end)
	for _, player in Players:GetPlayers() do
		task.spawn(track, player)
	end
	-- the round timer: one loop for every session, so leaving players need no cleanup of their own
	task.spawn(function()
		while true do
			task.wait(0.1)
			local now = os.clock()
			for player, s in sessions do
				if s.phase == Net.Phase.Play then
					local left = math.max(0, s.endsAt - now)
					local shown = math.ceil(left)
					if shown ~= s.timeShown then
						s.timeShown = shown
						player:SetAttribute("TimeLeft", shown)
					end
					if left <= 0 then
						endRound(player, s)
					end
				end
			end
		end
	end)
end

return Game
