--!strict
-- Pure game rules, no Roblox APIs, so Lune can test them (tests/rules.luau). The server decides every outcome with
-- these; the client calls them only to draw what the server will decide. Each takes the tuning table (Config).
-- A new game replaces judge and the zone helpers with its own judgement and keeps scoreFor/starsFor's shape.
local Rules = {}

export type Tuning = {
	ChargeSeconds: number,
	ZoneMin: number,
	ZoneMax: number,
	GoodHalfWidth: number,
	PerfectHalfWidth: number,
	ShrinkPerCombo: number,
	MinZoneScale: number,
	HoldSlack: number,
	Points: { PERFECT: number, GOOD: number },
	ComboStep: number,
	MaxMultiplier: number,
	StarScores: { number },
	TargetCount: number,
}
export type Rng = {
	NextInteger: (self: any, min: number, max: number) -> number,
	NextNumber: (self: any) -> number,
}
export type Grade = "PERFECT" | "GOOD" | "MISS"

-- The meter after `held` seconds of holding: up in ChargeSeconds, then back down, forever.
function Rules.meter(held: number, cfg: Tuning): number
	if held ~= held or held <= 0 then
		return 0
	end
	local phase = (held / cfg.ChargeSeconds) % 2
	return if phase <= 1 then phase else 2 - phase
end

-- The fastest a release at `amount` can have been charged: the way up takes amount * ChargeSeconds.
function Rules.holdPlausible(amount: number, secondsSinceLastAct: number, cfg: Tuning): boolean
	return secondsSinceLastAct >= amount * cfg.ChargeSeconds - cfg.HoldSlack
end

-- Half-widths (good, perfect) of the zone while the player has `combo` hits in a row.
function Rules.widths(combo: number, cfg: Tuning): (number, number)
	local scale = math.max(cfg.MinZoneScale, 1 - combo * cfg.ShrinkPerCombo)
	return cfg.GoodHalfWidth * scale, cfg.PerfectHalfWidth * scale
end

function Rules.judge(release: number, zone: number, combo: number, cfg: Tuning): Grade
	if release ~= release then
		return "MISS"
	end
	local good, perfect = Rules.widths(combo, cfg)
	local off = math.abs(math.clamp(release, 0, 1) - zone)
	if off <= perfect then
		return "PERFECT"
	end
	return if off <= good then "GOOD" else "MISS"
end

function Rules.multiplier(combo: number, cfg: Tuning): number
	return math.min(1 + math.max(combo, 0) * cfg.ComboStep, cfg.MaxMultiplier)
end

-- `combo` is the number of hits in a row BEFORE this one.
function Rules.scoreFor(grade: Grade, combo: number, cfg: Tuning): number
	if grade == "MISS" then
		return 0
	end
	local base = if grade == "PERFECT" then cfg.Points.PERFECT else cfg.Points.GOOD
	return math.floor(base * Rules.multiplier(combo, cfg))
end

-- 1 star for finishing a round, plus one for each threshold in StarScores reached.
function Rules.starsFor(score: number, cfg: Tuning): number
	local stars = 1
	if score ~= score then
		return stars
	end
	for _, threshold in cfg.StarScores do
		if score >= threshold then
			stars += 1
		end
	end
	return stars
end

-- A new ring index (never `previous`; pass 0 for none) and a zone centre, both from the given Random.
function Rules.nextTarget(previous: number, rng: Rng, cfg: Tuning): (number, number)
	local index = rng:NextInteger(1, cfg.TargetCount - 1)
	if previous >= 1 and index >= previous then
		index += 1
	end
	return index, cfg.ZoneMin + rng:NextNumber() * (cfg.ZoneMax - cfg.ZoneMin)
end

return Rules
