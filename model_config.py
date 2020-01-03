class ModelConfig:
    """模型参数配置
    """
    # 开单参数配置
    # 车载最大重量
    MAX_WEIGHT = 33000
    # 热镀、螺旋最大载重
    RD_LX_MAX_WEIGHT = 34000
    # 背包上限
    PACKAGE_MAX_WEIGHT = 33500
    # 分车次限制重量
    TRUCK_SPLIT_RANGE = 1000
    RD_LX_GROUP = ['热镀', '热度', '热镀1', '螺旋焊管', '热镀方矩管', 'QF热镀管']