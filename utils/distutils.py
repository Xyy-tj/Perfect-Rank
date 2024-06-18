from ast import Tuple
import sys
import os

# from networkx import desargues_graph
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)
from entity.player.player import CombatResource
from utils.logger import Ranker_Logger
logger = Ranker_Logger.get_logger()


def is_within_range(point_a: Tuple, point_b: Tuple, threshold: float):
    """
    If the distance between two points in a two-dimensional coordinate system is within the detection range
    判断两个点在二维坐标系下的距离是否在侦查范围内

    Args:
        point_a (Tuple): _description_
        point_b (Tuple): _description_
        threshold (float): _description_

    Returns:
        _type_: _description_
    """
    import math
    # 计算二维坐标系下两点之间的距离是否在侦查范围内
    if math.sqrt((point_a[0] - point_a[0]) ** 2 + (point_b[0] - point_b[1]) ** 2) <= threshold:
        return True
    return False