from rush.rankingscraper import load_stats
from config import ALL_ROUNDS, OUT_DIR, CACHE_DIR
from pprint import pprint
import os
import pickle
from collections import defaultdict

from rush.rushrankings import all_player_names


def load_round_stats(round_number: int) -> dict | None:
    cache_file_name = f'{CACHE_DIR}/round_{round_number}_all.pickle'

    if os.path.exists(cache_file_name):
        print('Loading cached file', cache_file_name)
        with open(cache_file_name, 'rb') as f:
            stats = pickle.load(f)
    else:
        stats = load_stats(round_number, use_cache=False)
        with open(cache_file_name, 'wb') as f:
            pickle.dump(stats, f)

    return stats

def dave_score_for_player(stats: dict, name: str) -> float:
    score = 0
    scoring_rankings = ['The Largest Dominions', 'Most Prestigious Dominions', 'Most Masterful Spies', 'Most Masterful Wizards']
    for ranking in scoring_rankings:
        if name in stats[ranking]:
            score += stats[ranking][name].score
    return score

def dave_scores_for_round(stats: dict) -> list[list]:
    dave_scores = {name: dave_score_for_player(stats, name) for name in all_player_names(stats)}
    dave_scored_filtered = {name: score for name, score in dave_scores.items() if score > 0}
    result = list()
    for name, score in sorted(dave_scored_filtered.items(), key=lambda item: item[1], reverse=True):
        result.append([name, score])
    return result

if __name__ == '__main__':
    all_round_scores = list()
    for round in ALL_ROUNDS:
        stats = load_round_stats(round)
        with open(f'{OUT_DIR}/dave_scores_round_{round}.txt', 'w') as f:
            dave_scores_round = dave_scores_for_round(stats)
            all_round_scores.append(dave_scores_round)
            f.writelines([f'{name}, {score}\n' for name, score in dave_scores_round])

    total_score = defaultdict(int)
    for stats in all_round_scores:
        for name, score in stats:
            total_score[name] += score

    with open(f'{OUT_DIR}/dave_scores_all_rounds.txt', 'w') as f:
        for name, score in sorted(total_score.items(), key=lambda item: item[1], reverse=True):
            f.write(name + ', ' + str(score) + '\n')
