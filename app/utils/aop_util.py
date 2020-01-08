import functools

from app.utils.weight_calculator import get_item_a_dict_list
from model_config import ModelConfig


def get_item_a(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        ModelConfig.ITEM_A_DICT.clear()
        data = get_item_a_dict_list(args[0].items)
        for i in data:
            ModelConfig.ITEM_A_DICT.setdefault(i['ITEMID'], {'GBGZL': i['GBGZL'], 'GS_PER': i['GS_PER']})
        return func(*args, **kw)

    return wrapper
