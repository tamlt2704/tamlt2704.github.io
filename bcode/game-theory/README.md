# Game Theory — Strategic Thinking in Code

A narrative-driven course on game theory implemented in Python. You're a strategy consultant at a tech company where every decision — pricing, hiring, feature launches — is a game against competitors, partners, and users. Over 15 chapters, you'll model real strategic dilemmas — one bad decision at a time.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, what games are, the cast |
| 01 | [The Prisoner's Dilemma](chapter-01-prisoners-dilemma.md) | Two devs blame each other for a bug | Dominant strategies, Nash equilibrium, payoff matrices |
| 02 | [Repeated Games](chapter-02-repeated-games.md) | The blame game happens every sprint | Tit-for-tat, cooperation, shadow of the future |
| 03 | [Mixed Strategies](chapter-03-mixed-strategies.md) | Competitor always counters our moves | Randomization, indifference principle, support |
| 04 | [Sequential Games](chapter-04-sequential-games.md) | Should we launch first or wait? | Game trees, backward induction, first-mover advantage |
| 05 | [Commitment & Credibility](chapter-05-commitment.md) | Our threats aren't working | Credible threats, burning bridges, strategic commitment |
| 06 | [Auctions](chapter-06-auctions.md) | We're overpaying for ad slots | English, Dutch, sealed-bid, Vickrey, winner's curse |
| 07 | [Mechanism Design](chapter-07-mechanism-design.md) | Engineers game the bonus system | Incentive compatibility, revelation principle |
| 08 | [Bargaining](chapter-08-bargaining.md) | Salary negotiation is leaving money on the table | Nash bargaining, ultimatum game, BATNA |
| 09 | [Signaling](chapter-09-signaling.md) | How do we prove quality without giving away secrets? | Spence signaling, pooling/separating equilibria |
| 10 | [Evolutionary Game Theory](chapter-10-evolutionary.md) | Why do toxic strategies persist in the codebase? | ESS, replicator dynamics, hawk-dove |
| 11 | [Voting & Social Choice](chapter-11-voting.md) | The team can't agree on a framework | Arrow's theorem, Condorcet, Borda count |
| 12 | [Cooperative Games](chapter-12-cooperative.md) | How do we split revenue fairly among teams? | Shapley value, core, coalitions |
| 13 | [Information Games](chapter-13-information.md) | We don't know what the competitor knows | Bayesian games, incomplete information, bluffing |
| 14 | [Network Effects & Coordination](chapter-14-networks.md) | Nobody adopts our platform first | Coordination games, tipping points, standards wars |
| 15 | [Tournament: Axelrod's Contest](chapter-15-tournament.md) | Build the best strategy and compete | Iterated PD tournament, strategy evolution |

## Prerequisites

- Python 3.10+
- `pip install numpy matplotlib nashpy`

## Philosophy

Every game is introduced because someone made a bad decision that looked rational. No equilibrium without a real strategic failure first. The naive strategy comes first. The game-theoretic insight follows.
