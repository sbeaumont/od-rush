from rush.rushrankings import load_scoring_ratios, round_scores, multiple_round_scores

ROUND_NUMBER = 51
ALL_BLOP_ROUNDS = (51, 49, 48, 47, 45, 44, 42, 41, 39, 38, 36, 35, 33, 30, 28, 26)
LAST_FIVE_ROUNDS = ALL_BLOP_ROUNDS[:5]
LAST_TEN_ROUNDS = ALL_BLOP_ROUNDS[:10]
BETA_ROUNDS = (24, 22, 20, 19)

OUT_DIR = 'out'

v1_ratios = load_scoring_ratios('rush/rush_rankings_v1.json')
v2_ratios = load_scoring_ratios('rush/rush_rankings_v2.json')
rounds_to_calculate = LAST_TEN_ROUNDS

print("Detailed scores for current round")
round_scores(v2_ratios, ROUND_NUMBER, OUT_DIR, with_components=True)

print("Separate scores for multiple blop rounds")
multiple_round_scores(v1_ratios, rounds_to_calculate, OUT_DIR)
