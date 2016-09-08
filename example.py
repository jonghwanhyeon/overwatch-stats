from pprint import pprint

import overwatch.stats

stats = overwatch.stats.query('pc', 'kr', '현종환-3104')
pprint(stats, indent=2)
"""
{ 'quick': { 'heroes': { 'ana': { 'cards': 5,
                                  'damage_done': 29781,
                                  'damage_done_average': 1172.97,
                                  'damage_done_most_in_game': 3519,
                                  'damage_done_most_in_life': 1052,
                                  'deaths': 177,
                                  'deaths_average': 6.97,
                                  'defensive_assists': 27,
                                  'defensive_assists_average': 1,
                                  'defensive_assists_most_in_game': 4,
                                  ...}},
             'overall': { 'cards': 346,
                          'damage_done': 1597963,
                          'damage_done_average': 2059,
                          'damage_done_most_in_game': 9797,
                          'deaths': 5522,
                          'deaths_average': 7.11,
                          'defensive_assists': 2017,
                          'defensive_assists_average': 3,
                          'defensive_assists_most_in_game': 18,
                          ...}}}
"""