# Designing for Roblox players

Roblox is a platform where a player decides in seconds, mostly on a phone, often with friends, and
usually between ages 9 and 17. A design that works elsewhere still has to survive those facts.

## What players choose on

1. **The thumbnail and title** on the home page or in search. A bright, readable image of the core
   moment (a character mid-action, a big number, a funny situation) and a title that says the verb
   ("Lily Pad Leap", not "Pondverse").
2. **The first 30 seconds.** No reading, no long cutscene, no menu maze. The player should be doing
   the core verb within 10 seconds of spawning and succeed at it within 30.
3. **Whether friends are in it.** Social games compound: friend joins, party play, visible other
   players, things to show off.

Discovery is driven by engagement: session length, return rate, and how many play-throughs lead to
friends joining. Design for those directly (`retention-liveops.md`), not for one-time spectacle.

## The loop

Every game has a loop that fits in a sentence: *do the verb -> get a reward -> spend it to do the verb
better or somewhere new*. Write it in CONCEPT.md before building.

- **Core verb** (seconds): jump, swing, collect, build, dodge. It needs a judgement in it
  (`mechanics-and-fun.md`).
- **Session loop** (minutes): a round, a run, a stage, a quest. Ends in a result screen and a choice
  to go again.
- **Long loop** (days): unlocks, collection, mastery, social status. Gives a reason to return.

If the core verb isn't fun alone, no amount of long loop will save it. Prototype it first, in
primitives, and play it.

## Genre conventions players expect

Genres on Roblox have strong conventions; break them on purpose, not by accident.
`templates/genres.md` lists the expected systems for simulators, tycoons, obbies, RPGs, horror and
battle royales. Research the current top games in the genre before deciding (`research.md`).

## Session design

- Sessions of 5-20 minutes, with natural stopping points that also invite one more go.
- Respect short attention: checkpoints, autosave, quick restarts.
- Long tasks that run while the player is away (growing plants, idle income) bring them back.
- Daily goals and streaks reward returning without punishing a missed day too hard.

## Social design

- Make other players visible and useful: co-op tasks, trading, showing off rare items, races with
  ghosts or live opponents, emotes.
- Easy party play: friends join the same server; private servers are cheap.
- Leaderboards per server (achievable) and global (aspirational).
- Moderation: filtered chat, report tools, no forced interaction with strangers.

## Accessibility and audience

- Text short and big; icons with labels; no essential information in colour alone.
- Works with touch, keyboard and gamepad; no hold-two-buttons verbs on a phone.
- Content suitable for the experience's maturity rating; follow Roblox community standards.
- Language: plain words. Many players read in a second language.

## Scope

A small game finished beats a big one half-built. The bar here is a complete small game: one verb,
3-5 stages or one strong round, a progression hook, polished feel, UI and audio, tested on a phone.
Add systems (pets, trading, guilds) only when the core loop already retains.

## Design documents

- `CONCEPT.md`: pitch, core verb and its judgement, loops, audience, art direction, comparable games
  with what you're taking and what you're changing.
- `SESSION.md`: the first session minute by minute: spawn, first action, first success, first
  failure, first reward, the moment the player understands the goal.
- Course or content tables as data in `shared/Config`, so design and code are the same thing.
