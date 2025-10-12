"""
Scoring system to calculate the Rush Rankings.

Author: Serge Beaumont
"""

from rush.rushrankings import round_scores, multiple_round_scores
from config import OUT_DIR, ALL_BLOP_ROUNDS, ALL_ROUNDS, LAST_TEN_ROUNDS, LAST_ROUND


def single_round(round_number: int):
    round_scores(ALL_BLOP_ROUNDS[round_number], round_number, OUT_DIR, with_components=True)


def main():
    print(f"Detailed scores for round {LAST_ROUND}")
    single_round(LAST_ROUND)

    print("\nSeparate scores for last ten rounds")
    multiple_round_scores(ALL_BLOP_ROUNDS, LAST_TEN_ROUNDS, OUT_DIR)

    print("\nLifetime scores")
    multiple_round_scores(ALL_BLOP_ROUNDS, ALL_ROUNDS, OUT_DIR)


if __name__ == '__main__':
    main()
