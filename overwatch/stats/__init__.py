import re
import datetime

import requests
from bs4 import BeautifulSoup

from .ids import *

stats_url = 'https://playoverwatch.com/en-us/career/{platform}/{region}/{battle_tag}'

def canonicalize_stat_name(name):
    canonicalized_name = name.lower()
    canonicalized_name = canonicalized_name.replace('-', ' ')
    canonicalized_name = re.sub(r'\s+', '_', canonicalized_name)
    
    return canonicalized_name

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
            'hours': r'(\d+) hours?',
            'minutes': r'(\d+) minutes?',
            'seconds': r'(\d+) seconds?',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, value, re.IGNORECASE)
            if match:
                return datetime.timedelta(**{ key: int(match.group(1)) })

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

def has_played(soup, play_mode, category_id=overall_category_id):
    if play_mode not in ('quick', 'competitive'):
        raise ValueError('play_mode should be quick or competitive')
        
    return bool(soup.find(id='{}-play'.format(play_mode)).find('div', attrs={
        'data-group-id': 'stats',
        'data-category-id': category_id,
    }))

def extract_level(soup):
    level = soup.find(attrs={ 'class': 'player-level' })
    return int(level.text.strip())

def extract_competitive_rank(soup):
    competitive_rank = soup.find(attrs={ 'class': 'competitive-rank' })
    if not competitive_rank:
        return None
    
    return int(competitive_rank.text.strip())

def extract_time_played_ratios(soup, play_mode):
    if play_mode not in ('quick', 'competitive'):
        raise ValueError('play_mode should be quick or competitive')
        
    time_played = soup.find(id='{}-play'.format(play_mode)).find('div', attrs={
        'data-group-id': 'comparisons',
        'data-category-id': 'overwatch.guid.0x0860000000000021',
    })
    
    output = dict()
    for item in time_played.select('.progress-category-item'):
        match = re.search(r'/(0x[0-9A-Z]+)\.png$', item.find('img')['src'])
        
        hero = inverted_hero_category_ids[match.group(1)]
        ratio = float(item['data-overwatch-progress-percent'])
        
        output[hero] = ratio
    
    return output

def extract_stats(soup, play_mode, category_id):
    if play_mode not in ('quick', 'competitive'):
        raise ValueError('play_mode should be quick or competitive')
    
    stats = soup.find(id='{}-play'.format(play_mode)).find('div', attrs={
        'data-group-id': 'stats',
        'data-category-id': category_id
    })
    if not stats: # e.g. not played the competitive mode or a cetain hero
        return None
    
    output = dict()
    for row in stats.select('tbody tr'):
        name, value = row.select('td')
        output[canonicalize_stat_name(name.text.strip())] = parse_stat_value(value.text.strip())
    
    return output

def query(platform, region, battle_tag):
    response = requests.get(stats_url.format(platform=platform, region=region, battle_tag=battle_tag.replace('#', '-')))
    if response.status_code == 404:
        raise ValueError('cannot find the player {battle_tag}'.format(battle_tag=battle_tag))
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    output = dict()
    for mode in ('quick', 'competitive'):
        if not has_played(soup, mode):
            continue
            
        output[mode] = {
            'overall': dict(),
            'heroes': dict()
        }
        
        # overall
        output[mode]['overall'] = extract_stats(soup, mode, overall_category_id)
        # extra stats
        output[mode]['overall']['level'] = extract_level(soup)
        output[mode]['overall']['competitive_rank'] = extract_competitive_rank(soup)
                
        # heroes
        time_played_ratios = extract_time_played_ratios(soup, mode)
        for hero, category_id in hero_category_ids.items():
            if not has_played(soup, mode, category_id):
                continue
            
            output[mode]['heroes'][hero] = extract_stats(soup, mode, category_id)
            # extra stat
            output[mode]['heroes'][hero]['time_played_ratio'] = time_played_ratios[hero]
    
    return output