# Architecture: who owns what

One rule decides most structure: **the server owns every rule, reward and currency; the client asks,
predicts and animates.** Everything below follows from it.

## Folder layout (Rojo)

```
src/
  server/        -> ServerScriptService.Server   (rules, data, rewards; never replicated)
  client/        -> StarterPlayer.StarterPlayerScripts.Client   (input, camera, UI, effects)
  shared/        -> ReplicatedStorage.Shared     (config, pure rules, types, layout math)
world/           -> Workspace.Map / ServerStorage assets (.rbxm saved from Studio)
scenarios/       -> Studio playtest scripts (not in the place)
tests/           -> Lune unit tests for pure modules (not in the place)
```

- One server entry (`Main.server.luau`) and one client entry (`Main.client.luau`) that require and
  start modules in a fixed order. No scattered Scripts; boot order is then readable in one file.
- `shared/` holds pure functions (scoring, progression rules, layout) so the server can enforce them,
  the client can preview them, and Lune can test them without Studio.
- Server-only assets live in `ServerStorage`; anything in `ReplicatedStorage` or `Workspace` is
  visible to every client.

## State: one owner, published as attributes

For per-player game state (phase, stage, score, hearts), the server keeps a plain Lua table per player
and publishes the parts the UI needs as **player attributes**. The client listens with
`GetAttributeChangedSignal` and renders.

```lua
local function publish(player: Player, s)
	player:SetAttribute("Stage", s.stage)
	player:SetAttribute("Score", s.score)
	player:SetAttribute("Hearts", s.hearts)
	player:SetAttribute("Phase", s.phase) -- LAST: the client switches screens on Phase
end
```

Set the attribute that triggers a screen change last, or the client renders the new screen with old
numbers (this happened: the results screen showed a 0 time).

Use a **phase state machine** for the session flow (Lobby -> Tutorial -> Ready -> Countdown -> Run ->
Results) as a pure transition table in `shared/` with unit tests; the server applies transitions, the
client only requests them. Illegal transitions return nil and are ignored.

For shared world state (a round timer, a boss's health), use attributes on a well-known instance or
a `Folder` of `ValueBase` objects; for big or frequently changing state, send deltas over a remote.

## Remotes: a contract, not a convenience

- A small number of remotes, named by domain (`PondAction`, `PondFeedback`), created by the server at
  boot (or in the place file), never by clients.
- `RemoteEvent` for fire-and-forget. `RemoteFunction` only client -> server, and only when the answer
  is needed now; never server -> client (a client that never returns hangs the server thread).
- `UnreliableRemoteEvent` for high-rate cosmetic streams (aim direction, effects) where a lost packet
  doesn't matter.
- Payloads: an action name plus a few primitives. Never send instances the server can find itself,
  never send prices, damage, rewards or positions to be trusted.

Every server handler validates in this order: **type -> range -> ownership/state -> rate**, then acts.
See `security.md` for the helper.

Server -> client feedback (`Land`, `Splash`, `Checkpoint`) carries what the client needs to
animate: a position, a quality, a combo count. The client never decides the outcome.

## Client prediction without client authority

Movement-heavy verbs (a leap, a dash) must feel instant, so the client moves its own character
(physics ownership is the client's for its character), and the server **judges results**, not inputs:
did the root end up on the pad, in order, in a plausible time? That keeps the feel local and the
rules server-side.

- The server checks positions against the course, not against what the client claims.
- Teleports, respawns and rewards happen on the server; the client reacts to the feedback event (and
  reframes its camera: a teleport must not leave the camera facing the old way).
- Anti-speed checks compare distance moved per second against the verb's maximum plus slack, and
  rubber-band rather than kick on a first offence (lag produces false positives).

## Networking and replication budget

- Properties and attributes replicate server -> client automatically; changing them every frame on
  many instances floods the network. Move scenery on the client when it doesn't affect rules
  (swaying reeds, idle animation), and only move gameplay objects on the server.
- `CFrame` writes on anchored parts replicate at the network rate (~20-60 Hz), so clients see moving
  platforms slightly behind. Make moving targets forgiving, or lead them in client-side aim.
- `StreamingEnabled` for big maps: the client may not have a part yet. Use `WaitForChild` with a
  timeout or `ModelStreamingMode = Persistent` on models the client code must always see.
- `NetworkOwnership`: the server owns unanchored parts unless it hands them out. For physics objects a
  player pushes, set the owner to that player for smoothness and validate the outcome server-side.

## Multiplayer shape

- Per-player state in a table keyed by `Player`; created in `PlayerAdded` (and for players already in
  the game when the script starts), cleaned up in `PlayerRemoving`.
- Shared rounds: one round module owns the round state machine; players join and leave it. Never let a
  leaving player break a round (iterate over a copy when removing).
- Teams, parties and matchmaking across servers use `TeleportService` (reserved servers) and
  `MemoryStoreService` queues; keep that out of the core loop until the single-server game is fun.
- Cross-server messages (`MessagingService`) are best-effort and rate-limited: announcements, not
  state.

## When a module grows

- Over ~600 lines or mixing two jobs: split by responsibility (rules / presentation / input), not by
  size.
- Data every system needs (config, layout) lives in `shared/` as data, computed once.
- Avoid frameworks with their own lifecycle unless the team already knows them; plain modules with
  `Start()` are easier for any agent to read and change.
