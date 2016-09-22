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
        return datetime.timedelta(seconds=0)
    
    if ':' in value: # e.g. 03:52
        times = list(map(int, value.split(':')))
        
        return datetime.timedelta(**{
            unit: time for unit, time in zip(('seconds', 'minutes', 'hours'), reversed(times))
        })
    else: # e.g. 98 HOURS
        patterns = {
            'hours': r'(\d+(?:\.\d+)?) hours?',
            'minutes': r'(\d+(?:\.\d+)?) minutes?',
            'seconds': r'(\d+(?:\.\d+)?) seconds?',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, value, re.IGNORECASE)
            if match:
                return datetime.timedelta(**{ key: parse_number(match.group(1)) })

def parse_stat_value(value):
    # 41 -> int
    # 1,583,117 -> int
    # 0.05 -> float
    # 14%-> float(0.14)
    # 03:52 -> timedelta
    # 09:23:07 -> timedelta
    # 98 HOURS -> timedelta
        
    try:
        return parse_number(value)
    except:
        return parse_time(value)

def has_played(tree, play_mode, category_id=overall_category_id):
    if play_mode not in ('quick', 'competitive'):
        raise ValueError('play_mode should be quick or competitive')

    return bool(tree.xpath('.//*[@id="{play_mode}-play"]//div[@data-group-id="stats" and @data-category-id="{category_id}"]'.format(
        play_mode=play_mode, 
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
    if play_mode not in ('quick', 'competitive'):
        raise ValueError('play_mode should be quick or competitive')
    
    time_played = tree.xpath('.//*[@id="{play_mode}-play"]//div[@data-group-id="comparisons" and @data-category-id="overwatch.guid.0x0860000000000021"]'.format(
        play_mode=play_mode
    ))[0]
    
    output = dict()
    for item in time_played.xpath('.//*[contains(@class, "progress-category-item")]'):
        match = re.search(r'/(0x[0-9A-Z]+)\.png$', item.find('img').get('src'))
        
        hero = inverted_hero_category_ids[match.group(1)]
        ratio = float(item.get('data-overwatch-progress-percent'))
        
        output[hero] = ratio
    
    return output

def extract_stats(tree, play_mode, category_id):
    if play_mode not in ('quick', 'competitive'):
        raise ValueError('play_mode should be quick or competitive')
    
    stats = tree.xpath('.//*[@id="{play_mode}-play"]//div[@data-group-id="stats" and @data-category-id="{category_id}"]'.format(
        play_mode=play_mode, 
        category_id=category_id
    ))
    if not stats: # e.g. not played the competitive mode or a cetain hero
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