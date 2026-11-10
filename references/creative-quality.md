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


Use alongside game-design, mechanics-and-fun and player-journey. Start with a player fantasy and a repeatable decision, not a trending title or a list of currencies. For new concepts, compare three materially different loops. State what the player does, judges, learns and changes in the world. A twist must change decisions or social dynamics, not just theme an existing obby.

## Research for insight

Sample successful genre games, a smaller distinctive example, and an adjacent genre or real-world activity. Search problems/fantasies, not only charts. Inspect first-time gameplay and later-session depth. Distinguish observation from hypothesis. Popularity, likes, update frequency and shop prices do not establish design quality or cause retention; don't use universal numeric thresholds as proof. Verify current facts using source evidence. Take principles, never another creator's art, names, levels or code.

Write a concept test: what should be enjoyable in one minute, what decision varies on repeat, what a new player might misunderstand, and what observation would make you revise the concept. A polished environment does not rescue a dull verb. A novelty claim needs comparison; unfamiliarity to the agent is not originality.

## Pacing by genre and session

Map arrival → understandable goal → first meaningful action → feedback → choice → earned payoff → recovery → next possibility. Test a clean first-time session and a returning-player session. Minimize avoidable waiting, but preserve exploration, suspense, downtime and anticipation where they create value. Not every game needs lives, stars, a countdown, a results screen or permanent progression.

Alternate introduce/test/twist/rest beats when appropriate. Escalate one variable at a time, make stakes understandable, and let recovery teach rather than punish. Failures should be diagnosable; unexpected failure spikes may indicate camera, collision or respawn bugs. Provide stopping points. Avoid deceptive timers, coercive streaks and pay-to-escape frustration.

Use bot scenarios for mechanical regressions and controlled difficulty samples; bots cannot establish human enjoyment. Run real controls with desktop/touch layouts, observe hesitation, route choice, time to first meaningful action, retry behavior and repeated-action fatigue. Report observed results and untested assumptions rather than predicting retention.

## Art direction and feedback

Choose an asset/shape language, palette, lighting hierarchy and focal landmarks from the game's fantasy. UI should fit that world; chunky toy UI is one treatment, not every game's default. Preserve legible interactive affordances. Scale feedback to meaning: quiet response for routine input, layered emphasis for a rare payoff. Constant particles, shake and number popups flatten emphasis and obstruct play. Reduced motion and clear sound levels are part of craft.

Before expanding, capture arrival, gameplay-height hero moment, first payoff, failure recovery and a phone view. Compare them to the intended reference: do they communicate the same world and action? Fix flat repetition and random props as design issues, not by adding effects. Use geometry-quality.md for all important generated models.

Record acceptance criteria in CONCEPT.md/SESSION.md. Review the largest weakness first, group fixes, and repeat tests when new changes justify them. A fixed round count or passing traversal bot is not an artistic quality gate.
