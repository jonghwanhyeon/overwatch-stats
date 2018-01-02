from pprint import pprint

import overwatch.stats

stats = overwatch.stats.query('pc', 'kr', '현종환-3104')
pprint(stats, indent=2)
"""
{ 'competitive': { 'heroes': { 'bastion': { 'all_damage_done': 2070,
                                            'all_damage_done_avg_per_10_min': 79.08,
                                            'all_damage_done_most_in_game': 2070,
                                            'all_damage_done_most_in_life': 2070,
                                            'barrier_damage_done': 1426,
                                            'barrier_damage_done_avg_per_10_min': 54,
                                            'barrier_damage_done_most_in_game': 1426,
                                            'death': 1,
                                            'death_avg_per_10_min': 0,
                                            'elimination': 2,
                                            'elimination_avg_per_10_min': 0,
                                            ...},
                               'dva': { 'all_damage_done': 24328,
                                        'all_damage_done_avg_per_10_min': 15.22,
                                        'all_damage_done_most_in_game': 12323,
                                        'all_damage_done_most_in_life': 3723,
                                        'barrier_damage_done': 8390,
                                        'barrier_damage_done_avg_per_10_min': 5,
                                        'barrier_damage_done_most_in_game': 4138,
                                        'card': 1,
                                        ...}},
  'competitive_rank': 1752,
  'level': 449,
  'quick': { 'heroes': { 'ana': { 'all_damage_done': 152201,
                                  'all_damage_done_avg_per_10_min': 2.87,
                                  'all_damage_done_most_in_game': 3739,
                                  'all_damage_done_most_in_life': 1517,
                                  'barrier_damage_done': 300,
                                  'barrier_damage_done_avg_per_10_min': 1,
                                  'barrier_damage_done_most_in_game': 300,
                                  'biotic_grenade_kill': 2,
                                  'card': 21,
                                  'death': 718,
                                  'death_avg_per_10_min': 0,
                                  'defensive_assist': 447,
                                  ...}}}
"""
