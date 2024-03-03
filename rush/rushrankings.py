"""
Calculator for the Rush Rankings of the OpenDominion game.

The Rush Rankings are a scoring system made for players who take on a "blackops" role,
also known as "bloppers". The regular OpenDominion game does not value this role in its
rankings since the game's primary goal is to be the largest and most powerful dominion.
These rankings honor those who do not play to be the largest, but who play to support
and raise their realm mates to the win by building and focusing on info and black ops.

This script scrapes the Valhalla pages of the OpenDominion website (opendominion.net)
and builds the scores and rankings based on the information found there.

The V1 ranking set is used until Round 35 (technical number 51),
the V2 ranking set is active from Round 36 onward.
"""

__author__ = "Serge Beaumont (AgFx)"
__credits__ = ["Rush", ]
__version__ = "1.0"

import json
from rush.rankingscraper import load_stats

MASTERY_STATS = \
    ('Most Masterful Spies', 'Most Masterful Wizards')
OPS_STATS = \
    ('Most Successful Spies', 'Most Successful Wizards')
THEFT_STATS = \
    ('Top Platinum Thieves', 'Top Food Thieves', 'Top Lumber Thieves',
     'Top Mana Thieves', 'Top Ore Thieves', 'Top Gem Thieves')
BLACKOP_STATS = \
    ('Masters of Plague', 'Masters of Swarm', 'Masters of Air',
     'Masters of Lightning', 'Masters of Water', 'Masters of Earth', 'Top Snare Setters')
ASSASSINATION_STATS = \
    ('Most Spies Executed', 'Top Saboteurs', 'Top Magical Assassins',
     'Top Military Assassins', 'Most Wizards Executed', 'Top Spy Disbanders')
FIREBALL_STAT = \
    ('Masters of Fire',)

# TOTAL_SCORE_RATIOS = {
#     'Mastery': (MASTERY_STATS, 25),
#     'Ops': (OPS_STATS, 35),
#     'Theft': (THEFT_STATS, 10),
#     'Blackops': (BLACKOP_STATS, 10),
#     'Assassination': (ASSASSINATION_STATS, 5),
#     'Fireball': (FIREBALL_STAT, 10)
# }


def is_blop_stat(stat_name: str) -> bool:
    """Used to filter the relevant rankings in the scraper."""
    blop_keywords = ['Wizard', 'Spies', 'Thieves', 'Masters', 'Saboteurs', 'Snare', 'Spy', 'Assassins', 'Bounties']
    for kw in blop_keywords:
        if kw in stat_name:
            return True
    return False


def all_player_names(stats: dict) -> set:
    players = set()
    for stat in stats.values():
        players.update(stat.keys())
    return players


def score_components(ratios: dict, stats: dict, name: str) -> dict:
    """Score a specific player on all components of the scoring system for the round."""
    result = dict()
    for component_name, score_component in ratios.items():
        total = 0
        for stat_name in score_component[0]:
            if name in stats[stat_name]:
                total += stats[stat_name][name].fs_score
        component_score = total / len(score_component[0]) * score_component[1]
        result[component_name] = component_score
    return result


def calculate_player_score(ratios: dict, stats: dict, name: str) -> float:
    """The player's total score is the sum total of all the scoring components."""
    player_score = sum([cs for cs in score_components(ratios, stats, name).values()])
    return round(player_score, 3)


def blop_scores_for_round(ratios: dict, round_number: int, with_components=False) -> list:
    """Calculate the scores for all players in a specific round."""
    stats = load_stats(round_number, is_blop_stat)
    players = all_player_names(stats)
    if with_components:
        return [(player, calculate_player_score(ratios, stats, player), score_components(ratios, stats, player)) for player in players]
    else:
        return [(player, calculate_player_score(ratios, stats, player)) for player in players]


def round_scores(ratios: dict, round_number: int, out_dir: str, with_components=False):
    """Output the round scores in a CSV format that can be imported into a spreadsheet."""
    blop_scores = blop_scores_for_round(ratios, round_number, with_components)
    top_blop = sorted(blop_scores, key=lambda e: e[1], reverse=True)
    with open(f'{out_dir}/Top (Black) Oppers Round {round_number}{" (Comps)" if with_components else ""}.txt', 'w') as f:
        if with_components:
            print(top_blop[0][2].keys())
            print([ratios[c][1] for c in top_blop[0][2].keys()])
        for p in top_blop:
            if with_components:
                f.write(f"{p[0]}, {p[1]}, {', '.join([str(v) for v in p[2].values()])}\n")
            else:
                f.write(f"{p[0]}, {p[1]}\n")


class Player:
    def __init__(self, name: str, round_numbers: list):
        self.name = name
        self.round_scores = {nr: 0 for nr in round_numbers}

    def add_round_score(self, nr, score):
        self.round_scores[nr] = score

    @property
    def total_score(self):
        return round(sum(self.round_scores.values()), 3)

    @property
    def average_score(self):
        return round(self.total_score / len(self.round_scores), 3)

    def scores_text(self):
        nrs = sorted(self.round_scores.keys(), reverse=True)
        sorted_scores = [str(round(self.round_scores[nr], 3)) for nr in nrs]
        return ','.join(sorted_scores)


def multiple_round_scores(ratio_versions_per_round: dict, round_numbers: list | tuple, out_dir: str):
    player_scores = dict()
    for nr in round_numbers:
        print(f'== ROUND {nr} ==')
        blop_scores = blop_scores_for_round(ratio_versions_per_round[nr], nr)
        for player, score in blop_scores:
            if player not in player_scores:
                player_scores[player] = Player(player, round_numbers)
            player_scores[player].add_round_score(nr, score)
    top_blop_sorted = sorted(player_scores.values(), key=lambda e: e.total_score, reverse=True)

    with open(f'{out_dir}/R{round_numbers[0]} Last {len(round_numbers)} Rounds - full.txt', 'w') as f:
        for player in top_blop_sorted:
            f.write(f"{player.name},{player.total_score},{player.average_score},{player.scores_text()}\n")

