# Starter game: "Pop"

`rbxgame new` gives you a finished, playable round-based game around a placeholder verb. Edit it into
your game; do not start from empty files. It exists to be replaced piece by piece, never all at once,
and it must stay playable after every step.

## What it does now

A ring of orbs faces a fixed camera. Hold (mouse, touch, Space, gamepad A) to charge a meter that swings
up and back down; release it inside the gold-and-teal zone. PERFECT or GOOD scores with a combo
multiplier, a MISS costs one of three lives. The round ends on the 45 s timer or at zero lives, then a
results screen (1-3 stars, score, personal best, Play again, Menu). Best score is saved.

Flow: `Title -> Play -> Results -> Play | Title`, owned by the server (`src/server/Game.luau`).
The client sends intents (`Start`, `Act`, `Menu`) on one RemoteEvent; the server validates each against the
phase, rate-limits, computes the outcome and publishes it as player attributes plus one `Event` for popups.

## Replace these three first

1. **The verb and its judgement.** `src/client/Input.luau` (what a press and a release do),
   `src/shared/Rules.luau` (`judge`, the meter, the zone) and the Act handler in `src/server/Game.luau`.
   Keep the rule: the client reports what the player did, the server decides what it was worth.
2. **The arena.** `src/server/Arena.luau` (built from `src/shared/Build.luau`), the camera pose and
   hit reactions in `src/client/Effects.luau`, the lighting look at the top of Effects.
3. **The palette and numbers.** `src/shared/Config.luau`: colours, round length, lives, timing, score,
   star thresholds. Also the UiKit theme and the sounds table in `src/client/Audio.luau`.

## Keep

- **`src/shared/Net.luau`**: the one contract (intents, `Phase`, the attribute names). Rename and add to it;
  do not scatter remote or attribute names through other files.
- **The state machine** in `Game.luau` (phase checks, rate limit, malformed-payload checks, one timer loop,
  cleanup on leave).
- **`src/server/PlayerData.luau`**: retries, cache, save on leave and shutdown, safe in-memory fallback.
  Add your fields to `DEFAULTS`; set `STORE_NAME`.
- **`BotHook` in `Input.luau`** (`busy`, `act`, `state`) and the scenarios: `scenarios/smoke.luau`
  (server rules), `scenarios/human-bot.luau` (precise and human-error bots), `scenarios/play-tour.txt`,
  `scenarios/ui-tour.txt`. Update their GAME-SPECIFIC parts when the verb changes.
- `tests/rules.luau`: change it with `Rules.luau`; it also simulates a precise and a shaky player to
  check the star thresholds.

## Order

1. Run it as is (`rbxgame check`, `rbxgame open`, press Play) so you know the baseline.
2. Write `CONCEPT.md`: the verb, what the player judges, the failure, the mastery.
3. Replace the verb: `Input` + `Rules` + the Act handler, with a failing `tests/rules.luau` first. Keep
   `Invoke("act")` working and run `scenarios/smoke.luau` and the precise bot after the change.
4. Replace the arena and palette; run the play tour and the UI tour (desktop and phone) and look.
5. Retune numbers until the human bots show a gentle curve (`references/mechanics-and-fun.md`).
6. Only then add what the starter lacks: tutorial, progression, shop (`references/monetization.md`), more screens.

Known limits: the release amount is client-reported (the zone is public), bounded by the server's charge-time
check; `Plays` merges by max across overlapping sessions; a round-end save happens at most every 30 s per
player; in Studio the data is in memory only, so a playtest never touches a real save.

Not in the starter on purpose: session locking across servers (`references/data.md`), a tutorial,
settings, a pause menu, any monetization.
