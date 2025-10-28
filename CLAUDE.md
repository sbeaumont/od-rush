# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Rush Rankings calculator for the OpenDominion game. It calculates specialized rankings for "blackops" players (bloppers) who focus on support roles rather than realm growth. The system scrapes Valhalla pages from opendominion.net and computes scores based on various performance metrics.

## Core Architecture

The ranking system operates in three stages:

1. **Scraping** (`rush/rankingscraper.py`)
   - Fetches ranking data from OpenDominion's Valhalla pages
   - Parses HTML tables using BeautifulSoup
   - Caches raw data as pickle files in `cache/` directory
   - Returns `dict[stat_name: dict[player_name: Ranking]]` structure

2. **Score Calculation** (`rush/rushrankings.py`)
   - Applies feature scaling to normalize scores (0-1 range)
   - Supports multiple scaling methods: linear, log, power, logpower
   - Calculates weighted category scores (Mastery, Ops, Theft, Blackops, War, Assassination, Fireball)
   - Applies land-size penalties to prevent tiny dominions from gaming rankings
   - Aggregates scores across single or multiple rounds

3. **Output Generation**
   - Single round: CSV with category breakdown
   - Multiple rounds: CSV with per-round scores, totals, and averages
   - Title holders: Lists top performers in each category

### Key Components

**Scoring Versions** (`rush/rush_rankings_v*.json`)
- JSON files define weighted scoring formulas
- Each category has: rankings list, calculation method, weight, penalty settings, scaling style
- Calculation methods: "average" or "average of best N"
- Version assignment per round in `config.py::ALL_BLOP_ROUNDS`

**Feature Scaling** (`rankingscraper.py::feature_scaled_scores`)
- Normalizes raw scores to 0-1 for fair comparison
- Methods: linear (default), log (compress outliers), power (penalize low scores), logpower (combined)
- Applied per stat category based on scoring version configuration

**Land Penalties** (`rushrankings.py::apply_low_land_penalty`)
- Gradual penalty for small dominions using concave curve (square root)
- Configured per category with `small_land_max_penalty` and optional `small_land_penalty_threshold`
- No penalty at/above threshold; scales to max penalty at minimum land size

**Round ID Mapping**
- Technical round IDs (26-69) map to display numbers (Round 20-46)
- `config.round_number_of_round_id()` converts technical ID to display number
- `ALL_BLOP_ROUNDS` dict maps round IDs to scoring versions

**Caching System**
- Pickle files: `cache/round_{id}.pickle` (filtered stats) and `cache/round_{id}_all.pickle` (all stats)
- Bypass with `use_cache=False` in `load_stats()`
- Cache includes raw scores; feature scaling applied after loading

## Common Commands

```bash
# Run main rankings calculation (single round + last 10 + lifetime)
python main.py

# Calculate title holders for the last round
python title-holders.py

# Generate Top 100 wiki page for latest round
python tophundred.py

# Calculate "Dave scores" (land + mastery) for all rounds
python rush/daverankings.py

# Install dependencies
pip install -r requirements.txt
```

## Data Flow Example

```
1. load_stats(67) → scrapes opendominion.net/valhalla/round/67
2. Returns: {'Most Masterful Spies': {'AgFx': Ranking(rank=1, score=5000, fs_score=1.0)}}
3. score_categories(v5_ratios, stats, 'AgFx') → calculates weighted scores per category
4. calculate_player_score() → sums categories into total score
5. Output: "AgFx, 7500, 123.456, 15.2, 18.5, ..." (name, land, total, categories...)
```

## Development Notes

- Round numbers in code are technical IDs (e.g., 67 = Round 45). Use `config.round_number_of_round_id()` to convert
- The `NOBODY_PLAYER` constant handles empty ranking categories (rare in test rounds)
- Player names with commas are sanitized with underscores for CSV compatibility
- Output files follow naming convention: `Top (Black) Oppers Round {number}.txt` or with ` (Cats)` suffix for category breakdown
- The `rush` package contains core logic; root-level scripts are entry points
- v6 ratios introduced log scaling and land penalties with 5000 threshold