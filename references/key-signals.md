# Key signals: the framework every game is designed, built and judged against

Roblox publishes the signals its Recommended for You sort ranks games by (creator docs, Discovery,
"Key signals": `rbxdocs read discovery.md --section "Key signals"`). They measure what players do
after they find the game, and Roblox states the goal behind them: promote games with strong long-term
retention. So they are not a marketing topic to look at after launch. They are the design brief.
Every concept, slice and review in this skill is organised around moving these eight numbers.
Re-read the docs section at the start of a project: Roblox adds, removes and re-weights signals.

## The eight signals

| Tier | Signal | What it counts | Segments |
|---|---|---|---|
| Most important | **Play-through rate** | plays per impression in the Home sort | none |
| Most important | **First-play bounce rate** (negative) | first sessions that end early | under 60 s; 61-180 s |
| Most important | **Play days per user** | distinct days a user plays | day 1; days 2-7; days 8-28 |
| Most important | **Playtime per user** | time in game, capped at 60 min per user per day | day 1; days 2-7; days 8-28 |
| Important | **Intentional co-play days per user** | days a user comes back to play with friends (joins, invites, private servers) | same |
| Important | **Qualified play sessions per user** | meaningful sessions from Home, excluding misclicks and quick bounces | same |
| Important | **Spend days per user** | distinct days a user spends Robux | same |
| Important | **Robux spent per user** | average spend | same |

All are computed on users who joined organically from the Home sort. The system explores (sends a
new cohort after an update) and expands only if that cohort's numbers hold, so an update that
bounces new players costs reach.

## What each signal asks of the design

**Play-through rate: the promise.** Decided by icon, title and thumbnails, so by whether the concept
can be shown in one image. Design the icon at concept time (concept-gate.md): one character, one
verb, one emotion, readable at 150 px beside the current top games. A concept that needs a sentence
to explain has a play-through problem no polish fixes. Rules: sauce.md, visual-craft.md.

**First-play bounce: the first 60 and 180 seconds.** Two cliffs, so two budgets. By 60 s the
player has acted (first input within 3 s of load), has seen the core verb pay off, and has received
a first reward (before 30 s). By 180 s they have made a first purchase or unlock, seen the next goal
with its bar already part-filled, and met the social stake at least once. Nothing in that window is
a wall of text, a lobby walk, a wait or a menu. Rules: player-journey.md sections 2 and 3.

**Play days: a reason for tomorrow, this week, this month.** One hook per segment. Day 1 -> 2: an
unfinished goal within reach, a daily reward, something growing while away. Days 2-7: a streak, a
collection at 40-70%, the first rebirth or world. Days 8-28: rare finds, seasonal or weekly content,
standings among friends, a second layer of progression. If CONCEPT.md cannot name the hook for each
segment, the game is a one-session game. Rules: retention-liveops.md, player-journey.md section 1.

**Playtime: sessions with no dead air, up to the cap.** The cap is 60 minutes a day, so the target
is a full, dense 20-40 minute session, not an endless grind. Every 5 s+ stretch where the player
cannot act or has nothing new to see is removed (player-journey.md section 2); each session has a
start goal, a mid goal and a natural "one more" at the end. Rules: fun-and-juice.md.

**Intentional co-play: friends are a feature.** Counted when people come back to play together, so
the game must be better with a friend in ways the player notices: a party multiplier, a co-op-only
unlock, things to do to and with each other, a rare item worth showing, an invite prompt at the
moment of a win, private servers. Bots fill seats so the stake exists in a quiet server. Rules:
player-journey.md section 4.

**Qualified play sessions: worth opening again today.** Short sessions must be complete: rejoin
lands in action with progress intact in under 10 s, and a 3-minute visit still earns something that
lasts. Timed returns (a chest in 20 minutes, a rotating shop) create the second and third session.

**Spend days and Robux per user: fair things to want.** Spend follows engagement; it is never a
gate on the core loop. Show the first offer only after the first win (a starter pack by minute 5-10),
sell speed, cosmetics, convenience and more of what the player already enjoys, and give repeat
reasons to spend on different days (rotating offers, a pass). Follow Roblox's policies for young
players. Rules: monetization.md, receipts.md.

## The owner's five requirements are the levers

| Requirement (player-journey.md) | Signals it moves |
|---|---|
| Rewarding progression, always something to work toward | play days, playtime, sessions, spend days |
| No unnecessary downtime | bounce, playtime, sessions |
| Readable without a tutorial at 30 s, 5 min, 30 min | bounce (both segments), play days day 1 |
| Social: interact, compete, play with friends | co-play days, play days, playtime |
| Every important action is satisfying | bounce, playtime, play-through (it makes the thumbnail moment) |

## Before real players exist: proxy checks

No analytics are available for an unpublished game, so every review reports these instead:

- **Play-through:** the icon and one thumbnail at 150 px on a sheet with six current top games in the
  genre. A fresh model (no design docs) is asked which it would click and what each game is.
- **Bounce:** a timeline of a first session from a bot or fresh-model run: time to first input, first
  core action, first reward, first unlock, first sight of another player's effect. Targets 3 s, 10 s,
  30 s, 120 s, 180 s. Every 5 s+ dead stretch listed.
- **Play days:** the three return hooks named, built and visible in a capture (the daily reward
  screen, the collection at part-fill, the rebirth bar).
- **Playtime:** a 20-minute bot run with a log of goals reached (one every 2-3 minutes in the first
  15) and the longest gap between rewards.
- **Co-play:** interactions between players per minute in a full round, and a list of what is better
  with a friend.
- **Sessions:** rejoin-to-action time and what a 3-minute session earns.
- **Spend:** what is for sale, when the first offer appears, and that the core loop is complete
  without paying. Never tested with real Robux.

## The scorecard

Kept in CONCEPT.md, updated at every review, one line per signal:
`signal | what in this game moves it | proxy measured (value, date) | weakest point | next change`.
A review that cannot fill a line names the missing feature as the next slice. After launch the same
table takes the real numbers from Creator Hub analytics (`rbxdocs search retention --guides`,
engagement, monetization) against Roblox's benchmarks, and the weakest signal picks the next update.
