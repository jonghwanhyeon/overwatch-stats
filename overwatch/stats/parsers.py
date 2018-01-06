import datetime
import re

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