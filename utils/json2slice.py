import sys
import os

# from networkx import desargues_graph
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)
from entity.player.player import CombatResource
from utils.logger import Ranker_Logger
logger = Ranker_Logger.get_logger()

import json
import entity.player as ett
from entity.player import CombatResourceList
import progressbar


def json2slice(file_path: str) -> CombatResourceList:
    # 读取JSON文件
    with open(file_path, "r", encoding='utf-8') as json_file:
        json_data = json.load(json_file)

    # 将JSON数据转换为作战资源实例
    cr_list = CombatResourceList()
    for entity in json_data:
        class_name = entity.pop('class_name', None)
        domain_name = entity.pop('domain', None)
        check_args_statu = entity.pop('check_args_statu', None)
        adv_scores_data = entity.pop('adv_scores')
        
        # 单独处理adv_scores属性
        adv_scores = ett.AdvScores()
        adv_scores.update_adv_scores(**adv_scores_data)
        if Ranker_Logger.flag["adv_warning"]:
            logger.warning("为保证规则即时生效，当前版本中AdvScores无法从json传递，请确保您已了解该特性")
            Ranker_Logger.flag["adv_warning"] = False
        # entity['adv_scores'] = adv_scores

        if class_name is None:
            raise ValueError("class_name field is missing in JSON data")
        try:
            cls = getattr(ett, class_name)
        except (ModuleNotFoundError, AttributeError):
            raise ValueError(f"Class {class_name} not found in entity package")
        cls_entity: CombatResource = cls(**entity)
        if not cls_entity.check_args_statu:
            logger.warning("Unexpected keyword arguments passed to CombatResource.__init__() for entity %s" % class_name)
        cr_list.add_entity(cls_entity)
        # 恢复entity中的class_name字段
        entity['class_name'] = class_name
        entity['domain'] = domain_name
        entity['check_args_statu'] = check_args_statu
    return cr_list


def slice2json(cr_list: CombatResourceList, file_path: str):
    # 将JSON对象保存为JSON文件
    with open(file_path, "w", encoding='utf-8') as json_file:
        json.dump(cr_list.get_json(), json_file, ensure_ascii=False, indent=4, default=lambda x: x.to_json())  # indent参数用于指定缩进空格数，方便阅读


'''以下为本工具提供的测试函数，用于测试上述函数的正确性，用户可自行修改或删除'''

def test_json2slice():
    cr_list = json2slice("examples/example1/output.json")
    for entity in cr_list.entity_list:
        print(entity.__dict__)

def net_test_slice2json():
    # 创建我方作战资源实例，一个例子
    db_name = "cls_tab.db"
    networkForce_instance = ett.NetworkForce(
                                             model="网络部队类型1",
                                             force_type=3,
                                             network_capability=1,
                                            )
    networkForce_instance.update_position(-0.5, 5.5)
    networkForce_instance.create_table(db_name)

    test_list = CombatResourceList()
    test_list.add_entity(networkForce_instance)

    slice2json(test_list, file_path="examples/example1/output_net.json")

def radio_test_slice2json():
    # 创建我方作战资源实例，一个例子
    db_name = "cls_tab.db"
    electromagneticForce_instance = ett.ElectromagneticForce(
                                             model="电磁部队类型1",
                                             force_type=4,
                                             electromagnetic_capability=1,
                                            )
    electromagneticForce_instance.update_position(-4.5, 4.5)
    electromagneticForce_instance.create_table(db_name)

    test_list = CombatResourceList()
    test_list.add_entity(electromagneticForce_instance)

    slice2json(test_list, file_path="examples/example1/output_radio.json")

def land_test_slice2json():
    # 创建我方作战资源实例，一个例子
    db_name = "cls_tab.db"
    tank_instance = ett.Tank(        model="坦克类型1",
                                     troops=111,
                                     weapons=100,
                                     radar=1000,
                                     max_speed=99,
                                     endurance=101,
                                     armor_thickness=100,
                                     firepower=100,
                                     speed=100,
                                 )
    print(tank_instance)
    vars(tank_instance)
    tank_instance.update_position(-0.5, 0.5)
    tank_instance.create_table(db_name)
    infantry_instance = ett.Infantry(model="步兵类型1",
                                     troops=111,
                                     weapons=100,
                                     radar=1000,
                                     max_speed=99,
                                     endurance=101,
                                     size=100,
                                     equipment=["步枪", "手榴弹"],
                                 )
    infantry_instance.update_position(-0.5, 0.5)
    infantry_instance.create_table(db_name)

    artillery_instance = ett.Artillery(model="火炮类型1",
                                     troops=1111,
                                     weapons=1020,
                                     radar=10200,
                                     max_speed=99,
                                     endurance=101,
                                     caliber=100,
                                     range = 111,
                                     mobility=111
                                     )
    artillery_instance.update_position(-0.1, 0.5)
    artillery_instance.create_table(db_name)

    antiAircraft_instance = ett.AntiAircraft(model="防空武器类型1",
                                       troops=1111,
                                       weapons=1520,
                                       radar=10200,
                                       max_speed=99,
                                       endurance=101,
                                       range=111,
                                       firepower=1111,
                                       mobility=3545
                                       )
    antiAircraft_instance.update_position(-0.1, 1.5)
    antiAircraft_instance.create_table(db_name)

    missileSystem_instance = ett.MissileSystem(model="导弹系统类型1",
                                             troops=1111,
                                             weapons=1520,
                                             radar=10200,
                                             max_speed=99,
                                             endurance=101,
                                             range=111,
                                             missile_type="反舰导弹",
                                             accuracy=3545,
                                             )
    missileSystem_instance.update_position(4.1, 1.5)
    missileSystem_instance.create_table(db_name)

    engineer_instance = ett.Engineer(model="工程兵类型1",
                                               troops=1111,
                                               weapons=1520,
                                               radar=10200,
                                               max_speed=99,
                                               endurance=101,
                                               equipment=["工程车辆","炸弹"],
                                               skills=5,
                                               )
    engineer_instance.update_position(4.1, 5.5)
    engineer_instance.create_table(db_name)

    communicationVehicle_instance = ett.CommunicationVehicle(model="工程兵类型1",
                                                 troops=1111,
                                                 weapons=1520,
                                                 radar=10200,
                                                 max_speed=99,
                                                 endurance=101,
                                                 communication_system="卫星通信",
                                                 encryption_level=1,
                                                 mobility=10,
                                                 )
    communicationVehicle_instance.update_position(4.1, 9.5)
    communicationVehicle_instance.create_table(db_name)

    test_list = CombatResourceList()
    test_list.add_entity(tank_instance)
    test_list.add_entity(infantry_instance)
    test_list.add_entity(artillery_instance)
    test_list.add_entity(antiAircraft_instance)
    test_list.add_entity(missileSystem_instance)
    test_list.add_entity(engineer_instance)
    test_list.add_entity(communicationVehicle_instance)
    slice2json(test_list, file_path="examples/example1/output_land.json")


def ship_test_slice2json():
    # 创建我方作战资源实例，一个例子
    db_name = "cls_tab.db"
    aircraftCarrier_instance = ett.AircraftCarrier(model="航空母舰类型1",
                                                   displacement = 12,
                                                   weapons=10,
                                                   helicopters=10,
                                                   radar=10,
                                                   max_speed=90,
                                                  )
    aircraftCarrier_instance.update_position(1, 1)
    aircraftCarrier_instance.create_table(db_name)

    submarine_instance = ett.Submarine(model="潜艇类型1",
                                       displacement = 12,
                                       weapons=10,
                                       helicopters=10,
                                       radar=10,
                                       max_speed=90,
                                       torpedoes = ["torpedoes1","torpedoes2","torpedoes3"],
                                       sonar_system=1,
                                      )
    submarine_instance.update_position(5, 0.5)
    submarine_instance.create_table(db_name)

    destroyer_instance = ett.Destroyer(model="驱逐舰类型1",
                                       displacement=12,
                                       weapons=10,
                                       helicopters=10,
                                       radar=10,
                                       max_speed=190,
                                       artillery=11,
                                       missile_system=1,
                                     )
    destroyer_instance.update_position(11, 0.5)
    destroyer_instance.create_table(db_name)

    frigate_instance = ett.Frigate(model="护卫舰类型1",
                                   displacement=12,
                                   weapons=10,
                                   helicopters=10,
                                   radar=10,
                                   max_speed=190,
                                   anti_submarine_weapon = ["anti_submarine_weapon1","anti_submarine_weapon2","anti_submarine_weapon3"],
                                   artillery=11,
                                   sonar_system=1,
                                   )
    frigate_instance.update_position(11, 5)
    frigate_instance.create_table(db_name)

    landingShip_instance = ett.LandingShip(model="登陆舰队类型1",
                                           displacement=12,
                                           weapons=10,
                                           helicopters=13,
                                           radar=10,
                                           max_speed=190,
                                           landing_craft = ["landing_craft1","landing_craft2","landing_craft3"],
                                           command_system=1,
                                          )
    landingShip_instance.update_position(111, 5)
    landingShip_instance.create_table(db_name)

    test_list = CombatResourceList()
    test_list.add_entity(aircraftCarrier_instance)
    test_list.add_entity(submarine_instance)
    test_list.add_entity(destroyer_instance)
    test_list.add_entity(frigate_instance)
    test_list.add_entity(landingShip_instance)
    slice2json(test_list, file_path="examples/example1/output_ship.json")

def air_test_slice2json():
    # 创建我方作战资源实例，一个例子
    db_name = "cls_tab.db"
    aircraft_instance = ett.Aircraft(model="飞行器类型1",
                                     endurance=101,
                                     payload=555,
                                     max_speed=99,
                                     combat_radius=34,
                                     radar=1,
                                     weapons=["炸弹","对空导弹"],
                                 )

    aircraft_instance.update_position(-12, 0.5)
    aircraft_instance.create_table(db_name)

    test_list = CombatResourceList()
    test_list.add_entity(aircraft_instance)

    slice2json(test_list, file_path="examples/example1/output_air.json")

def space_test_slice2json():
    # 创建我方作战资源实例，一个例子
    db_name = "cls_tab.db"
    satellite_instance = ett.Satellite(model="卫星类型1",

                                       satellite_type="侦察卫星",
                                       orbit_type="地球同步轨道",
                                       payload="High-resolution camera",
                                       maneuverability="High",
                                      )

    satellite_instance.update_position(-12, 5)
    satellite_instance.create_table(db_name)

    test_list = CombatResourceList()
    test_list.add_entity(satellite_instance)

    slice2json(test_list, file_path="examples/example1/output_space.json")


def test_slice2json():
    # 创建我方作战资源实例，一个例子
    db_name = "cls_tab.db"
    aircraft_instance = ett.Aircraft(model="F-22 Raptor",
                                     endurance=200,
                                     payload=8000,
                                     max_speed=2410,
                                     combat_radius=1600,
                                     radar=True,
                                     weapons=["Missile", "Bomb"],
                                     value=30)
    aircraft_instance.update_position(-0.5, 0.5)
    aircraft_instance.create_table(db_name)
    aircarrier_instance = ett.AircraftCarrier(domain="航空母舰",
                                              model="辽宁舰",
                                              displacement=50000,
                                              weapons=80, helicopters=30,
                                              radar=30,
                                              max_speed=60,
                                              value=99)
    aircarrier_instance.update_position(0.1, 0.2)
    aircarrier_instance.create_table(db_name)
    satellite_instance = ett.Satellite(domain='Earth Observation',
                               model='EOSat-1',
                               satellite_type='EO',
                               orbit_type='LEO',
                               payload='High-resolution camera',
                               maneuverability='High',
                               value=130)
    satellite_instance.update_position(0, -0.3)

def blue_slice_generate():
    # 创建敌方作战资源实例切片
    # db_name = "cls_tab.db"
    blue_cr_list = []
    isowner = False
    # aircraft_instance = ett.Aircraft(model="F-22 Raptor",
    #                                  endurance=200,
    #                                  payload=8000,
    #                                  max_speed=2410,
    #                                  combat_radius=1600,
    #                                  radar=True,
    #                                  weapons=["Missile", "Bomb"],
    #                                  value=30,
    #                                  description="敌方飞机1",
    #                                  id=101,
    #                                 isowner=isowner)
    # aircraft_instance.update_position(0.07, -0.4)
    # blue_cr_list.append(aircraft_instance)

    
    aircarrier_instance = ett.AircraftCarrier(model="里根号航母",
                                              displacement=50000,
                                              weapons=80, helicopters=30,
                                              radar=30,
                                              max_speed=60,
                                              value=99,
                                              description="敌方航母",
                                              id=118,
                                    isowner=isowner)
    aircarrier_instance.update_position(0.1, 0.2)
    blue_cr_list.append(aircarrier_instance)

    destroyer_instance = ett.Destroyer(model="驱逐舰",
                                              artillery=10, missile_system=True,
                                              displacement=50000,
                                              weapons=30, helicopters=10,
                                              radar=None,
                                              max_speed=100,
                                              description="敌方驱逐舰1",
                                              id=119,
                                    isowner=isowner)
    destroyer_instance.update_position(0.35, -0.67)
    blue_cr_list.append(destroyer_instance)

    destroyer_instance2 = ett.Destroyer(model="驱逐舰",
                                              artillery=10, missile_system=True,
                                              displacement=50000,
                                              weapons=30, helicopters=10,
                                              radar=None,
                                              max_speed=100,
                                              description="敌方驱逐舰2",
                                              id=119,
                                    isowner=isowner)
    destroyer_instance2.update_position(0.48, -0.79)
    blue_cr_list.append(destroyer_instance2)

    frigate_instance = ett.Frigate(model="护卫舰",
                                    anti_submarine_weapon=["反潜导弹", "反潜鱼雷"],
                                    artillery=8, sonar_system=True,
                                    displacement=50000,
                                              weapons=30, helicopters=10,
                                              radar=None,
                                              max_speed=100,
                                    description="敌方护卫舰1",
                                    id=116,
                                    isowner=isowner)
    frigate_instance.update_position(0.07, -0.8)
    blue_cr_list.append(frigate_instance)

    frigate_instance2 = ett.Frigate(model="护卫舰",
                                    anti_submarine_weapon=["反潜导弹", "反潜鱼雷"],
                                    artillery=8, sonar_system=True,
                                    displacement=50000,
                                              weapons=30, helicopters=10,
                                              radar=None,
                                              max_speed=100,
                                    description="敌方护卫舰2",
                                    id=117,
                                    isowner=isowner)
    frigate_instance2.update_position(0.51, -0.33)
    blue_cr_list.append(frigate_instance2)
    
    test_list = CombatResourceList(blue_cr_list)
    slice2json(test_list, file_path="examples/example1/blueentity.example")


def red_slice_generate():
    # 创建我方作战资源实例切片
    # db_name = "cls_tab.db"
    isowner = True
    red_cr_list = []
    aircraft_instance = ett.Aircraft(model="歼20",
                                     endurance=200,
                                     payload=8000,
                                     max_speed=2410,
                                     combat_radius=1600,
                                     radar=True,
                                     weapons=["Missile", "Bomb"],
                                     value=30,
                                     description="我方歼击机1",
                                     id=102,
                                     isowner=isowner)
    aircraft_instance.update_position(-0.63, -0.2)
    red_cr_list.append(aircraft_instance)

    aircraft_instance2 = ett.Aircraft(model="歼20",
                                     endurance=200,
                                     payload=8000,
                                     max_speed=2410,
                                     combat_radius=1600,
                                     radar=True,
                                     weapons=["Missile", "Bomb"],
                                     value=30,
                                     description="我方歼击机2",
                                     id=103,
                                     isowner=isowner)
    aircraft_instance2.update_position(-0.4, 0.16)
    red_cr_list.append(aircraft_instance2)
    
    aircraft_instance3 = ett.Aircraft(model="歼20",
                                     endurance=200,
                                     payload=8000,
                                     max_speed=2410,
                                     combat_radius=1600,
                                     radar=True,
                                     weapons=["Missile", "Bomb"],
                                     value=30,
                                     description="我方歼击机3",
                                     id=104,
                                     isowner=isowner)
    aircraft_instance3.update_position(-0.23, 0.47)
    red_cr_list.append(aircraft_instance3)

    aircraft_instance4 = ett.Aircraft(model="歼20",
                                     endurance=200,
                                     payload=8000,
                                     max_speed=2410,
                                     combat_radius=1600,
                                     radar=True,
                                     weapons=["Missile", "Bomb"],
                                     value=30,
                                     description="我方歼击机4",
                                     id=105,
                                     isowner=isowner)
    aircraft_instance4.update_position(-0.13, 0.73)
    red_cr_list.append(aircraft_instance4)

    radar_instance = ett.Radar(model="雷达型号1",
                                    radar_range=200,
                                    radar_accuracy="High",
                                    value=30,
                                    description="我方雷达型号1",
                                    id=106,
                                    isowner=isowner)
    radar_instance.update_position(-0.52, -0.24)
    red_cr_list.append(radar_instance)

    radar_instance2 = ett.Radar(model="雷达型号2",
                                    radar_range=200,
                                    radar_accuracy="High",
                                    value=30,
                                    description="我方雷达2",
                                    id=107,
                                    isowner=isowner)
    radar_instance2.update_position(-0.06, 0.59)
    red_cr_list.append(radar_instance2)

    antiair_instance = ett.GroundAirDefenseUnit(model="防空导弹型号1",
                                    radar_system="雷达系统1",
                                    missile_range=200,
                                    mobility=100,
                                    troops=100,
                                    weapons = 100,
                                    max_speed = 100,
                                    value=30,
                                    description="我方防空导弹1",
                                    id=108,
                                    isowner=isowner)
    antiair_instance.update_position(-0.66, -0.38)
    red_cr_list.append(antiair_instance)

    antiair_instance2 = ett.GroundAirDefenseUnit(model="防空导弹型号2",
                                    radar_system="雷达系统2",
                                    missile_range=200,
                                    mobility=100,
                                    troops=100,
                                    weapons = 100,
                                    max_speed = 100,
                                    value=30,
                                    description="我方防空导弹2",
                                    id=109,
                                    isowner=isowner)
    antiair_instance2.update_position(-0.43, -0.05)
    red_cr_list.append(antiair_instance2)

    antiair_instance3 = ett.GroundAirDefenseUnit(model="防空导弹型号3",
                                    radar_system="雷达系统3",
                                    missile_range=200,
                                    mobility=100,
                                    troops=100,
                                    weapons = 100,
                                    max_speed = 100,
                                    value=30,
                                    description="我方防空导弹3",
                                    id=110,
                                    isowner=isowner)
    antiair_instance3.update_position(-0.15, 0.51)
    red_cr_list.append(antiair_instance3)
    

    test_list = CombatResourceList(red_cr_list)
    slice2json(test_list, file_path="examples/example1/redentity.example")


if __name__ == "__main__":
    # test_json2slice()
    # land_test_slice2json()
    # air_test_slice2json()
    # net_test_slice2json()
    # radio_test_slice2json()
    # ship_test_slice2json()
    # space_test_slice2json()
    blue_slice_generate()
    red_slice_generate()