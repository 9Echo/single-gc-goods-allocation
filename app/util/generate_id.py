

class TrainId:
    """
    全局车次号
    Args:

    Returns:

    Raise:

    """
    train_id = 0

    @staticmethod
    def get_id():
        TrainId.train_id += 1
        return TrainId.train_id

    @staticmethod
    def set_id():
        TrainId.train_id = 0
