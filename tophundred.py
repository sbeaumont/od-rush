"""
Generator for the OpenDominion Round Top 100 Wiki pages.
"""

import re
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict, field
from datetime import datetime
from config import LAST_ROUND, round_number_of_round_id


URL = f"https://www.opendominion.net/valhalla/round/{LAST_ROUND}/largest-dominions"


WIKI_TABLE = """{{| class="wikitable"
|- ! Rank !! Dominion Name !! Player !! Land Size
{}
|}}"""

WIKI_LINE = """|- style="vertical-align: top;"
| {rank} || [[{dominion_link_name}|{dominion}]] || {player} || {score}"""

WIKI_LINE_WINNER = """|- style="vertical-align: top;"
| {rank} || [[Round_{round}|{dominion} **winning realm**]] || {player} || {score}"""


@dataclass
class Ranking:
    rank: int
    dominion: str
    player: str
    score: int
    realm: int
    round: int
    dominion_link_name: str = field(init=False)

    def __post_init__(self):
        # If it's not a number or letter, turn into underscore
        name = re.sub('[^A-Za-z0-9]', '_', self.dominion)
        # remove multiple underscores in a row
        name = re.sub('_{2,}', '_', name)
        # remove underscores at the end
        name = re.sub('_*$', '', name)
        self.dominion_link_name = f"Round_{self.round}_{name}"


def get_page(page_url: str) -> BeautifulSoup | None:
    """Utility function to load a URL into a BeautifulSoup instance."""
    page = requests.get(page_url)
    if page.status_code == 200:
        return BeautifulSoup(page.content, "html.parser")
    else:
        return None


def parse_entries_from_page(soup: BeautifulSoup) -> dict[str, Ranking]:
    """Pull rankings out of a stat page into a dict{player name: Ranking}."""
    results = dict()
    try:
        for line in soup.tbody.find_all('tr'):
            entry = [child.text.strip() for child in line.find_all('td')]
            ranking = Ranking(int(entry[0]),
                              entry[1],
                              entry[2],
                              int(entry[-1].replace(',', '')),
                              int(entry[4]),
                              round_number_of_round_id(LAST_ROUND))
            results[ranking.player] = ranking
    except AttributeError:
        print(soup.contents)
        raise
    return results


def main():
    soup = get_page(URL)
    entries = parse_entries_from_page(soup).values()
    sorted_entries = sorted(entries, key=lambda e: e.rank)
    winner = sorted_entries[0]
    lines = list()
    for entry in sorted_entries:
        line = WIKI_LINE_WINNER if entry.realm == winner.realm else WIKI_LINE
        lines.append(line.format(**asdict(entry)))
    joined_lines = '\n'.join(lines)
    page_contents = WIKI_TABLE.format(joined_lines)

    with open(f"top_100_round_{round_number_of_round_id(LAST_ROUND)}.txt", 'w') as f:
        f.write(page_contents)
    print(page_contents)


if __name__ == '__main__':
    start = datetime.now()
    main()
    duration = datetime.now() - start
    print(f"Executed in {duration.seconds}.{duration.microseconds} seconds.")
