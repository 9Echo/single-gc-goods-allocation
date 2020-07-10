# -*- coding: utf-8 -*-
# Description:
# Created: liujiaye  2020/07/10
from model_config import ModelConfig


def get_lower_limit(big_commodity_name) -> int:
    if big_commodity_name in ModelConfig.RG_COMMODITY_WEIGHT:
        return ModelConfig.RG_COMMODITY_GROUP[big_commodity_name]
    else:
        return ModelConfig.RG_MIN_WEIGHT
