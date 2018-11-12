import re

import inflect

from .ids import INVERTED_HERO_CATEGORY_IDS, LEVEL_IDS
from .parsers import parse_number, parse_time, parse_stat_value

_inflector = inflect.engine()


def _underscorize_stat_name(name):
    words = re.split(r'\s+', name.lower().replace('-', ' '))
    singular_words = map(_inflector.singular_noun, words)

    return '_'.join([
        singular_word or word for singular_word, word in zip(singular_words, words)
    ])


def extract_play(tree, play_mode):
    if play_mode not in ('quick', 'competitive'):
        raise ValueError('play_mode should be quick or competitive')

    if play_mode == 'quick':
        play_mode = 'quickplay'

    play = tree.xpath('.//div[@id="{play_mode}"]'.format(play_mode=play_mode))
    if not play:  # e.g. not played the competitive mode
        return None

    return play[0]


def extract_level(tree):
    level = tree.find('.//*[@class="player-level"]')
    return int(level.text_content().strip())


def extract_endorsement(tree):
    endorsement = tree.find('.//*[@class="endorsement-level"]')

    shotcaller = endorsement.xpath('.//*[contains(@class, "shotcaller")]')
    shotcaller = float(shotcaller[0].get('data-value')) if shotcaller else 0.0

    teammate = endorsement.xpath('.//*[contains(@class, "teammate")]')
    teammate = float(teammate[0].get('data-value')) if teammate else 0.0

    sportsmanship = endorsement.xpath('.//*[contains(@class, "sportsmanship")]')
    sportsmanship = float(sportsmanship[0].get('data-value')) if sportsmanship else 0.0

    return {
        'level': int(endorsement.text_content().strip()),
        'shotcaller': shotcaller,
        'teammate': teammate,
        'sportsmanship': sportsmanship,
    }


def extract_icon_url(tree):
    icon = tree.find('.//img[@class="player-portrait"]')

    return icon.get('src').strip()


def extract_competitive_rank(tree):
    competitive_rank = tree.find('.//*[@class="competitive-rank"]')
    if competitive_rank is None:  # not played competitive mode or not completed placement matches
        return None

    return int(competitive_rank.text_content().strip())


def extract_time_played_ratios(tree, play_mode):
    play = extract_play(tree, play_mode)
    if play is None:
        raise ValueError('cannot extract the {play_mode} play'.format(play_mode))

    time_played = play.xpath('.//div[@data-group-id="comparisons" and @data-category-id="0x0860000000000021"]')[0]
    output = dict()
    for item in time_played.xpath('.//*[contains(@class, "progress-category-item")]'):
        match = re.search(r'/(0x[0-9A-Z]+)\.png$', item.find('img').get('src'))

        hero = INVERTED_HERO_CATEGORY_IDS[match.group(1)]
        ratio = float(item.get('data-overwatch-progress-percent'))

        output[hero] = ratio

    return output


def extract_stats(tree, play_mode, category_id):
    play = extract_play(tree, play_mode)
    if play is None:
        return None

    stats = play.xpath('.//div[@data-group-id="stats" and @data-category-id="{category_id}"]'.format(
        category_id=category_id
    ))
    if not stats:  # e.g. not played a cetain hero
        return None

    stats = stats[0]

    output = dict()
    for row in stats.findall('.//tbody//tr'):
        name, value = row.findall('.//td')
        output[_underscorize_stat_name(name.text_content().strip())] = parse_stat_value(value.text_content().strip())

    return output
