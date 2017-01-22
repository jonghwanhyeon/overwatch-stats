import re
import datetime

import requests
import lxml.html
import inflect

from .ids import *

stats_url = 'https://playoverwatch.com/en-us/career/{platform}/{region}/{battle_tag}'

inflector = inflect.engine()
def underscorize_stat_name(name):
    words = re.split(r'\s+', name.lower().replace('-', ' '))
    singular_words = map(inflector.singular_noun, words)

    return '_'.join([
        singular_word or word for singular_word, word in zip(singular_words, words)
    ])

def parse_number(value):
    value = value.replace(',', '')
    
    if value[-1] == '%':
        return float(value[:-1]) / 100
    
    try:
        return int(value)
    except ValueError:
        return float(value)
    
def parse_time(value):
    if value == '--':
        return 0.0
    
    if ':' in value: # e.g. 03:52
        times = list(map(int, value.split(':')))
        
        return datetime.timedelta(**{
            unit: time for unit, time in zip(('seconds', 'minutes', 'hours'), reversed(times))
        }).total_seconds()
    else: # e.g. 98 HOURS
        patterns = {
            'hours': r'(\d+(?:\.\d+)?) hours?',
            'minutes': r'(\d+(?:\.\d+)?) minutes?',
            'seconds': r'(\d+(?:\.\d+)?) seconds?',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, value, re.IGNORECASE)
            if match:
                return datetime.timedelta(**{ key: parse_number(match.group(1)) }).total_seconds()

def parse_stat_value(value):
    # 41 -> int(41)
    # 1,583,117 -> int(1583117)
    # 0.05 -> float(0.05)
    # 14%-> float(0.14)
    # 03:52 -> float(232.0)
    # 09:23:07 -> float(33787.0)
    # 98 HOURS -> float(352800.0)
        
    try:
        return parse_number(value)
    except:
        return parse_time(value)

def extract_play(tree, play_mode):
    if play_mode not in ('quick', 'competitive'):
        raise ValueError('play_mode should be quick or competitive')
    
    if play_mode == 'quick':
        play_mode = 'quickplay'

    play = tree.xpath('.//div[@id="{play_mode}"]'.format(play_mode=play_mode))
    if not play: # e.g. not played the competitive mode
        return None
    
    return play[0]

def has_played(tree, play_mode, category_id=overall_category_id):
    play = extract_play(tree, play_mode)
    if play is None:
        return False

    return bool(play.xpath('.//div[@data-group-id="stats" and @data-category-id="{category_id}"]'.format(
        category_id=category_id
    )))

def extract_level(tree):
    level = tree.find('.//*[@class="player-level"]')

    match = re.search(r'/playerlevelrewards/(0x[0-9A-Z]+)_Border', level.get('style'))
    base_level = level_ids[match.group(1)]

    return base_level + int(level.text_content().strip())

def extract_competitive_rank(tree):
    competitive_rank = tree.find('.//*[@class="competitive-rank"]')
    if competitive_rank is None: # not played competitive mode or not completed placement matches
        return None
    
    return int(competitive_rank.text_content().strip())

def extract_time_played_ratios(tree, play_mode):
    play = extract_play(tree, play_mode)
    if play is None:
        raise ValueError('cannot extract the {play_mode} play'.format(play_mode))

    time_played = play.xpath('.//div[@data-group-id="comparisons" and @data-category-id="overwatch.guid.0x0860000000000021"]')[0]

    output = dict()
    for item in time_played.xpath('.//*[contains(@class, "progress-category-item")]'):
        match = re.search(r'/(0x[0-9A-Z]+)\.png$', item.find('img').get('src'))
        
        hero = inverted_hero_category_ids[match.group(1)]
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
    if not stats: # e.g. not played a cetain hero
        return None
    
    stats = stats[0]

    output = dict()
    for row in stats.findall('.//tbody//tr'):
        name, value = row.findall('.//td')
        output[underscorize_stat_name(name.text_content().strip())] = parse_stat_value(value.text_content().strip())
    
    return output

def query(platform, region, battle_tag):
    response = requests.get(stats_url.format(platform=platform, region=region, battle_tag=battle_tag.replace('#', '-')))
    if response.status_code == 404:
        raise ValueError('cannot find the player {battle_tag}'.format(battle_tag=battle_tag))
    
    tree = lxml.html.fromstring(response.text)

    output = dict()
    output['level'] = extract_level(tree)

    competitive_rank = extract_competitive_rank(tree)
    if competitive_rank:
        output['competitive_rank'] = competitive_rank

    for mode in ('quick', 'competitive'):
        if not has_played(tree, mode):
            continue
            
        output[mode] = {
            'overall': dict(),
            'heroes': dict()
        }
        
        # overall
        output[mode]['overall'] = extract_stats(tree, mode, overall_category_id)
                
        # heroes
        time_played_ratios = extract_time_played_ratios(tree, mode)
        for hero, category_id in hero_category_ids.items():
            if not has_played(tree, mode, category_id):
                continue
            
            output[mode]['heroes'][hero] = extract_stats(tree, mode, category_id)
            # extra stat
            output[mode]['heroes'][hero]['time_played_ratio'] = time_played_ratios[hero]
    
    return output