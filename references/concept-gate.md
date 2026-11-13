# The concept gate: pass this before building anything

Two finished, polished games were rejected in November 2026 for the same reason: "an unoriginal idea
and just not that fun, there's not much to it." One was a single-player lily-pad runner, the other a
single-player knock-down puzzler with stars. More levels did not fix either. The idea was wrong
before the first file. This page is how to not do that again. Do it in writing in `CONCEPT.md`.

## What the charts say (checked August to November 2026; re-check with `references/research.md`)

- No single-player arcade, puzzle or runner game is in the top lists or the fastest risers. Everything
  that holds players has **other players in the same space** and **something that grows between
  sessions** (a number, a collection, a plot). Have both or pick another idea.
- The winning families: steal/defend incrementals, plant-and-wait plots, "+1" climbers with rebirth,
  co-op survival runs with a finite goal, cosy job plus anomaly horror, collection with a small skill
  beat (fishing bar), mess-making physics with no fail state, two-player asymmetric co-op.
- A median Roblox game keeps 4 to 8% of players the next day and under 1% after a week. The median
  session is 6.6 minutes; games whose sessions average 19+ minutes keep about 2.5 times as many.
  So the first session must chain three to five loops of three to five minutes.
- Reskins lose: about a hundred "Steal a ___" clones share 8% of that format's traffic. The clones that
  grew changed the **verb** (smash the egg open, run a treadmill to reach it), not the skin.
- Hits fade in weeks. Plan a small game for a two-to-four-week life and have the first event ready.

## How to find the idea

Real hits came from one of these moves. Name which one you are using.

1. **Two proven loops plus one twist** (a moving base to defend + a road-trip survival run + a Western
   setting). The twist has to show in a five-second clip.
2. **Play the twenty existing versions, build the one you wished existed** (the fishing game with a
   real skill bar, rods that differ, procedural fish). Use Studio's MCP or the charts to list them.
3. **Change the verb of a proven format**, never only the theme.
4. **The counter-game**: play the other side of a trend (hide among the things being stolen).
5. **Cosy job with a rule that mutates**: the job is a complete simple game; the rule reveal is the hook.
6. **Bring a structure from Steam, mobile or .io games** and add a Roblox layer (shared server,
   collection, trading). Take the structure only: never a name, art, text, level or sound.

Write every candidate as one line:

> **[fantasy] + [one verb with a skill beat] + [what another player can do to or with me] + [a
> collectable or number that grows]**

Write ten. Then put each through the three tests and kill at least seven:

- **Clip test.** Can the funniest five seconds be filmed with the UI off and understood by a stranger?
- **Mutation test.** Name the proven game it comes from and the one verb you changed. Cannot: it is a
  reskin. No proven game at all: it is a guess; find the comparable or drop it.
- **Stake test.** What can another player do **to** me or **with** me: steal, shove, rescue, trade,
  race side by side, call out, sabotage, build together? A leaderboard alone is no stake.

## Red flags (any one: rework the concept, do not start building)

1. The title names a genre or a skin, not a premise.
2. The only other player is a leaderboard, or each player has a private arena.
3. Nothing that grows persists between sessions.
4. A failed attempt pays nothing.
5. The first payoff takes more than 30 seconds or needs reading.
6. It needs custom characters, a hundred hand-made levels, or more than about 300 live physics parts.
7. The format already has three clones in the top lists and you are adding a theme.
8. It is a precision puzzle. Roblox players like chaos they caused, with others watching.
9. You cannot say what the player does in minute 10 that they could not do in minute 1.
10. You are deepening a rejected game by adding levels. Pivot the verb and the stake instead.

## Depth, cheapest first (pick two or three; each is a loop the player sees working by minute 5)

| System | Build cost | What it buys |
|---|---|---|
| Rebirth with a multiplier: the same stage at 2x, 4x, 8x | 1 day | Turns a 40-second action into 20 minutes. First rebirth at 3 to 5 minutes, each next about twice as long |
| Rarity-rolled collectables: 12 to 20 base meshes x tint x size x 1-in-N mutation | 2 to 3 days | Hundreds of items; show the rarest on the player or their plot |
| A plot that earns while away | 2 days | The reason to come back tomorrow, with no new content |
| Exposure to others (steal, raid, shove) with a lock or cooldown | 3 to 4 days | The stake and the clip. Small servers (6 to 10) keep rivalry personal |
| One readable hazard cycle of 30 to 60 seconds, plus a shop | 1 to 2 days | A shared ritual ("tide's out!"). One cycle beats five hazard types |
| Shop that restocks on a timer | hours | A reason to stay five more minutes |
| Pick one of three random modifiers each round | 2 days | Variety without content |
| Trading | 3 to 5 days, high exploit risk | Only after collectables exist; server-side, no duplication |

Fill empty seats with bots that play the same rules, so the stake exists with one human on the server.

## Difficulty for casual skill games (the knock-down puzzler was "too hard")

- The first five levels or rounds: about nine in ten new players succeed first try. Later ones seven
  or eight in ten. The top rating should need something clever, not a perfect twitch.
- Stack help, most valuable first: a full aim preview at the start (shorten it later); aim assist
  toward the nearest target; targets 20 to 30% bigger than they look; one extra shot after three
  failures (never taken away); feedback that teaches ("a little more power"); retry in under two seconds.
- Fail forward: every attempt pays coins in proportion to what it did, and coins buy permanent upgrades.
- Help the beginner openly and make the best outcome the loudest thing in the game: hit-pause of 50 to
  80 ms and a camera shake on the big impact, slow motion on the last target, debris that stays so the
  mess is visible, a pitch that rises with the chain.
- Tune thresholds from recorded bot and human scores, the way level designers do: it is the most
  time-consuming step and the one that decides whether the game feels fair.

## Prove it before polishing

Greybox with primitives in two days. Bots prove it can be completed; only people prove it is fun. With
five people, stop each after three minutes and note: did they restart on their own, did they call
someone over or say "watch this", can they say the goal in one sentence. Three restarts and two
"watch this" moments: go. Fewer: change the verb or the stake, or kill it. Record the result in
`CONCEPT.md`. When no people are available, say so in the handoff instead of calling the idea proven.

## What to write in CONCEPT.md

The one-line formula; the move used and the proven comparables (names, numbers, date checked); the
verb you changed; the stake; the two or three depth systems and when each first shows; the first 60
seconds second by second; minute 10; the five-second clip; the biggest build risk; the kill criteria.
