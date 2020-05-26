import math
import copy
from app.main.pipe_factory.entity.delivery_item import DeliveryItem
from app.main.pipe_factory.entity.delivery_sheet import DeliverySheet
from app.util import weight_calculator
from model_config import ModelConfig


class CreateDeliveryItem():
    def __init__(self,order):
        """
        将订单数据转为订单子项的list
        :param order:订单数据
        :return delivery_item:订单子项的list
        """
        self.success=True
        self.delivery_item_list = []

        for item in order.items:
            delivery_item = DeliveryItem()
            delivery_item.product_type = item.product_type
            delivery_item.spec = item.spec
            delivery_item.quantity = item.quantity
            delivery_item.free_pcs = item.free_pcs
            delivery_item.item_id = item.item_id
            delivery_item.material = item.material
            delivery_item.f_whs = item.f_whs
            delivery_item.f_loc = item.f_loc
            delivery_item.max_quantity = ModelConfig.ITEM_ID_DICT.get(delivery_item.item_id[:3])
            delivery_item.volume = delivery_item.quantity / delivery_item.max_quantity if delivery_item.max_quantity else 0
            delivery_item.weight = weight_calculator.calculate_weight(delivery_item.product_type, delivery_item.item_id, delivery_item.quantity, delivery_item.free_pcs)
            delivery_item.total_pcs = weight_calculator.calculate_pcs(delivery_item.product_type, delivery_item.item_id, delivery_item.quantity, delivery_item.free_pcs)
            # 如果遇到计算不出来的明细，计算异常
            if delivery_item.weight == 0:
                    self.delivery_item_list[0]=delivery_item #一旦计算出错利用list的0号位记录这个项
                    self.success=False
                    break #一时出现计算异常就返回false了

            self.delivery_item_list.append(delivery_item)

    def is_success(self):
        #如果不成功，返回一个特殊的sheet,上面有计算出错的子项，封装到sheet里只是为了利用sheet上额外信息去定位这个定单
        if not self.success:
            sheet = DeliverySheet()
            sheet.weight = '0'
            sheet.items = [self.delivery_item_list[0]]
            return sheet

    def spec(self):
        """
        根据规格优先再对订单子项的list再进行拆分
        :param order:
        :return:
        """

        for delivery_item in self.delivery_item_list:
             # 如果该明细有件数上限并且单规格件数超出，进行切单
            if delivery_item.max_quantity and delivery_item.quantity > delivery_item.max_quantity:
                # copy次数
                count = math.floor(delivery_item.quantity / delivery_item.max_quantity)
                # 最后一个件数余量
                surplus = delivery_item.quantity % delivery_item.max_quantity
                # 标准件数的重量和总根数
                new_weight = weight_calculator.calculate_weight(delivery_item.product_type, delivery_item.item_id, delivery_item.max_quantity, 0)
                new_total_pcs = weight_calculator.calculate_pcs(delivery_item.product_type, delivery_item.item_id, delivery_item.max_quantity, 0)
                # 创建出count个拷贝的新明细，散根数为0，件数为标准件数，总根数为标准总根数，体积占比近似为1
                for i in range(0, count):
                    copy_dilivery_item = copy.deepcopy(delivery_item)
                    copy_dilivery_item.free_pcs = 0
                    copy_dilivery_item.quantity = delivery_item.max_quantity
                    copy_dilivery_item.volume = 1
                    copy_dilivery_item.weight = new_weight
                    copy_dilivery_item.total_pcs = new_total_pcs
                    # 将新明细放入明细列表
                    self.delivery_item_list.append(copy_dilivery_item)
                # 原明细更新件数为剩余件数，体积占比通过件数/标准件数计算
                delivery_item.quantity = surplus
                delivery_item.volume = delivery_item.quantity / delivery_item.max_quantity if delivery_item.max_quantity else 0
                delivery_item.weight = weight_calculator.calculate_weight(delivery_item.product_type, delivery_item.item_id, delivery_item.quantity, delivery_item.free_pcs)
                delivery_item.total_pcs = weight_calculator.calculate_pcs(delivery_item.product_type, delivery_item.item_id, delivery_item.quantity, delivery_item.free_pcs)

        return self.delivery_item_list, True

    def weight(self,order):
        """
        创建提货单子项
        :param order:
        :return:
        """
        product_type = None
        delivery_items = []
        new_max_weight = 0
        for item in order.items:
            if not product_type:
                product_type = item.product_type
                if product_type in ModelConfig.RD_LX_GROUP:
                    new_max_weight = g.RD_LX_MAX_WEIGHT
            for _ in range(item.quantity):
                di = DeliveryItem()
                di.product_type = item.product_type
                di.spec = item.spec
                di.quantity = 1
                di.free_pcs = 0
                di.item_id = item.item_id
                di.material = item.material
                di.f_whs = item.f_whs
                di.f_loc = item.f_loc
                di.volume = 1 / di.max_quantity if di.max_quantity else 0.001
                di.weight = weight_calculator.calculate_weight(di.product_type, di.item_id, di.quantity, di.free_pcs)
                di.total_pcs = weight_calculator.calculate_pcs(di.product_type, di.item_id, di.quantity, di.free_pcs)
                # 如果遇到计算不出来的明细，返回0停止计算
                if di.weight == 0:
                    if di.weight == 0:
                        return [di], False
                delivery_items.append(di)
            for _ in range(item.free_pcs):
                di = DeliveryItem()
                di.product_type = item.product_type
                di.spec = item.spec
                di.quantity = 0
                di.free_pcs = 1
                di.item_id = item.item_id
                di.material = item.material
                di.f_whs = item.f_whs
                di.f_loc = item.f_loc
                di.volume = 0
                di.weight = weight_calculator.calculate_weight(di.product_type, di.item_id, di.quantity, di.free_pcs)
                di.total_pcs = weight_calculator.calculate_pcs(di.product_type, di.item_id, di.quantity, di.free_pcs)
                delivery_items.append(di)
        return delivery_items, new_max_weight, True

    def optimize(self):
        max_delivery_items = []
        min_delivery_items = []

        for delivery_item in self.delivery_item_list:
            # 如果遇到计算不出来的明细，返回0停止计算
            if delivery_item.weight == 0:
                return [delivery_item], [], False
            # 搜集小管
            if dilivery_item.volume == 0:
                min_delivery_items.append(dilivery_item)
                continue
            # 如果该明细有件数上限并且单规格件数超出，进行切单
            if dilivery_item.max_quantity and dilivery_item.quantity > dilivery_item.max_quantity:
                # copy次数
                count = math.floor(dilivery_item.quantity / dilivery_item.max_quantity)
                # 最后一个件数余量
                surplus = dilivery_item.quantity % dilivery_item.max_quantity
                # 标准件数的重量和总根数
                new_weight = weight_calculator.calculate_weight(dilivery_item.product_type, dilivery_item.item_id, dilivery_item.max_quantity, 0)
                new_total_pcs = weight_calculator.calculate_pcs(dilivery_item.product_type, dilivery_item.item_id, dilivery_item.max_quantity, 0)
                # 创建出count个拷贝的新明细，散根数为0，件数为标准件数，总根数为标准总根数，体积占比近似为1
                for i in range(0, count):
                    copy_di = copy.deepcopy(dilivery_item)
                    copy_di.free_pcs = 0
                    copy_di.quantity = dilivery_item.max_quantity
                    copy_di.volume = 1
                    copy_di.weight = new_weight
                    copy_di.total_pcs = new_total_pcs
                    # 将新明细放入明细列表
                    max_delivery_items.append(copy_di)
                # 原明细更新件数为剩余件数，体积占比通过件数/标准件数计算
                dilivery_item.quantity = surplus
                dilivery_item.volume = dilivery_item.quantity / dilivery_item.max_quantity if dilivery_item.max_quantity else 0
                dilivery_item.weight = weight_calculator.calculate_weight(dilivery_item.product_type, dilivery_item.item_id, dilivery_item.quantity, dilivery_item.free_pcs)
                dilivery_item.total_pcs = weight_calculator.calculate_pcs(dilivery_item.product_type, dilivery_item.item_id, dilivery_item.quantity, dilivery_item.free_pcs)

            max_delivery_items.append(dilivery_item)
        return max_delivery_items, min_delivery_items, True
