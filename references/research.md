# Research an idea in about 15 minutes

Five rules:
1. Research the genre's top five, not the whole site. The floor (what every top game has) and the one
   thing the best does that the rest don't are the two findings that matter.
2. Players-now (CCU) and like ratio say more than visits. Visits are lifetime; a 4-year-old game with
   2B visits and 300 players is a fossil. A 15-day-old game at 30k CCU is the current wave.
3. Look at the first minute, not the tenth: frames and transcript from the opening of a gameplay video
   show the hook, the tutorial (or its absence) and the loop.
4. Read the shop: game passes and developer products, with prices, are the designers' own map of what
   players want more of.
5. Take structure, never content: no names, art, text, sounds or characters from another game.

## Commands (run in a scratch folder; files land in `.rbx-research/` and `.yt-research/`)

```bash
rbx-research sorts                              # chart ids: top-trending, top-playing-now, trending-in-<genre>
rbx-research charts --sort top-trending         # rank | CCU | like % | genre | visits | age | last update | ids
rbx-research charts --sort all --genre obby     # every chart merged, one genre
rbx-research search "pet simulator"
rbx-research game <placeId|universeId|url|"name">   # details, passes and products with prices, badges, store media + contact sheet
rbx-research compare <id> <id> <id>             # side by side: CCU, likes, visits/day, age, monetisation surface
yt-research search "roblox <game or genre> gameplay" -n 8
yt-research brief <url>                         # transcript with timestamps + a labelled frame sheet (stills only)
yt-research devlog "<topic>"                    # Roblox devlogs and Studio tutorials
devforum search "<technical question>" --solved # Developer Forum answers
devforum read <url>
```

## Reading the numbers

- **Momentum**: CCU against age. Under 60 days and over 10k CCU is a breakout; check what it shares with
  the other breakouts on the trending chart (the format of the moment: "+1 X every second", "don't
  fall", "grow a ...").
- **Quality**: like ratio. 90%+ is loved, 80-90% fine, under 75% means players feel cheated (often by
  monetisation or difficulty walls).
- **Stickiness**: favorites per 1k visits; 3+ is strong.
- **Live ops**: days since the last update. Top games update weekly; "[UPD 21]" in a title is a promise
  of more.
- **Monetisation surface**: count and median price of passes and products. Many cheap products (14-49R)
  means impulse buys inside runs; a few 99-149R passes means permanent upgrades. Note which are
  convenience and which edge into pay-to-win, and what the like ratio says about it.

## What to extract from each comparable (write it into CONCEPT.md)

| Question | Where it shows |
|---|---|
| What does the player do in the first 10 seconds? | `yt-research brief` frames 1-3, the game's first screenshot |
| What is the 30-second loop? | transcript + frames: the repeated action, its reward, the upgrade |
| What pulls a session to 20 minutes? | progression shown on screen: levels, stages, rebirths, collections |
| What brings players back tomorrow? | daily rewards, timers, limited events, friends, trading |
| What do they sell, and is it fair? | passes, products, like ratio |
| What does it look like? | contact sheet: style, palette, lighting, UI density |
| What do players complain about? | dislikes, video comments read in the browser, DevForum threads |

## The deliverable: CONCEPT.md

One page, filled from the evidence: pitch, comparables (with the numbers above), the floor, the twist,
the 30/60/300-second experience, progression, social hooks, fair monetisation, art direction with
three screenshot paths from `.rbx-research/`, and the first playable's scope. The twist must be
something a player notices in the first minute, not a system they discover after an hour.
