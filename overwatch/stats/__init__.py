import datetime
import re

import lxml.html
import requests

from .extractors import (
    extract_level, extract_icon_url, extract_competitive_rank,
    extract_time_played_ratios, extract_stats
)
from .ids import OVERALL_CATEGORY_ID, HERO_CATEGORY_IDS
from .utils import has_played

STATS_URL = 'https://playoverwatch.com/en-us/career/{platform}/{region}/{battle_tag}'

AVAILABLE_PLAY_MODES = ('quick', 'competitive')


def query(platform, region, battle_tag):
    url = STATS_URL.format(platform=platform, region=region, battle_tag=battle_tag.replace('#', '-'))
    response = requests.get(url)
    if response.status_code == 404:
        raise ValueError('cannot find the player {battle_tag}'.format(battle_tag=battle_tag))

    tree = lxml.html.fromstring(response.text)

    output = {}
    output['level'] = extract_level(tree)
    output['icon_url'] = extract_icon_url(tree)

    competitive_rank = extract_competitive_rank(tree)
    if competitive_rank:
        output['competitive_rank'] = competitive_rank

    for mode in AVAILABLE_PLAY_MODES:
        if not has_played(tree, mode):
            continue

        output[mode] = {
            'overall': {},
            'heroes': {},
        }

        # overall
        output[mode]['overall'] = extract_stats(tree, mode, OVERALL_CATEGORY_ID)

        # heroes
        time_played_ratios = extract_time_played_ratios(tree, mode)
        for hero, category_id in HERO_CATEGORY_IDS.items():
            if not has_played(tree, mode, category_id):
                continue

            output[mode]['heroes'][hero] = extract_stats(tree, mode, category_id)
            output[mode]['heroes'][hero]['time_played_ratio'] = time_played_ratios[hero]

    return output
