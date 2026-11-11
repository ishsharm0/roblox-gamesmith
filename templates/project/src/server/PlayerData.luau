--!strict
-- Saved player data: a DataStore behind a session cache, every call pcall-wrapped with retries. When the store is
-- unreachable (Studio without API access, an outage) the player plays on in-memory defaults that are never written back.
-- A new game changes DEFAULTS and STORE_NAME. Session locking across servers: references/data.md.
local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")

local STORE_NAME = "PlayerData_v1"
local DEFAULTS = { Best = 0, Plays = 0 }
local TRIES = 3

export type Data = { Best: number, Plays: number }
type Entry = { data: Data, persistent: boolean }

local PlayerData = {}
local cache: { [Player]: Entry } = {}
local store: DataStore? = nil

local function key(player: Player): string
	return "u" .. player.UserId
end

local function copyDefaults(): Data
	return table.clone(DEFAULTS)
end

-- Run fn up to TRIES times with a growing pause; returns (ok, result).
local function retry<T>(fn: () -> T): (boolean, T?)
	for attempt = 1, TRIES do
		local ok, result = pcall(fn)
		if ok then
			return true, result
		end
		if attempt < TRIES then
			task.wait(0.4 * attempt)
		end
	end
	return false, nil
end

-- Fill missing fields and drop wrong types from whatever the store returned.
local function reconcile(raw: any): Data
	local data = copyDefaults()
	if type(raw) == "table" then
		for field, default in DEFAULTS :: { [string]: any } do
			local value = raw[field]
			if type(value) == type(default) and value == value then
				(data :: any)[field] = value
			end
		end
	end
	return data
end

-- Loads (yields) and caches the player's data. Safe to call once per player.
function PlayerData.load(player: Player): Data
	if not store then
		local ok, found = pcall(function()
			return DataStoreService:GetDataStore(STORE_NAME)
		end)
		if ok then
			store = found
		end
	end
	local entry: Entry = { data = copyDefaults(), persistent = false }
	local current = store
	if current then
		local ok, raw = retry(function()
			return current:GetAsync(key(player))
		end)
		if ok then
			entry.data = reconcile(raw)
			entry.persistent = true
		else
			warn("[PlayerData] store unavailable, playing on defaults without saving: " .. player.Name)
		end
	end
	cache[player] = entry
	return entry.data
end

-- The live table (callers write through it), or nil before load / after release.
function PlayerData.get(player: Player): Data?
	local entry = cache[player]
	return if entry then entry.data else nil
end

-- Writes the cached data. Best only ever rises, so a stale server cannot lower a record.
function PlayerData.save(player: Player): boolean
	local entry, current = cache[player], store
	if not entry or not entry.persistent or not current then
		return false
	end
	local snapshot = table.clone(entry.data)
	local ok = retry(function()
		return current:UpdateAsync(key(player), function(old: any)
			local merged = reconcile(old)
			merged.Plays = math.max(merged.Plays, snapshot.Plays)
			merged.Best = math.max(merged.Best, snapshot.Best)
			return merged
		end)
	end)
	return ok
end

-- Saves and forgets a leaving player.
function PlayerData.release(player: Player)
	PlayerData.save(player)
	cache[player] = nil
end

-- Save everyone when the server shuts down, in parallel, within the engine's 30 s window.
function PlayerData.start()
	game:BindToClose(function()
		local pending = 0
		for _, player in Players:GetPlayers() do
			pending += 1
			task.spawn(function()
				PlayerData.save(player)
				pending -= 1
			end)
		end
		local deadline = os.clock() + 25
		while pending > 0 and os.clock() < deadline do
			task.wait(0.1)
		end
	end)
end

return PlayerData
