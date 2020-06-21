class ModelConfig:
    """模型参数配置
    """
    # 日钢标载
    RG_MAX_WEIGHT = 33000
    RG_MIN_WEIGHT = 31000
    RG_SECOND_MIN_WEIGHT = 24000
    RG_SINGLE_UP_WEIGHT = 500
    RG_SINGLE_LOWER_WEIGHT = 1000
    RG_PRIORITY = {'客户催货': 1, '超期清理': 2}
    RG_PRIORITY_GRADE = {1: "A", 2: "B", 3: "C", 4: "D"}
    RG_LY_GROUP = {
        '赣榆区': ['U220-赣榆库', '赣榆区'],
        '黄岛区': ['U210-董家口库', '黄岛区'],
        '淮阴区': ['U288-岚北港口库2', '淮阴区'],
        '灌云县': ['U288-岚北港口库2LYG', '灌云县'],
        '连云区': ['U123-连云港东泰码头(外库)', 'U124-连云港东联码头(外库)', '连云区']
    }
    RG_COMMODITY_GROUP = {'型钢': ['型钢'],
                          '线材': ['线材'],
                          '螺纹': ['螺纹'],
                          '白卷': ['西区开平板', '窄带', '冷板', '白卷', '老区黑卷', '西区黑卷'],
                          '老区黑卷': ['白卷', '老区黑卷', '西区黑卷', '线材'],
                          '西区黑卷': ['西区开平板', '窄带', '冷板', '白卷', '老区黑卷', '西区黑卷'],
                          '西区开平板': ['西区开平板', '窄带', '冷板', '白卷', '西区黑卷', '开平板'],
                          '窄带': ['西区开平板', '窄带', '冷板', '白卷', '西区黑卷'],
                          '冷板': ['西区开平板', '窄带', '冷板', '白卷', '西区黑卷'],
                          '开平板': ['西区开平板', '开平板']
                          }
    RG_COMMODITY_GROUP_FOR_SQL = {'型钢': ['型钢'],
                                  '线材': ['线材'],
                                  '螺纹': ['螺纹'],
                                  '白卷': ['开平板', '窄带', '冷板', '白卷', '黑卷'],
                                  '黑卷': ['白卷', '黑卷', '线材', '开平板', '窄带', '冷板'],
                                  '开平板': ['开平板', '窄带', '冷板', '白卷', '黑卷'],
                                  '窄带': ['开平板', '窄带', '冷板', '白卷', '黑卷'],
                                  '冷板': ['开平板', '窄带', '冷板', '白卷', '黑卷'],
                                  }
    RG_PORT_NAME_END_LYG = ["泰州钢冉码头", "泰州华纳码头",
                            "常州钢材现货交易市场码头", "常州万都码头",
                            "常州新东港码头", "常州武进码头",
                            "无锡国联皋桥码头", "无锡国信码头"]
    RG_COMMODITY_LYG = ["老区黑卷", "西区黑卷", "白卷"]
    RG_VARIETY_VEHICLE = {
        "型钢": ["垫木", "垫皮", "钢丝绳"],
        "线材": ["垫木"],
        "螺纹": ["垫木"],
        "白卷": ["鞍座", "草垫子", "垫皮", "垫木"],
        "老区黑卷": ["鞍座", "草垫子", "垫皮", "垫木"],
        "西区黑卷": ["鞍座", "草垫子", "垫皮", "垫木"],
        "西区开平板": ["垫木"],
        "窄带": ["钢丝绳", "垫皮", "垫木"],
        "冷板": ["钢丝绳"],
        "开平板": ["垫木"]
    }
    RG_WAREHOUSE_GROUP = [
        ['P5-P5冷轧成品库', 'P6-P6冷轧成品库', 'P7-P7剪切成品1库', 'P8-P8精整黑卷成品库'],
        ["B2-小棒库(二棒)", "E1-#1热轧卷成品库", "E2-#2热轧卷成品库", "E3-#3热轧卷成品库", "E4-#4热轧卷成品库", "F1-成品中间库",
         "F2-山东联储中间库", "H1-大H型钢成品库", "T1-小H型钢成品库", "X1-高线库", "X2-多头盘螺库", "Z1-热轧#1580成品库",
         "Z2-热轧#2150成品", "Z4-精整1#成品库", "Z5-开平1、2#成品库", "Z8-开平3#成品库", "ZA-开平5#成品库", "ZC-精整2#成品库"],
        ["F10-运输处临港东库", "F20-运输处临港西库"]
    ]
    # 标准车载最大重量
    STANDARD_MAX_WEIGHT = 33000
    # 标准热镀、螺旋最大载重
    STANDARD_RD_LX_MAX_WEIGHT = 33500
    # 标准热镀、螺旋上浮重量
    STANDARD_RD_LX_UP_WEIGHT = 500
    # 标准背包上限
    STANDARD_PACKAGE_MAX_WEIGHT = 33500
    # 背包重量下浮
    PACKAGE_LOWER_WEIGHT = 2500
    # 体积上限系数
    MAX_VOLUME = 1.18
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
