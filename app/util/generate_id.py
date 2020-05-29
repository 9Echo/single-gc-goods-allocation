from datetime import datetime


class TrainId:
    """
    全局车次号
    Args:

    Returns:

    Raise:

    """
    train_id = 0
    overall_time = None

    @staticmethod
    def get_id():
        # 前缀
        suffix = TrainId.overall_time if TrainId.overall_time else datetime.now().strftime("%Y%m%d%H%M")
        TrainId.train_id += 1
        return suffix + str(TrainId.train_id).zfill(4)

    @staticmethod
    def set_id():
        TrainId.train_id = 0
        TrainId.overall_time = None


if __name__ == "__main__":
    for i in range(10):
        print(TrainId.get_id())