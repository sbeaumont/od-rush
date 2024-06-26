"""
Utility to scrape the Valhalla pages and extract ranking information.

Round
    Stat
        Ranking
"""
import os.path
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from typing import Callable
import pickle

from config import VALHALLA_URL, CACHE_DIR

NOBODY_PLAYER = 'Nobody (Empty Categories)'


@dataclass
class Ranking:
    rank: int
    player: str
    score: int
    fs_score: float = 0


def get_page(page_url: str) -> BeautifulSoup | None:
    """Utility function to load a URL into a BeautifulSoup instance."""
    page = requests.get(page_url)
    if page.status_code == 200:
        return BeautifulSoup(page.content, "html.parser")
    else:
        return None


def get_stat_page_urls(round_number: int) -> dict[str, str]:
    """Retrieve all stat page URLs from the stat overview page of the round."""
    round_url = '/'.join([VALHALLA_URL, str(round_number)])
    page = get_page(round_url)
    stat_page_urls = {link.text: link['href'] for link in page.find_all('a') if link['href'].startswith(round_url)}
    return stat_page_urls


def parse_entries_from_page(soup: BeautifulSoup) -> dict[str, Ranking]:
    """Pull rankings out of a stat page into a dict{player name: Ranking}."""
    results = dict()
    try:
        # Rare case (happens in test rounds) that no one scored for a category.
        box_body = soup.find('div', class_='box-body').find_all('p')
        if len(box_body) > 0 and box_body[0].text.strip() == 'No records found.':
            print('No records found.')
            return {NOBODY_PLAYER: Ranking(0, NOBODY_PLAYER, 0)}

        for line in soup.tbody.find_all('tr'):
            entry = [child.text.strip() for child in line.find_all('td')]
            ranking = Ranking(int(entry[0]), entry[2], int(entry[-1].replace(',', '')))
            results[ranking.player] = ranking
    except AttributeError:
        # If anything goes wrong, it's likely the page that changed. Print it for analysis.
        print(soup.contents)
        raise
    return results


def feature_scaled_scores(rankings: dict, low=0, high=1):
    """Compress a series of scores into a range from 0 (lowest score) to 1 (highest score)."""
    max_score = max([r.score for r in rankings.values()])
    min_score = min([r.score for r in rankings.values()])
    for r in rankings.values():
        if max_score - min_score > 0:
            r.fs_score = low + ((r.score - min_score) * (high - low)) / (max_score - min_score)
        else:
            r.fs_score = 1


def load_stats(round_number: int, stat_filter: Callable[[str], int], use_cache=True) -> dict:
    """Pull all the Valhalla ranking pages and returns all the relevant ranking lists for a specific round."""
    stat_page_urls = get_stat_page_urls(round_number)
    stat_pages = {k: v for k, v in stat_page_urls.items() if stat_filter(k)}

    cache_file_name = f'{CACHE_DIR}/round_{round_number}.pickle'
    if os.path.exists(cache_file_name) and use_cache:
        print('Loading cached file', cache_file_name)
        with open(cache_file_name, 'rb') as f:
            result = pickle.load(f)
    else:
        result = dict()
        for name, url in stat_pages.items():
            page = get_page(url)
            if page:
                print('Loading', name)
                page_stats = parse_entries_from_page(page)
                if page_stats:
                    feature_scaled_scores(page_stats)
                    result[name] = page_stats
                else:
                    print(f'No stats for {name}')
            else:
                print("Warning: could not load page", url)
        if use_cache:
            with open(cache_file_name, 'wb') as f:
                pickle.dump(result, f)
    return result
