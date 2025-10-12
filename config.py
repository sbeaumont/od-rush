import json

OUT_DIR = './out'
CACHE_DIR = './cache'
OD_BASE = 'https://www.opendominion.net'
VALHALLA_URL = f'{OD_BASE}/valhalla/round'


def load_scoring_ratios(filename: str):
    with open(filename) as f:
        return json.load(f)


v1_ratios = load_scoring_ratios('rush/rush_rankings_v1.json')
v2_ratios = load_scoring_ratios('rush/rush_rankings_v2.json')
v3_ratios = load_scoring_ratios('rush/rush_rankings_v3.json')
v4_ratios = load_scoring_ratios('rush/rush_rankings_v4.json')
v5_ratios = load_scoring_ratios('rush/rush_rankings_v5.json')
v6_ratios = load_scoring_ratios('rush/rush_rankings_v6.json')

ALL_BLOP_ROUNDS = {
    # 69: v6_ratios, # Round 46
    # 67: v5_ratios, # Round 45
    67: v6_ratios, # Round 45
    66: v4_ratios, # Round 44
    64: v4_ratios, # Round 43
    63: v4_ratios, # Round 42
    61: v4_ratios, # Round 41
    60: v4_ratios,
    58: v4_ratios,
    56: v3_ratios,
    54: v2_ratios,
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
LAST_ROUND = ALL_ROUNDS[0]
LAST_FIVE_ROUNDS = ALL_ROUNDS[:5]
LAST_TEN_ROUNDS = ALL_ROUNDS[:10]
BETA_ROUNDS = (24, 22, 20, 19)


def round_number_of_round_id(round_id: int) -> int:
    return 20 + ALL_ROUNDS[::-1].index(round_id)


if __name__ == '__main__':
    print(round_number_of_round_id(57))