# RICE prioritization

RICE is a scoring framework used by product managers and product owners to compare
initiatives when capacity is limited.

## Formula

**RICE score = (Reach × Impact × Confidence) / Effort**

- **Reach:** How many users or customers are affected in a given time window
  (for example, users per quarter). Use a concrete estimate, not a vague label.
- **Impact:** How much the initiative moves the chosen outcome for each person
  reached. Common scale: 3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = minimal.
- **Confidence:** How sure you are about the reach, impact, and effort estimates
  (often as a percentage: 100%, 80%, 50%). Low confidence should pull the score down.
- **Effort:** Person-months (or person-weeks) of work from design, engineering,
  and other contributors. Put effort in the denominator so costly work ranks lower
  unless impact justifies it.

## How a Product Owner uses RICE

1. List candidate features or bets in the same backlog slice.
2. Estimate each factor with the team; write assumptions next to the numbers.
3. Sort by score and discuss outliers (high effort + high uncertainty).
4. Treat the ranking as an input to prioritization, not as an automatic decision.
   Strategy, dependencies, risk, and commitments can override a pure score.

## Common pitfalls

- Inflating Impact without evidence.
- Using Reach of "everyone" without a time box.
- Ignoring Confidence when estimates are guesses.
- Comparing items with inconsistent Effort units.
