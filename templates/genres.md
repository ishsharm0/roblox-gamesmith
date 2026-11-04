# Genre playbooks

What players expect from each popular Roblox genre, the systems to build in order, and where each
genre usually goes wrong. Adapt; don't paste. Research the current top games first (`references/research.md`):
conventions shift.

Every genre still needs a core verb with a judgement in it, a designed difficulty curve, stakes and a
score (`references/mechanics-and-fun.md`). The genre sets the frame around that.

---

## Obby / platformer

**Loop:** run and jump through stages -> checkpoint -> harder stage -> finish -> beat your time.

**Build in order:** checkpoints and respawn -> 10-20 stages designed as beats (introduce, test, twist,
breathe) -> stage counter and timer -> respawn feel (instant, camera reframed) -> skip-stage product
(optional) -> leaderboard -> cosmetics (trails, colours).

**Expect:** fair jumps (no pixel-perfect gaps on mobile), visible next goal, short stages, quick
respawn, a sense of height or danger.

**Goes wrong:** jumps that are all the same (the "obby for babies" failure); an invisible kill brick;
long stages without checkpoints; mobile players unable to make jumps tuned on a keyboard. Fix with a
skill element in the movement itself (charged jumps, timing hazards, momentum), a human-model bot run,
and halfway saves on long stages.

## Simulator

**Loop:** do an action (click, swing, collect) -> earn currency -> buy upgrades/pets -> earn faster ->
unlock a new area -> rebirth for a multiplier.

**Build in order:** the earn action with satisfying feedback -> currency and one upgrade shop -> areas
gated by currency -> pets/companions with boosts -> rebirth -> eggs/collection -> trading (late).

**Expect:** big numbers that keep going up, frequent unlocks (something new every few minutes), pets,
areas that look different, idle progress.

**Goes wrong:** the action is a plain click with no judgement; inflation where numbers stop meaning
anything; paywalled areas. Give the action timing or aim (crit windows, combo meters), keep a visible
next goal, and tune prices from analytics.

## Tycoon

**Loop:** claim a plot -> buy droppers/machines -> income flows -> buy more -> the base grows ->
rebirth.

**Build in order:** plot claiming and ownership -> one income machine with a visible conveyor -> a
button-pad purchase path that builds the base piece by piece -> income display -> upgrades and
branching paths -> decoration and showing off -> rebirth.

**Expect:** the base visibly growing, satisfying build-in animations, a clear next purchase, other
players' bases to compare with.

**Goes wrong:** long waits with nothing to do (add active income: mini-games, collection runs); plot
ownership bugs (server must own plot state); exploitable buttons (validate ownership and distance).

## RPG / adventure

**Loop:** quest -> fight/explore -> loot and XP -> level and gear up -> harder zone -> boss.

**Build in order:** movement and combat feel (`references/systems-combat.md`) -> one zone with enemies and
a quest -> XP and levels -> inventory and gear (`references/systems-inventory.md`) -> boss -> second zone ->
parties and trading.

**Expect:** a world worth exploring, readable combat, gear that changes how you play, bosses with
patterns, playing with friends.

**Goes wrong:** scope (build one great zone first); combat that's stat-checking, not skill; quest text
nobody reads (show, don't tell).

## Horror

**Loop:** explore a space -> find items/solve puzzles -> evade a threat -> escape; often in a group.

**Build in order:** one dark, readable level with lighting and sound -> the threat with clear rules
(sight, sound, patrol) -> objectives -> chase sequences -> group roles and revives -> more levels.

**Expect:** tension through sound and light, a threat with learnable rules, jump scares earned by
buildup, playing with friends (screaming together is the point).

**Goes wrong:** too dark to see on phones (tune brightness on a phone, use light pools); a threat
that's unfair (always telegraph); too gory for the maturity rating.

## Battle royale / arena

**Loop:** drop in -> loot -> fight -> survive the shrinking zone -> last one standing -> queue again.

**Build in order:** combat with good feel -> one arena -> round flow (lobby, countdown, play, results)
-> loot spawns -> shrinking zone -> spectate -> matchmaking and reserved servers.

**Expect:** quick rounds (5-10 min), fair spawns, readable combat, rewards for a good finish even when
you don't win.

**Goes wrong:** not enough players per server early (support small lobbies and bots); exploits (server
hit detection, `references/security.md`); long downtime between rounds.

---

## Systems shared by every genre

- Session flow: title -> (tutorial) -> play -> results -> again (`references/player-journey.md`).
- Saving progress (`references/data.md`), settings (sound, reduced motion), and a best/high score.
- UI built from the kit (`references/ui-ux-style.md`), tested on a phone.
- Audio for every key event (`references/audio.md`).
- Analytics funnel for the first session (`references/retention-liveops.md`).
