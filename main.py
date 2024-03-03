"""
Scoring system to calculate the Rush Rankings.

Author: Serge Beaumont
"""

from rush.rushrankings import round_scores, multiple_round_scores
from config import OUT_DIR, ALL_BLOP_ROUNDS, ALL_ROUNDS, LAST_TEN_ROUNDS


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
    main(LAST_TEN_ROUNDS)
    # single_round(54)
