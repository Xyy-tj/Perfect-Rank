import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.logger import Ranker_Logger
logger = Ranker_Logger.get_logger()

from typing import Optional
from entity.player import CombatResource, CombatResourceList


class Task:
    '''任务类，表示任务的信息'''
    def __init__(self):
        self.name: str  # 任务名称，指定为字符串类型
        self.description: str  # 任务描述，指定为字符串类型


class CombatScore:
    '''某方阵营的分数类'''
    def __init__(self):
        pass

    def display_info(self):
        pass


class Observation:
    """
    观察类，智能体可以观察到的杀伤观察信息
    """
    def __init__(self):
        self.time: str  # 时间，指定为字符串类型
        self.task: Optional[Task] = None  # 任务，假设entity是一个类或类型，使用Optional表示可选
        self.red_entity: CombatResourceList  # 红方实体清单，假设value是一个类型
        self.blue_entity: CombatResourceList  # 蓝方实体清单，假设value是一个类型
        self.red_score: CombatScore  # 红方得分，指定为浮点数类型
        self.blue_score: CombatScore  # 蓝方得分，指定为浮点数类型
        self.step: int  # 步长，指定为整数类型
        self.scene_id: int  # 场景ID，指定为整数类型

        # if isinstance(observation, dict):
        #     # 如果observation是dict类型
        #     for key, value in observation.items():
        #         setattr(self, key, value)
        # elif isinstance(observation, Observation):
        #     # 如果observation是OBS类的实例
        #     for key, value in observation.__dict__.items():
        #         setattr(self, key, value)
        # else:
        #     raise ValueError("Invalid input type. observation should be dict or OBS class.")

    def obs_setup(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
            logger.debug(f"【态势信息载入】属性 {key} 设置为 {value}")

    def get_red_entity(self):
        return self.red_entity
    
    def get_blue_entity(self):
        return self.blue_entity
    
    