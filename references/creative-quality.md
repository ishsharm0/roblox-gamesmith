# Original concepts and player pacing

## Ideas players click (read before CONCEPT.md)

A concept is **fantasy + verb + twist**, and it fits in a title a 12-year-old would click and explain
to a friend in one sentence. "Obby with lily pads" is a theme. "The pads sink, and you only get one
jump" is a game.

- **Write ten titles before choosing.** Each one is a premise in five words ("Throw Food For Animals",
  "Survive Your Ideas", "+1 Spider Arm", "Do Not Stop."). Pick the one whose first 30 seconds you can
  describe as an action, not a menu.
- **What breaks out now** (top-trending chart, 2026-11-09; recheck with `rbx-research charts --sort
  top-trending`): most new games are 2-7 weeks old, have 10k+ CCU and a 90%+ like ratio. They are
  physics/ragdoll sandboxes (ragdoll physics, throwing things), absurd one-line premises, "+1 X every
  second" incrementals with a visible body change, and survival/escape with a stated rule. They are
  rarely a generic obby or tycoon. Read the format of the moment, then add the twist only you have.
- **The verb must be funny or tense on its own.** Watch a 10-second clip of only the core action with
  no UI. If it isn't fun to watch, no progression system will save it.
- **Visible escalation.** The player's power should show on screen: bigger, more, faster, sillier.
  Numbers going up in a corner is not escalation.
- **Social by default.** Other players are visible and can affect each other, and the funniest moment
  is something you would clip.

Boring detector (fail and rethink if any are true): the title names a genre instead of a premise; the
first 30 seconds are walking or reading; the core action is "touch part, get number"; the world is
generic grass, blocks and a spawn pad; nothing on screen changes as the player gets better.


## Research for insight

Use it with game-design, mechanics-and-fun and player-journey. Compare three different loops before
committing, and for each write what the player does, judges, learns and changes in the world. A twist
changes decisions or how players affect each other; a new theme on an old obby is not a twist.

Sample the genre's top games, one small odd one, and one adjacent genre or real activity. Play or
watch the first minute and a late session of each. Charts tell you what gets clicked, not why it
keeps players, so write what you saw separately from what you guess. Take principles, never another
creator's art, names, levels or code.

Write the concept test in CONCEPT.md: what is fun in the first minute, which decision changes on a
repeat, what a new player will misunderstand, and what result would make you change the concept.

## Pacing

Map the session: arrival → a goal you can see → the first action → feedback → a choice → an earned
payoff → recovery → the next thing. The defaults:

- The first action within 10 seconds of spawning and the first payoff within 30.
- Beats alternate introduce, test, twist, breathe. One new variable at a time.
- A failure costs under 10 seconds and shows why it happened. A spike of failures on an easy beat is
  a camera, collision or respawn bug until proven otherwise.
- A round has an end: a results moment with a score to beat and one button to go again.
- No fake timers, no streaks that punish a day off, no paying to skip frustration you built.

A sandbox or social game replaces the round with goals the player sets; say so in CONCEPT.md and
give it visible escalation instead.

Bots prove the game can be finished and show the difficulty curve. They cannot tell you it is fun.
Play it with real input on desktop and a phone layout and note where you hesitated, got bored or
wanted another go. Report what you saw and what is untested.

## Art direction and feedback

Pick a shape language, a palette, a lighting mood and landmarks from the game's fantasy, and make the
UI part of that world. Feedback scales with meaning: a small answer for routine input, the full
stack for the rare payoff. Particles, shake and popups on everything flatten the payoff and hide the
play.

Before expanding, capture arrival, the hero moment at player height, the first payoff, a failure and
recovery, and a phone view. Put them beside the references. If they don't show the same world and
action, fix the composition (repetition, random props, empty ground), not the effects. Use
geometry-quality.md for every important model.

Review the largest weakness first and fix by layer. A bot visiting every platform is not a finished
game.
