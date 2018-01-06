from .extractors import extract_play
from .ids import OVERALL_CATEGORY_ID

def has_played(tree, play_mode, category_id=OVERALL_CATEGORY_ID):
    play = extract_play(tree, play_mode)
    if play is None:
        return False

    return bool(play.xpath('.//div[@data-group-id="stats" and @data-category-id="{category_id}"]'.format(
        category_id=category_id
    )))