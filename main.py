from rush.rushrankings import load_scoring_ratios, round_scores, multiple_round_scores
from config import OUT_DIR

ROUND_NUMBER = 52
ALL_BLOP_ROUNDS = (52, 51, 49, 48, 47, 45, 44, 42, 41, 39, 38, 36, 35, 33, 30, 28, 26)
LAST_FIVE_ROUNDS = ALL_BLOP_ROUNDS[:5]
LAST_TEN_ROUNDS = ALL_BLOP_ROUNDS[:10]
BETA_ROUNDS = (24, 22, 20, 19)

v1_ratios = load_scoring_ratios('rush/rush_rankings_v1.json')
v2_ratios = load_scoring_ratios('rush/rush_rankings_v2.json')
rounds_to_calculate = LAST_TEN_ROUNDS

ratio_versions_per_round = {
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

print("Detailed scores for current round")
round_scores(v2_ratios, ROUND_NUMBER, OUT_DIR, with_components=True)

print("Separate scores for multiple blop rounds")
multiple_round_scores(ratio_versions_per_round, rounds_to_calculate, OUT_DIR)

print("Lifetime scores")
multiple_round_scores(ratio_versions_per_round, ALL_BLOP_ROUNDS, OUT_DIR)
