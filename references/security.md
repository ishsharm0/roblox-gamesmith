# Security: assume every client is hostile

Exploit tools let a player run arbitrary Luau in their own client: fire any remote with any arguments,
read anything replicated to them, move their character anywhere, and delete or change their local
copies of parts and GUIs. They cannot touch the server's memory, `ServerStorage`,
`ServerScriptService`, or another player's client. Design so that the worst a client can do is lie
about itself, and the server notices.

## The remote handler pattern

```lua
local Rate = {} -- [player] = { [action] = lastTime }

local function allowed(player: Player, action: string, perSecond: number): boolean
	local now = os.clock()
	local t = Rate[player] or {}
	Rate[player] = t
	if t[action] and now - t[action] < 1 / perSecond then
		return false
	end
	t[action] = now
	return true
end

Action.OnServerEvent:Connect(function(player, kind, arg)
	if typeof(kind) ~= "string" then return end                 -- type
	if kind == "Buy" then
		if typeof(arg) ~= "string" or #arg > 32 then return end -- type + range
		local item = Shop.items[arg]
		if not item then return end                             -- exists
		if not allowed(player, "Buy", 4) then return end         -- rate
		Shop.buy(player, item)                                   -- the server reads the price itself
	end
end)
Players.PlayerRemoving:Connect(function(p) Rate[p] = nil end)
```

Checklist for every argument:
- **Type**: `typeof` (not `type`, which says "userdata" for Roblox types). Numbers: also finite
  (`x == x`, not `math.huge`). Strings: length cap.
- **Range**: clamp or reject. Indexes are integers in range (`math.floor(x) == x`).
- **Ownership**: an instance argument belongs to this player (is in their plot, their inventory, their
  character) and still exists (`inst:IsDescendantOf(workspace)`).
- **State**: the action is legal now (right phase, not dead, not mid-round, cooldown elapsed, close
  enough: `(root.Position - target.Position).Magnitude < 12`).
- **Rate**: per player per action. Drop silently; log repeated abuse.

## What the server must compute itself

- Prices, rewards, damage, cooldowns, drop tables: from server config, never from the payload.
- Positions for rewards: read the character's root on the server; check distance and line of sight
  for interactions.
- Time: server clocks only. A client "I finished in 12 s" is ignored; the server timed the run.
- Randomness: server-side `Random.new()`. Client-visible seeds let exploiters predict loot.

## Movement and physics

The client owns its character's physics, so speed, fly and teleport hacks move the character for real.

- Check progress, not inputs: checkpoints must be reached in order (`Rules.checkpoint` style), each
  pad landed in sequence, with a plausible time between them.
- A speed check: distance between server samples / elapsed vs the maximum the verb allows, plus slack
  for lag. On violation: rubber-band to the last valid position; repeated violations: kick and log.
- Never trust `Humanoid.WalkSpeed` read on the server as proof; the client can move without it.
- Touched events fire on the server for client-moved characters, and exploiters can fire them from
  far away by moving parts locally: verify distance in the handler.

## Data and economy

- Currency changes go through one server module with a reason string (`Economy.add(player, 50,
  "quest:3")`); log large or unusual grants.
- Saved data is validated on load (types, ranges, schema version); a corrupted field resets to a
  default rather than crashing the session.
- Developer product grants are idempotent by `PurchaseId` (see `receipts.md`).
- Trading: both sides confirm on the server with a snapshot of both inventories; the trade applies
  atomically or not at all. Lock both profiles during the swap.

## Things that leak

- Anything in `ReplicatedStorage`, `ReplicatedFirst`, `Workspace`, `StarterGui`, `StarterPack` and
  `StarterPlayer` is downloadable. Admin lists, unreleased content, answer keys and server config go
  in `ServerStorage` / `ServerScriptService`.
- `LocalScript` source is readable; never put secrets (API keys, webhook URLs) in client code. Use
  `HttpService` from the server only, with keys in Secrets (`HttpService:GetSecret`).
- `RemoteFunction` server -> client can hang the server thread forever. Don't.

## Free models and plugins

Free models are the most common backdoor. Before keeping any inserted asset:
1. List every script inside it (`Script`, `LocalScript`, `ModuleScript`, including ones parented to
   odd places or disabled).
2. Delete scripts you didn't read. Search the rest for `require(` with a number, `getfenv`,
   `setfenv`, `loadstring`, `HttpService`, `TeleportService`, `MarketplaceService`, long encoded
   strings, and `string.char` chains.
3. Check for scripts created at runtime (`Instance.new("Script")`) and for `InsertService` use.
4. Prefer mesh-only assets; rebuild behaviour yourself.

`studio luau` can do the search over a whole place in one call; do it after every insert.

## Moderation and safety rules that are also security

- Player-entered text shown to others goes through `TextService:FilterStringAsync` (and
  `TextChatService` for chat). Unfiltered display gets games taken down.
- No off-platform links, no personal information collection, age-appropriate content.
- Paid random items (loot boxes) must show odds and are restricted in some regions; check current
  Roblox policy before shipping any.

## Audit pass

`workflows/audits.md` has the security checklist; run it before every publish and after adding any
remote or any inserted asset.
