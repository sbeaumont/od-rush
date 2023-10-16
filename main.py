"""
Scoring system to calculate the Rush Rankings.

Author: Serge Beaumont
"""

from rush.rushrankings import load_scoring_ratios, round_scores, multiple_round_scores
from config import OUT_DIR

v1_ratios = load_scoring_ratios('rush/rush_rankings_v1.json')
v2_ratios = load_scoring_ratios('rush/rush_rankings_v2.json')

ALL_BLOP_ROUNDS = {
    52: v2_ratios,
    51: v1_ratios,
    49: v1_ratios,
    48: v1_ratios,
    47: v1_ratios,
    45: v1_ratios,
    44: v1_ratios,
    42: v1_ratios,
    41: v1_ratios,
    39: v1_ratios,
    38: v1_ratios,
    36: v1_ratios,
    35: v1_ratios,
    33: v1_ratios,
    30: v1_ratios,
    28: v1_ratios,
    26: v1_ratios
}

ALL_ROUNDS: list[int] = sorted(ALL_BLOP_ROUNDS.keys(), reverse=True)
LAST_FIVE_ROUNDS = ALL_ROUNDS[:5]
LAST_TEN_ROUNDS = ALL_ROUNDS[:10]
BETA_ROUNDS = (24, 22, 20, 19)


def single_round(round_number: int):
    print(f"Detailed scores for round {round_number}")
    round_scores(ALL_BLOP_ROUNDS[round_number], round_number, OUT_DIR, with_components=True)


def main(rounds_to_calculate: list[int]):
    single_round(rounds_to_calculate[0])

    print("Separate scores for multiple blop rounds")
    multiple_round_scores(ALL_BLOP_ROUNDS, rounds_to_calculate, OUT_DIR)

    print("Lifetime scores")
    multiple_round_scores(ALL_BLOP_ROUNDS, ALL_ROUNDS, OUT_DIR)


if __name__ == '__main__':
    # main(LAST_TEN_ROUNDS)
    single_round(53)
