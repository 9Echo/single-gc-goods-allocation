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
        suffix = TrainId.get_overall_time()
        TrainId.train_id += 1
        return suffix + str(TrainId.train_id)

    @staticmethod
    def set_id():
        TrainId.train_id = 0

    @staticmethod
    def get_overall_time():
        if not TrainId.overall_time:
            TrainId.overall_time = datetime.now().strftime("%Y%m%d%H%M")
        return TrainId.overall_time


if __name__ == "__main__":
    for i in range(10):
        print(TrainId.get_id())