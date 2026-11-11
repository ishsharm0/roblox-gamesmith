# Mechanics and fun: a game is a skill to get better at

Read this before CONCEPT.md is final and again before the first playtest. Pretty screens on top of a
trivial verb are still a trivial game.

## The checklist, for any genre

Whatever the game is (aiming, building, racing, collecting, fighting, managing), it is not ready for an
art pass until each line has a concrete answer in CONCEPT.md:

1. **Verb:** the one thing the player does every few seconds, and what they have to *judge* to do it
   well (timing, distance, angle, order, risk). No judgement, no game.
2. **Failure:** what going wrong looks like, what it costs, and how fast the player is back in.
3. **Mastery:** what a good player does that a new one can't, and how the game shows it (score, combo,
   stars, time, a rank).
4. **One new thing at a time:** the list of ideas the game introduces, in order, each first met alone
   and safe, then combined. Fewer than four ideas is a demo.
5. **Decision:** a real choice that recurs (safe or greedy, spend or save, which target first).
6. **Feedback:** every input and every outcome answered within 100 ms by motion and sound; the best
   outcome is the loudest thing in the game.
7. **Assist that fades:** the guide a new player gets (a preview, a highlight, a slower start) and when
   it goes away.
8. **Reason to go again:** what the results screen shows that makes one more round obvious.

The rest of this file is how one game learned each line the hard way. The examples are from a jumping
game; the rules are not about jumping. `references/reference-game.md` has that game's specifics.

## What the person rejected

Lily Pad Leap v2 had a title screen, a tutorial, results and a nice UI, and the person said: "way too
easy... it's literally just a user jumping as if it was an obby for babies... needs more mechanics and
actual fun". Every pad was the same distance apart, the default Roblox walk-and-jump did all the work,
nothing could go wrong except walking off the edge, nothing was scored, and the only thing that changed
between stages was a smaller pad. There was no decision to make and no way to be good at it.

v3 fixed it, and every fix generalises:
- **A core verb with skill in it.** Hold to charge, release to leap. The meter swings up and back
  down, so timing the release is the skill. Distance is the decision: every gap is different.
- **A reason to be precise.** Landing near the centre is PERFECT and builds a combo multiplier; a
  sloppy landing resets it. The same course is easy to finish and hard to master.
- **Stakes.** Three hearts. A splash costs a heart and the combo; losing all three costs time. Each
  checkpoint gives a heart back, which is a breather.
- **Variety introduced one at a time.** Garden 1 teaches distance. Garden 2 adds bounce blossoms (a
  thrill) and drifting pads (timing). Garden 3 adds turtles that dive and koi that leap across the
  path. Garden 4 mixes everything on small, fast-sinking pads.
- **Assists that fade.** The landing preview shows the full arc and a landing ring, then the arc
  only, then half an arc, then nothing. The player's own judgement takes over as they improve.
- **Juice on every outcome.** PERFECT! with rising pitch per combo step, sparkles, a score punch, a
  splash and heart loss, a stage banner, stars landing one by one at the end.

## Design the core verb first

Write it in CONCEPT.md as: input → what the player judges → what happens → how it can go wrong → what
mastery looks like. If "what the player judges" is empty, the verb has no skill.

| Skill type | Examples | Roblox-friendly form |
|---|---|---|
| Timing | charge-and-release, rhythm, dodging on a beat | hold a button; a meter that swings |
| Distance / aim | how far, which direction | camera aim with assist toward the intended target |
| Route choice | safe path vs fast path, detours for collectibles | branches, collectibles high on the arc |
| Reading hazards | when it's safe to go | telegraphed cycles (shake, ripple, glow) before danger |
| Resource | spend now or save | hearts, boosts, a multiplier you can cash in |

Give the player a choice every few seconds, a reason to replay (score, stars, best time) and a way to
show off (combo, PERFECT streaks, leaderboard). Keep the input simple (one button plus the camera works
on phones); put the depth in the judgement, not the controls.

## The difficulty curve is a table you design

Lay the course out as data (`Config.Stages[i].beats` in the test game: gap, kind, side offset), never as
"N pads spaced evenly". For each stage:
1. **Introduce** the new element once, somewhere safe (a lotus or solid ground right after it).
2. **Test** it twice with different numbers (a short gap, then a long one).
3. **Twist** it (the same element combined with an older one).
4. **Breathe**: a checkpoint, a heart back, a stage banner.
Raise difficulty by mixing elements, shrinking margins and removing assists, not only by shrinking
platforms. Vary the rhythm: a long gap after two short ones, a drift pad after a still one.

## Fairness rules (each one was a real bug in the test game)

- **Never chain two timed hazards without somewhere safe to wait.** A pad that sinks in 1.3 s right
  before a turtle that is underwater for 2.4 s means a guaranteed splash. Fix: the pad before a timed
  element holds longer, or the player can wait on solid ground.
- **A failure must not cause the next failure.** After a splash the player respawned beside pads that
  were still sunk, and splashed again. Fix: respawning restores that stage's hazards, cancelling any
  tween still running on them.
- **Input during automatic movement is ignored.** A leap pressed just as a bounce pad fired its own
  launch sent the player into the water. Lock input while the game moves the player, and buffer
  presses made a moment early (see "Feel").
- **If the game steers, it must steer to where the target will be.** Aim assist picked the direction
  but aimed at a drifting pad's position at take-off. The pad slid up to 3.2 studs during the leap,
  nearly a whole radius, so landing was luck. That beat failed 60% of the time for a casual player.
  Leading the target by its sampled velocity × flight time brought it to 31%. Any judgement the player
  can't make (here, sideways aim) must not decide the outcome.
- **Bound the retry length.** If failing sends you back to the stage start, a stage of n beats at
  success p takes about 1/pⁿ tries. Ten beats at 80% is about 9, and casual runs looped 20 to 30 times
  in the last garden. Give long late stages a halfway save that is visible in the world (the test
  game's lotus bud: `bud = n` in a stage's config, the pad never sinks, a splash respawns there).
- **Telegraph every danger.** Turtles shake before they dive; koi throw spray before they leap.
- **The camera serves the next decision.** On a spiral route the camera faced the old direction and
  leaps went sideways. After each landing the camera turns to frame the next target, and after every
  teleport too (respawn, restart), so the player's first look after a respawn is at the next decision.

## Feel (the part a bot can't tell you)

- **Input buffer.** A press within about 0.35 s before landing starts the action on touchdown.
- **Coyote time / grounded check.** A landing bounce briefly reads as "airborne"; use a short ray
  down instead of only `Humanoid.FloorMaterial`.
- **Stick the landing.** Zero horizontal velocity on touchdown; play a squash; land the camera.
- **Clean ballistic arcs.** A humanoid brakes in the air. For a leap, put it in
  `HumanoidStateType.Physics` with an `AlignOrientation` holding it upright, set the velocity for the
  arc, and end the flight with a lookahead ray against the landable parts only (pads' collision discs,
  never scenery under the arc, which otherwise "lands" you in mid-air).
- **Reward sound climbs.** Pitch rises with the combo; the miss sound is short and soft, not punishing.

## Scoring and stars

**Calibrate stars from bots, never from guesses.** Run the precise bot and the casual bot several times,
then set the thresholds so a casual player earns 1 to 2 stars and a precise one 2 to 3. Cap every
multiplier (combo, chain) and show the capped value: a "CHAIN x39" label on a x3 cap reads as a bug.

Score the things that take skill (precision, streaks, risk, speed) and show it live. Stars: one for
finishing, one for thoroughness (every collectible), one for mastery (a score or time a good player
reaches on a good run). Calibrate with a bot: a perfect bot scored about 28k on the test course, so the
mastery star went to 15k, not the 9k first guessed.

## Prove it with bots, then judge it as a person

Give the client a test hook that drives the real controls: a `BotHook` BindableFunction under the
player, where `Invoke("act", amount)` performs the core verb through the same code a key press uses and
`Invoke("busy")` says whether the player can act yet. Then write a bot that plays the whole course
with perfect inputs (the template's `scenarios/human-bot.luau` with `BotProfile = "precise"`). Run
it several times and read:
- **Completable?** Every run reaches the results screen.
- **Where does it fail?** Splashes per stage are the difficulty curve; a cluster in one place is either
  a fairness bug or a spike to smooth. Each cluster in the test game was a bug from the list above.
- **How long?** About a minute for a precise bot here; humans take two to three.

The hook is the same in every genre; only what `act` means changes:

| Genre | `act(amount)` means | `busy` is true while | The precise bot computes | What to read from runs |
|---|---|---|---|---|
| Charge and release (jump, throw, golf, cannon) | release at this charge 0..1 | in flight, animating | the charge for the target distance from the game's own ballistics | misses per level, shots used, stars |
| Aim and shoot | fire at an aim point (pass a second argument or set an attribute for the target) | reloading, projectile live | the target's position plus lead | accuracy, time to clear, damage taken |
| Collect and upgrade (simulator, tycoon) | do the next purchase or collection the hook reports as best | walking, on cooldown | the cheapest upgrade with the best return | currency per minute over time: it must rise, with no dead minutes |
| Racing and movement | steer toward the next gate with this throttle | never | the racing line through gate centres | lap times, wall hits, where it slows |
| Wave survival, combat | attack the nearest threat or retreat if health is low | attack recovering | the kill order by danger | wave reached, deaths per wave |
| Puzzle, placement | place this piece at the hook's suggested cell | piece settling | the solver's move | levels solved, moves over par |

Give the hook a third call, `Invoke("state")`, returning a small table (level, score, lives, what is
next) so the bot and the tours can report progress without reaching into game internals.

### Then a bot that misses like a person (required)

A precise bot finishes, so it hides two things: how hard the game is for a human, and every code path
that only runs after a mistake (respawn, heart loss, retrying a section). Write a second bot that adds a
person's errors and plays several full runs (`templates/project/scenarios/human-bot.luau` is the harness; every new project gets it):
- **Judgement:** misread the target by a normal error that is a fraction of the distance and grows as
  guides fade. Starting points: careful 1.5% to 8%, casual 3% to 13%, new 5% to 18%, from the full guide
  to no guide.
- **Timing:** release a timed input with a normal error. Careful is 35 ms, casual 60 ms and new 90 ms.
  Convert it through the meter's speed (charge error = seconds / ChargeTime).
- **Reaction:** wait 0.25 to 0.55 s after a hazard clears before acting, so late actions meet the next
  hazard the way a person's do.
- **Report:** splashes per stage, plus a histogram of where they happen ("stage.pad>kind distance"),
  over at least 4 runs with a fixed seed so before and after compare fairly.

Read it this way:
- **Spread out with a gentle rise:** that's a curve.
- **One stage far above the others:** a wall to smooth. Remember that a reset-to-checkpoint rule
  compounds, so a stage of n beats at success rate p costs about 1/pⁿ tries.
- **One spot far above its neighbours:** usually a bug, not difficulty.

Before blaming the game for a hot spot, run a zero-error probe on that one beat
(respawn, then act with the exact input, 20 times at
several delays). In the test game, the first leap of garden 4 failed 36% of the time, a 14-stud hop
that should almost never fail. The probe never missed, so the bug was in the bot: it read the distance
from the water before the respawn finished, then leapt with that stale charge. Make the bot wait for
the outcome itself (a splash, or the next pad counted, then the respawn settled), never a fixed delay.
Also rank spots by failures ÷ attempts, not raw failures: the first beat of a stage is retried after
every failure later in that stage, so its raw count is always the biggest.

Bots must respect telegraphed hazards the way a person does (wait for the warning to pass), or a
precise bot's perfectly periodic retries can sync with a hazard's timer and fail the same way forever.
A run stuck at the action cap with one beat failing ~100% is that, not difficulty. Also attribute
failures that happen during automatic movement (a bounce, a conveyor) to that movement, not to the
player's next input; the template harness reports them as `<stage>.<progress> auto`.

Run it long: a full multi-run session passes the 5-minute MCP call limit. Start it in `task.spawn`,
post progress to a player attribute (`BotReport`, `BotDone`), and poll from a background shell loop.

A bot proves the course works; it does not prove the game is fun. Then play it with real input
(`user_keyboard_input` holding the key for real lengths) and capture moments: the charge, mid-air, the
landing popup. Ask: is there a decision every few seconds? Did I want another go after the results?

## Before calling the mechanics done

- [ ] The core verb has a judgement in it, written in CONCEPT.md.
- [ ] Every stage introduces, tests, twists and breathes; the beats are data.
- [ ] There are stakes (lives, combo, time) and recovery (checkpoints, heart refills).
- [ ] Score, stars and a best are tracked, saved and shown.
- [ ] Every danger is telegraphed and no two timed hazards are chained without a safe wait.
- [ ] The precise bot finishes, repeatedly.
- [ ] The human-model bot (casual profile, 4+ runs, fixed seed) finishes every run; splashes rise gently
  stage to stage with no stage far above the rest and no hot spot that a short, easy beat explains.
- [ ] Input feels right: buffered, never eaten, the camera frames the next decision.
- [ ] Animation sells the verb (`references/procedural-animation.md`).
