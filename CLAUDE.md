# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Rush Rankings calculator for the OpenDominion game. It calculates specialized rankings for "blackops" players (bloppers) who focus on support roles rather than realm growth. The system scrapes Valhalla pages from opendominion.net and computes scores based on various performance metrics.

## Core Architecture

The ranking system:
1. **Scrapes** ranking data from OpenDominion's Valhalla pages (`rush/rankingscraper.py`)
2. **Calculates** scores using versioned scoring ratios (v1-v5) based on round number (`rush/rushrankings.py`)
3. **Outputs** CSV-formatted ranking files to the `out/` directory

### Key Components

- **Scoring Versions**: Different scoring formulas (v1-v5 JSON files) are applied based on round number, defined in `config.py::ALL_BLOP_ROUNDS`
- **Score Components**: Each version weights categories like Mastery, Ops, Theft, Blackops, War, Assassination, and Fireball
- **Caching**: Scraped data is cached as pickle files in `cache/` to avoid repeated API calls
- **Feature Scaling**: Raw scores are normalized to 0-1 range for fair comparison across different metrics

## Common Commands

```bash
# Run main rankings calculation (single round + last 10 + lifetime)
python main.py

# Calculate title holders for the last round
python title-holders.py

# Install dependencies
pip install -r requirements.txt
```

## Development Notes

- Round numbers in the code are technical IDs (e.g., 67 = Round 45). Use `config.round_number_of_round_id()` to convert
- The `NOBODY_PLAYER` constant handles empty ranking categories
- Cache can be bypassed with `use_cache=False` parameter in `load_stats()`
- Output files follow naming convention: `Top (Black) Oppers Round {number}.txt`