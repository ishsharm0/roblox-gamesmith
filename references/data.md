# Player data: save it once, correctly

Lost progress is the fastest way to lose a player for good. All persistence goes through **one server
module** that owns load, save, session locking and schema migration. Nothing else calls DataStores.

## Use ProfileStore (or an equivalent session-locked store)

Raw `DataStore:SetAsync` has two classic failures: two servers writing the same key (a player who
rejoins fast gets the old server's late save on top of the new one: item duplication or loss), and
saves that silently fail during an outage. ProfileStore (MadStudio, Apache-2.0) solves both with
session locks and periodic autosave. It is one ModuleScript: copy it from
github.com/MadStudioRoblox/ProfileStore into `src/server/Vendor/` (keep its licence header).

```lua
local ProfileStore = require(script.Parent.Vendor.ProfileStore)

local TEMPLATE = { version = 2, coins = 0, best = 0, stage = 1, owned = {}, settings = { music = true } }
local store = ProfileStore.New("PlayerData_v1", TEMPLATE)
local profiles: { [Player]: any } = {}

local function onAdded(player: Player)
	local profile = store:StartSessionAsync(`player_{player.UserId}`, {
		Cancel = function() return player.Parent ~= Players end,
	})
	if not profile then
		player:Kick("Your data couldn't load. Please rejoin.")
		return
	end
	profile:AddUserId(player.UserId) -- GDPR erasure requests
	profile:Reconcile()             -- fill fields added to TEMPLATE since this profile was saved
	migrate(profile.Data)
	profile.OnSessionEnd:Connect(function()
		profiles[player] = nil
		player:Kick("Your data was loaded on another server.")
	end)
	if player.Parent == Players then
		profiles[player] = profile
	else
		profile:EndSession()
	end
end

Players.PlayerRemoving:Connect(function(player)
	local profile = profiles[player]
	if profile then profile:EndSession() end
end)
```

- In Studio, use `store.Mock` (or a flag) so tests never touch live data.
- Never yield the game's boot on data: show a loading state, then start the player's session when the
  profile arrives.
- `game:BindToClose` is handled by ProfileStore; if you roll your own, end every session there.

## Schema and migration

- A `version` field in every profile. On load, run each migration step in order
  (`if data.version < 2 then ... data.version = 2 end`), then `Reconcile`.
- Rename by copying then clearing the old field in a migration, never by renaming the template key
  alone (the old data would be orphaned).
- Validate types and ranges after load: a bad field resets to its default and logs, instead of erroring
  every time that player joins.
- Keep saved data small and boring: numbers, strings, arrays and dictionaries of those. No instances,
  no `Vector3` (store `{x, y, z}`), no mixed tables, no sparse arrays.

## What to save

- Progress the player would be upset to lose: currency, unlocks, best times, settings, tutorial seen.
- Not: session-only state (current round, position) unless the genre needs resume.
- Leaderboards: an `OrderedDataStore` written on improvement only, read with `GetSortedAsync` and
  cached for a minute; never once per player per frame.

## Limits that bite

- Each key holds up to 4 MB; each request has per-minute budgets per server
  (`DataStoreService:GetRequestBudgetForRequestType`). Autosave intervals of 2-5 minutes are plenty.
- Writes to the same key are rate-limited (about one per 6 seconds). Batch changes in memory and let
  the session save them.
- DataStores need "Enable Studio Access to API Services" to run in Studio, and the place must be
  published. Without it, use the mock.

## Purchases

Developer product grants touch saved data and must be idempotent; that is a separate, careful pattern
in `receipts.md`. Game passes are checked with `UserOwnsGamePassAsync` (cache per session) and are
also granted immediately on `PromptGamePassPurchaseFinished`.

## Testing

- Pure migration functions are unit-tested in Lune (`tests/`).
- In Studio: load with the mock, mutate, end session, reopen, check the fields survived.
- Before publishing: one session with real DataStores on a private test place, rejoining twice fast.
