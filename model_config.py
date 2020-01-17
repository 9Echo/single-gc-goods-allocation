class ModelConfig:
    """模型参数配置
    """
    # 开单参数配置
    INCOMING_WEIGHT = 0
    # 车载最大重量
    MAX_WEIGHT = 33000
    # 热镀、螺旋最大载重
    RD_LX_MAX_WEIGHT = 34000
    # 背包上限
    PACKAGE_MAX_WEIGHT = 33500
    # 体积上限系数
    MAX_VOLUME = 1.18
    # 计算重量、根数基础数据加载
    ITEM_A_DICT = {}
    # 分车次限制重量
    TRUCK_SPLIT_RANGE = 1000
    # 下差严重品类，后续改成通过物资代码前三位识别
    RD_LX_GROUP = ['热镀', '热度', '热镀1', '螺旋焊管', '热镀方矩管', 'QF热镀管']
    # 考虑体积的物资，后续根据成都、重庆和偏远地区调整装车量
    ITEM_ID_DICT = {
        '01C': 22,
        '01A': 16,
        '019': 20,
        '018': 34,
        '017': 34,
        '016': 34,
        '015': 34,
        '014': 34,
        '02C': 22,
        '02A': 16,
        '029': 20,
        '028': 34,
        '027': 34,
        '026': 34,
        '025': 34,
        '024': 40,
        '04C': 22,
        '04A': 16,
        '049': 20,
        '048': 34,
        '047': 34,
        '046': 34,
        '045': 34,
        '044': 40,
        '0C0': 100,
        '0C1': 75,
        '0C2': 49,
        '0C3': 25,
        '0C4': 20,
        '0C5': 18,
        '0C6': 12,
        '0C7': 8,
        '0C8': 6,
    }
