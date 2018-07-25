# Overwatch Stats
A Python library to query a player's overwatch stats from Battle.net

## Requirements
- Python 3.2+
- requests
- lxml
- inflect

## Installation
	pip install overwatch-stats

## Usage
```python
import overwatch.stats
stats = overwatch.stats.query('pc', '현종환#3104')
```

# API
## overwatch.stats.query(platform, battle_tag)
Queries a player's stats from the Battle.net.
### Parameters
- `platform`: `pc`, `xbl` or `psn`
- `battle_tag`: the player's battle tag
