import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.logger import Ranker_Logger
logger = Ranker_Logger.get_logger()

import inspect

class ActionType:
    max_action_id = 0  # 类属性，记录已分配的最大动作ID

    def __init__(self, actor_id):
        ActionType.max_action_id += 1
        self.action_id = ActionType.max_action_id  # 分配唯一的动作ID
        self.actor_id = actor_id
        self.time_stamp = None
        self.success = False
        self.description = ""

    def display_action(self):
        logger.info(f"Action ID: {self.action_id}")
        logger.info(f"Actor ID: {self.actor_id}")
        logger.info(f"Time Stamp: {self.time_stamp}")
        logger.info(f"Success: {self.success}")
        logger.info(f"Description: {self.description}")
    
    def get_json(self):
        '''获取动作的JSON格式数据'''
        json_data = {'action_type': self.__class__.__name__}
        
        # 获取父类实例属性
        parent_attrs = {"action_id", "actor_id", "time_stamp", "success", "description"}
        
        # 获取当前对象的所有属性
        all_attrs = self.__dict__
        
        # 分离父类属性和子类属性
        parent_data = {}
        child_data = {}
        
        for key, value in all_attrs.items():
            if key in parent_attrs:
                parent_data[key] = value
            else:
                child_data[key] = value
        
        json_data.update(parent_data)
        if child_data:
            json_data['sub_attr'] = child_data
        
        return json_data
    

class MoveAction(ActionType):
    def __init__(self, actor_id, destination, movement_type="Ground", speed=0, formation=None):
        super(MoveAction, self).__init__(actor_id)
        self.destination = destination  # 移动目的地坐标
        self.movement_type = movement_type  # 移动类型（地面、空中、水面等）
        self.speed = speed  # 移动速度
        self.formation = formation  # 移动编队

    def display_action(self):
        super().display_action()
        logger.info(f"Destination: {self.destination}")
        logger.info(f"Movement Type: {self.movement_type}")
        logger.info(f"Speed: {self.speed}")
        logger.info(f"Formation: {self.formation}")



class AttackAction(ActionType):
    def __init__(self, actor_id, target, duration, intensity):
        super(AttackAction, self).__init__(actor_id)
        self.target = target  # 攻击目标
        self.duration = duration  # 攻击时间，单位为秒
        self.intensity = intensity  # 攻击强度, 度量范围为0~100

    def display_action(self):
        super().display_action()
        print(f"Target: {self.target}")


class DefendAction(ActionType):
    def __init__(self, actor_id, position, duration=None, reinforcement=None, start_time=None, end_time=None):
        super(DefendAction, self).__init__(actor_id)
        self.position = position  # 驻守位置
        self.duration = duration  # 防御持续时间
        self.reinforcement = reinforcement  # 增援信息
        self.start_time = start_time  # 开始时间
        self.end_time = end_time  # 结束时间
    
    def display_action(self):
        super().display_action()
        print(f"Position: {self.position}")
        print(f"Duration: {self.duration}")
        print(f"Reinforcement: {self.reinforcement}")
        print(f"Start Time: {self.start_time}")
        print(f"End Time: {self.end_time}")


class InvestigateAction(ActionType):
    def __init__(self, actor_id, area, method=None, duration=None, start_time=None, end_time=None):
        super(InvestigateAction, self).__init__(actor_id)
        self.area = area  # 侦查区域
        self.method = method  # 侦查方法
        self.duration = duration  # 侦查持续时间
        self.start_time = start_time  # 开始时间
        self.end_time = end_time  # 结束时间
    
    def display_action(self):
        super().display_action()
        print(f"Area: {self.area}")
        print(f"Method: {self.method}")
        print(f"Duration: {self.duration}")
        print(f"Start Time: {self.start_time}")
        print(f"End Time: {self.end_time}")


class IndirectaimAction(ActionType):
    def __init__(self, actor_id, target, method=None, duration=None, start_time=None, end_time=None):
        super(IndirectaimAction, self).__init__(actor_id)
        self.target = target  # 间瞄目标
        self.method = method  # 间瞄方法
        self.duration = duration  # 间瞄持续时间
        self.start_time = start_time  # 开始时间
        self.end_time = end_time  # 结束时间
    
    def display_action(self):
        super().display_action()
        print(f"Target: {self.target}")
        print(f"Method: {self.method}")
        print(f"Duration: {self.duration}")
        print(f"Start Time: {self.start_time}")
        print(f"End Time: {self.end_time}")

class CommunicationAction(ActionType):
    """通讯动作类，用于描述实体之间的通讯行为

    Args:
        action_id: 动作ID
        actor_id: 执行动作的实体ID
        message: 通讯信息
        target: 通讯目标
        method: 通讯方法（如无线电、信号灯等）
        duration: 通讯持续时间
        start_time: 通讯开始时间
        end_time: 通讯结束时间
    """
    def __init__(self, actor_id, message, target=None, method=None, duration=None, start_time=None, end_time=None):
        super(CommunicationAction, self).__init__(actor_id)
        self.message = message  # 通讯信息
        self.target = target  # 通讯目标
        self.method = method  # 通讯方法
        self.duration = duration  # 通讯持续时间
        self.start_time = start_time  # 开始时间
        self.end_time = end_time  # 结束时间
    
    def display_action(self):
        super().display_action()
        print(f"Message: {self.message}")
        print(f"Target: {self.target}")
        print(f"Method: {self.method}")
        print(f"Duration: {self.duration}")
        print(f"Start Time: {self.start_time}")
        print(f"End Time: {self.end_time}")
