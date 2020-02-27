import functools

from app.utils.code import ResponseCode
from app.utils.my_exception import MyException
from app.utils.weight_calculator import get_item_a_dict_list
from model_config import ModelConfig


def get_item_a(func):
    """
    加载重量计算基础数据
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kw):
        ModelConfig.ITEM_A_DICT.clear()
        data = get_item_a_dict_list(args[0].items)
        for i in data:
            ModelConfig.ITEM_A_DICT.setdefault(i['ITEMID'], {'GBGZL': i['GBGZL'], 'GS_PER': i['GS_PER']})
        return func(*args, **kw)

    return wrapper


def set_weight(func):
    """
    设置载重范围
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kw):
        weight = args[0].truck_weight
        if weight:
            if int(weight) < 20000:
                raise MyException('输入的重量过小，请重新输入！', ResponseCode.Error)
            # 将最大载重、热镀、螺旋最大载重、背包最大载重统一赋值为用户自定义
            ModelConfig.MAX_WEIGHT, ModelConfig.RD_LX_MAX_WEIGHT, ModelConfig.PACKAGE_MAX_WEIGHT \
                = weight, weight, weight
            # 热镀螺旋上浮设置为0
            ModelConfig.RD_LX_UP_WEIGHT = 0
        else:
            # 设置默认值
            ModelConfig.MAX_WEIGHT = ModelConfig.STANDARD_MAX_WEIGHT
            ModelConfig.RD_LX_MAX_WEIGHT = ModelConfig.STANDARD_RD_LX_MAX_WEIGHT
            ModelConfig.RD_LX_UP_WEIGHT = ModelConfig.STANDARD_RD_LX_UP_WEIGHT
            ModelConfig.PACKAGE_MAX_WEIGHT = ModelConfig.STANDARD_PACKAGE_MAX_WEIGHT

        return func(*args, **kw)

    return wrapper
