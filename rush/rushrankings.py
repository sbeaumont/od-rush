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
the V2 ranking set is used on Round 36
The V3 ranking set is used on Round 37 and 38
The V4 ranking set is used on Round 39+.
"""

__author__ = "Serge Beaumont (AgFx)"
__credits__ = ["Rush", ]
__version__ = "1.0"

import re
import statistics

from rush.rankingscraper import load_stats, get_all_land_sizes


def is_blop_stat(stat_name: str) -> bool:
    """Used to filter the relevant rankings in the scraper."""
    blop_keywords = [
        'Wizard',
        'Spies',
        'Thieves',
        'Masters',
        'Saboteurs',
        'Snare',
        'Spy',
        'Assassins',
        'Bounties',
        'Largest Dominions']
    for kw in blop_keywords:
        if kw in stat_name:
            return True
    return False


def is_dom_stat(stat_name: str) -> bool:
    """Filter out realm, pack, and solo rankings - only include individual dominion stats."""
    exclude_keywords = ['Realm', 'Pack', 'Solo']
    for kw in exclude_keywords:
        if kw in stat_name:
            return False
    return True


def all_player_names(stats: dict) -> set:
    players = set()
    for stat in stats.values():
        players.update(stat.keys())
    players.discard("Bot")
    return players


def sanitize_name_for_csv(name: str) -> str:
    """Replace commas in player names with underscores to prevent CSV parsing issues."""
    return name.replace(',', '_')


def score_components(ratios: dict, stats: dict, name: str, land_sizes: dict = None) -> dict:
    """Score a specific player on all components of the scoring system for the round."""
    result = dict()
    for component_name, score_component in ratios.items():
        component_score = 0
        if score_component['calculation'] == 'average':
            total = 0
            for stat_name in score_component['rankings']:
                if name in stats[stat_name]:
                    total += stats[stat_name][name].fs_score
            component_score = total / len(score_component['rankings']) * score_component['weight']
        elif re.fullmatch(r'average of best (\d+)', score_component['calculation']):
            best = int(re.search(r'average of best (\d+)', score_component['calculation']).group(1))
            ranking_scores = list()
            for stat_name in score_component['rankings']:
                if name in stats[stat_name]:
                    ranking_scores.append(stats[stat_name][name].fs_score)
            best_scores = sorted(ranking_scores, reverse=True)[:best]
            component_score = sum(best_scores) / best * score_component['weight']
        else:
            raise Exception(f"Unknown calculation method: {score_component['calculation']}")

        # Apply small-land penalty if relevant
        if land_sizes and name in land_sizes and 'small_land_max_penalty' in score_component:
            penalty = score_component['small_land_max_penalty']
            if penalty > 0:
                min_land = min(land_sizes.values())
                max_land = max(land_sizes.values())
                threshold = score_component.get('small_land_penalty_threshold', None)
                component_score = apply_low_land_penalty(
                    component_score,
                    land_sizes[name],
                    min_land,
                    max_land,
                    penalty,
                    threshold
                )

        result[component_name] = component_score
    return result


def calculate_player_score(ratios: dict, stats: dict, name: str, land_sizes: dict = None) -> float:
    """The player's total score is the sum total of all the scoring components."""
    player_score = sum([cs for cs in score_components(ratios, stats, name, land_sizes).values()])
    return round(player_score, 3)


def blop_scores_for_round(ratios: dict, round_number: int, with_components=False) -> list:
    """Calculate the scores for all players in a specific round."""
    # Build scaling methods dict from ratios config
    scaling_methods = {}
    for component_name, component_config in ratios.items():
        scaling_style = component_config.get('scaling_style', 'linear')
        for stat_name in component_config['rankings']:
            scaling_methods[stat_name] = scaling_style

    stats = load_stats(round_number, stat_filter=is_dom_stat, scaling_methods=scaling_methods)
    players = all_player_names(stats)

    # Get land sizes for known players only
    all_land_sizes = get_all_land_sizes(round_number, stat_filter=is_dom_stat)
    land_sizes = {player: land for player, land in all_land_sizes.items()
                  if player in players}

    if with_components:
        return [(player, calculate_player_score(ratios, stats, player, land_sizes), score_components(ratios, stats, player, land_sizes)) for player in players]
    else:
        return [(player, calculate_player_score(ratios, stats, player, land_sizes)) for player in players]


def round_scores(ratios: dict, round_number: int, out_dir: str, with_components=False):
    """Output the round scores in a CSV format that can be imported into a spreadsheet."""
    blop_scores = blop_scores_for_round(ratios, round_number, with_components)
    top_blop = sorted(blop_scores, key=lambda e: e[1], reverse=True)

    # Get land sizes for all players
    all_land_sizes = get_all_land_sizes(round_number)

    with open(f'{out_dir}/Top (Black) Oppers Round {round_number}{" (Comps)" if with_components else ""}.txt', 'w') as f:
        if with_components:
            print(top_blop[0][2].keys())
            print([ratios[c]['weight'] for c in top_blop[0][2].keys()])
        for p in top_blop:
            player_name = p[0]
            sanitized_name = sanitize_name_for_csv(player_name)
            land_size = all_land_sizes.get(player_name, 0)
            if with_components:
                f.write(f"{sanitized_name}, {land_size}, {p[1]}, {', '.join([str(v) for v in p[2].values()])}\n")
            else:
                f.write(f"{sanitized_name}, {land_size}, {p[1]}\n")


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


def apply_low_land_penalty(score: float, player_land: float, min_land: float, max_land: float, max_penalty: float = 0.5, threshold: float = None) -> float:
    """
    Apply gradual penalty to a single score based on land size.
    Uses a concave curve (square root) for more gradual penalty.

    Args:
        score: The original score to adjust
        player_land: The player's land size
        min_land: Minimum land size in the round
        max_land: Maximum land size in the round
        max_penalty: Maximum penalty to apply (e.g., 0.5 for 50% reduction at smallest size)
        threshold: Optional land size threshold. If specified, no penalty is applied above this
                  value, and penalty scales from 0% at threshold to max_penalty at min_land.
                  If None, uses max_land as the threshold (original behavior).

    Returns:
        Adjusted score with penalty applied
    """
    if max_penalty < 0:
        raise ValueError(f"max_penalty must be >= 0, got {max_penalty}")
    if max_penalty == 0:
        return score  # No penalty configured

    # Use threshold if specified, otherwise fall back to max_land
    effective_max = threshold if threshold is not None else max_land

    # No penalty if player is at or above threshold
    if player_land >= effective_max:
        return score

    if effective_max < min_land:
        raise ValueError(f"effective_max ({effective_max}) must be >= min_land ({min_land})")
    if effective_max == min_land:
        raise ValueError(f"effective_max equals min_land ({effective_max}) - invalid land data")
    if player_land < min_land:
        raise ValueError(f"player_land ({player_land}) is below min_land ({min_land})")

    # Land ratio: 0 at min_land, 1 at effective_max
    land_ratio = (player_land - min_land) / (effective_max - min_land)

    # Concave curve using square root
    # At min land (ratio=0): sqrt(0) = 0 → multiplier = 1 - max_penalty
    # At effective_max (ratio=1): sqrt(1) = 1 → multiplier = 1
    multiplier = 1.0 - max_penalty * (1 - land_ratio ** 0.5)

    return score * multiplier


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
            sanitized_name = sanitize_name_for_csv(player.name)
            f.write(f"{sanitized_name},{player.total_score},{player.average_score},{player.scores_text()}\n")

