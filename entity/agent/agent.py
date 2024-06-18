import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.logger import Ranker_Logger
logger = Ranker_Logger.get_logger()

from typing import Union, List
import random

from entity.action import ActionType
from entity.map import Map 
from entity.ovservation.observation import Observation

from algorithm.advAssAlg import SituationAdvantage, AdvRule
from algorithm.thrSrtAlg import ThrRule
from algorithm.resSchAlg import ResRule


class BaseAgent:
    def __init__(self, config):
        self.config: dict
        self.scenario: str
        self.color: str
        self.faction: str
        self.seat: int
        self.role: str
        self.user_name: str
        self.user_id: int
        self.priority: dict
        self.observation: Observation
        self.map: Map
        self.map_data: dict
        self.rules_group_adv:  List[AdvRule]
        self.rules_group_thr:  List[ThrRule]
        self.rules_group_res:  List[ResRule]

    def setup(self, setup_info: dict):
        """在推演开始之前，向agent提供此次推演的相关信息，AI应在此函数中进行一些初始化等操作。
        此方法只接收一个参数“setup_info”；此参数为一个字典，字典内包含关于当前推演的一些开局信息。
        
        生成动作列表：
            阶段1处理：如果观察信息中的时间阶段为1，根据操作员的子类型生成特定类型的动作，并返回动作列表。
            非阶段1处理：遍历所有可控制的操作员及其可执行的动作，根据优先级字典self.priority中定义的动作类型顺序，逐个生成可执行的动作实例，并将其添加到总动作列表total_actions中。
        
        Args:
            setup_info (dict): 战场信息，包括场景信息、基础数据、费用数据、视野数据、阵营信息、座位信息、角色信息、用户名、用户ID等

        Returns:
            list: 返回一个包含一个或多个Action的列表
        """
        self.scenario = setup_info.get("scenario", None)
        self.color = setup_info.get("faction", None)
        self.faction = setup_info.get("faction", None)
        self.seat = setup_info.get("seat", None)
        self.role = setup_info.get("role", None)
        self.user_name = setup_info.get("user_name", None)
        self.user_id = setup_info.get("user_id", None)
        # self.priority = {
        #     ActionType.Occupy: self.gen_occupy,
        #     ActionType.Shoot: self.gen_shoot,
        #     ActionType.GuideShoot: self.gen_guide_shoot,
        #     ActionType.JMPlan: self.gen_jm_plan,
        #     ActionType.LayMine: self.gen_lay_mine,
        #     ActionType.ActivateRadar: self.gen_activate_radar,
        #     ActionType.ChangeAltitude: self.gen_change_altitude,
        #     ActionType.GetOn: self.gen_get_on,
        #     ActionType.GetOff: self.gen_get_off,
        #     ActionType.Fork: self.gen_fork,
        #     ActionType.Union: self.gen_union,
        #     ActionType.EnterFort: self.gen_enter_fort,
        #     ActionType.ExitFort: self.gen_exit_fort,
        #     ActionType.Move: self.gen_move,
        #     ActionType.RemoveKeep: self.gen_remove_keep,
        #     ActionType.ChangeState: self.gen_change_state,
        #     ActionType.StopMove: self.gen_stop_move,
        #     ActionType.WeaponLock: self.gen_WeaponLock,
        #     ActionType.WeaponUnFold: self.gen_WeaponUnFold,
        #     ActionType.CancelJMPlan: self.gen_cancel_JM_plan
        # }  # choose action by priority
        self.observation = setup_info.get("observation", None)
        self.rules_group_adv, self.rules_group_thr, self.rules_group_res = self.default_rules()
        # self.map = Map(
        #     setup_info["basic_data"],
        #     setup_info["cost_data"],
        #     setup_info["see_data"]
        # )  # use 'Map' class as a tool
        # self.map_data = self.map.get_map_data()

    def step(self, observation: Observation):
        self.observation = observation  # save observation for later use
        self.team_info = observation["role_and_grouping_info"]
        self.controllable_ops = observation["role_and_grouping_info"][self.seat][
            "operators"
        ]
        communications = observation["communication"]
        for command in communications:
            if command["type"] in [200, 201] and command["info"]["company_id"] == self.seat:
                if command["type"] == 200:
                    self.my_mission = command
                elif command["type"] == 201:
                    self.my_direction = command
        total_actions = []

        if observation["time"]["stage"] == 1:
            actions = []
            for item in observation["operators"]:
                if item["obj_id"] in self.controllable_ops:
                    operator = item
                    if operator["sub_type"] == 2 or operator["sub_type"] == 4:
                        actions.append(
                            {
                                "actor": self.seat,
                                "obj_id": operator["obj_id"],
                                "type": 303,
                                "target_obj_id": operator["launcher"],
                            }
                        )
            actions.append({
                "actor": self.seat,
                "type": 333
            })
            return actions

        # loop all bops and their valid actions
        for obj_id, valid_actions in observation["valid_actions"].items():
            if obj_id not in self.controllable_ops:
                continue
            for (
                action_type
            ) in self.priority:  # 'dict' is order-preserving since Python 3.6
                if action_type not in valid_actions:
                    continue
                # find the action generation method based on type
                gen_action = self.priority[action_type]
                action = gen_action(obj_id, valid_actions[action_type])
                if action:
                    total_actions.append(action)
                    break  # one action per bop at a time
        return total_actions
    
    def reset(self):
        self.scenario = None
        self.color = None
        self.priority = None
        self.observation = None
        self.map = None
        self.scenario_info = None
        self.map_data = None
        self.seat = None
        self.faction = None
        self.role = None
        self.controllable_ops = None
        self.team_info = None
        self.my_direction = None
        self.my_mission = None
        self.user_name = None
        self.user_id = None
        self.history = None
        self.rules_group_adv, self.rules_group_thr, self.rules_group_res = self.default_rules()

    
    def update_obs(self, observation: Observation):
        '''更新观察信息，传入新的观察信息，更新agent的观察信息

        - args:
            observation (Union[dict, Observation]): 新的观察信息
        '''
        self.observation = observation


    def default_rules(self):
        '''默认规则组

        - returns:
            List[AdvRule]: 默认规则组
        '''
        from algorithm.advAssAlg import SpecificRule, SpecificRule2
        from algorithm.thrSrtAlg import SpecificThrRule, SpecificThrRule2
        from algorithm.resSchAlg import SpecificResRule, SpecificResRule2

        rule1 = SpecificRule()
        rule2 = SpecificRule2()

        thr_rule1 = SpecificThrRule()
        thr_rule2 = SpecificThrRule2()

        res_rule1 = SpecificResRule()
        res_rule2 = SpecificResRule2()

        return [rule1, rule2], [thr_rule1, thr_rule2], [res_rule1, res_rule2]


    def set_rules(self, adv_rules: List[AdvRule]=None, thr_rules: List[ThrRule]=None, res_rules: List[ResRule]=None):
        '''设置规则组

        - args:
            rules (List[AdvRule]): 规则组
        '''
        try:
            if adv_rules:
                self.rules_group_adv = adv_rules
                logger.info(f"【规则设置】设置优势评估规则组：{adv_rules}")
            if thr_rules:
                self.rules_group_thr = thr_rules
                logger.info(f"【规则设置】设置威胁识别规则组：{thr_rules}")
            if res_rules:
                self.rules_group_res = res_rules
                logger.info(f"【规则设置】设置资源调度规则组：{res_rules}")
            
        except:
            logger.info(f"【规则设置】规则设置失败，请检查相关规则实现细节")
        finally:
            return True
        


    # TODO: Implement the following methods
    def adv_ass_by_rules(self):

        advalg = SituationAdvantage(self.observation)
        for rule in self.rules_group_adv:
            advalg.add_rule(rule)
        advscore = advalg.quantize()

        gain = random.randint(0, 5)
        red_count = len(self.observation.red_entity)
        blue_count = len(self.observation.blue_entity)
        red_value = advscore * 40 + gain * 2
        blue_value  = (100-advscore) * 40 + gain * 2

        return advscore, red_count, blue_count, red_value, blue_value
    
    def adv_ass_by_step(self):
        import sqlite3
        scene_id= self.observation.scene_id
        step = self.observation.step

        # 连接到数据库
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

        # 执行查询
        cursor.execute("SELECT Red FROM adv WHERE SceneID = ? AND Step = ?", (scene_id, step))
        advscore = cursor.fetchone()
        if isinstance(advscore, tuple):
            advscore = advscore[0]

        cursor.execute("SELECT RedCount FROM adv WHERE SceneID = ? AND Step = ?", (scene_id, step))
        red_count = cursor.fetchone()
        if isinstance(red_count, tuple):
            red_count = red_count[0]

        cursor.execute("SELECT BlueCount FROM adv WHERE SceneID = ? AND Step = ?", (scene_id, step))
        blue_count = cursor.fetchone()
        if isinstance(blue_count, tuple):
            blue_count = blue_count[0]

        # 关闭连接
        conn.close()
        gain = random.randint(0, 5)
        red_value = advscore * 40 + gain * 2
        blue_value  = (100-advscore) * 40 + gain * 2
        return advscore, red_count, blue_count, red_value, blue_value
    

    # TODO: Implement the Adv_ass method based on LLM
    def adv_ass_by_ai(self):
        """提供对接大模型的优势评估方法接口
        

        Returns:
            _type_: _description_
        """
        advscore = ...
        pass
        return advscore


    def threaten_recog(self):
        # 从self.observation.blue_entity中获取符合威胁定义的entity
        all_indices = []
        for thr_rule in self.rules_group_thr:
            flag_i, indices_i = thr_rule.judge(self.observation)
            all_indices.append(indices_i)  # 确保indices_i作为一个子列表添加

        # 合并所有的indices并去除重复项
        merged_indices = set()
        for indices in all_indices:
            merged_indices.update(indices)  # 将子列表中的元素添加到集合中，自动去重

        # 如果需要返回列表形式，可以将集合转换为列表
        return self.observation.blue_entity.get_json_by_indices(list(merged_indices))
    

    # TODO: Implement the following methods
    from algorithm.resSchAlg import ResSchCfg
    def action_schedul(self, cfg: ResSchCfg):
        from entity.action import ActionType, MoveAction
        from algorithm.resSchAlg import resSchAlg

        # 调用调度算法类的类方法run()函数得到调度结果动作列表
        logger.debug("调度算法logger debug层次")
        actions_dict = resSchAlg.run(self.observation, cfg=cfg)
        
        return actions_dict

