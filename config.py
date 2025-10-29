import json

OUT_DIR = './out'
CACHE_DIR = './cache'
OD_BASE = 'https://www.opendominion.net'
VALHALLA_URL = f'{OD_BASE}/valhalla/round'


def load_scoring_config(filename: str):
    with open(filename) as f:
        return json.load(f)


v1_config = load_scoring_config('rush/rush_rankings_v1.json')
v2_config = load_scoring_config('rush/rush_rankings_v2.json')
v3_config = load_scoring_config('rush/rush_rankings_v3.json')
v4_config = load_scoring_config('rush/rush_rankings_v4.json')
v5_config = load_scoring_config('rush/rush_rankings_v5.json')
v6_config = load_scoring_config('rush/rush_rankings_v6.json')

ALL_BLOP_ROUNDS = {
    69: v6_config, # Round 46
    67: v5_config, # Round 45
    66: v4_config, # Round 44
    64: v4_config, # Round 43
    63: v4_config, # Round 42
    61: v4_config, # Round 41
    60: v4_config,
    58: v4_config,
    56: v3_config,
    54: v2_config,
    52: v2_config,
    51: v1_config,
    49: v1_config,
    48: v1_config,
    47: v1_config,
    45: v1_config,
    44: v1_config,
    42: v1_config,
    41: v1_config,
    39: v1_config,
    38: v1_config,
    36: v1_config,
    35: v1_config,
    33: v1_config,
    30: v1_config,
    28: v1_config,
    26: v1_config
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