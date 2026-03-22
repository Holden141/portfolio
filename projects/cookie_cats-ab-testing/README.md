## Context
This dataset includes A/B test results of Cookie Cats to examine what happens when the first gate in the game was moved from level 30 to level 40. When a player installed the game, he or she was randomly assigned to either gate_30 or gate_40.

The data is from 90,189 players that installed the game while the AB-test was running.

**Variables:**
- `userid`: Unique player identifier
- `version`: Control (gate_30) or treatment (gate_40)
- `sum_gamerounds`: Number of game rounds played in first 14 days
- `retention_1`: Did player return after 1 day?
- `retention_7`: Did player return after 7 days?

## Analysis

| Metric | P-value | Significant? |
|--------|---------|--------------|
| Game rounds (Mann-Whitney) | 0.0502 | No |
| 1-day retention (Chi-square) | 0.0755 | No |
| 7-day retention (Chi-square) | 0.0016 | **Yes** |

## Conclusion

Moving the first gate from level 30 to 40 had no significant effect on:
- Game rounds played
- 1-day retention

However, it **significantly improved 7-day retention** (p = 0.0016). Players who reached the gate were more likely to stick with the game long-term.

The change benefits committed players without alienating casual users.

[Link to notebook](ab-test.ipynb)