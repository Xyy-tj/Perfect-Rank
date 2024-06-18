import sys
import os
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)
from utils.logger import Ranker_Logger
logger = Ranker_Logger.get_logger()

from typing import List
import warnings


class Player:
    # 类级别的计数器
    _id_counter = 0

    def __init__(self, user_id, nickname, adr, rws, kd, id=None, **kwargs):
        self.id = self._generate_id() if id is None else id  # 分配独有的ID
        self.user_id = user_id
        self.nickname = nickname
        self.adr = adr
        self.rws = rws
        self.kd = kd

    def check_args(self, **kwargs):
        '''检查参数是否符合规范'''
        if kwargs:
            warnings.warn("Unexpected keyword arguments passed to CombatResource.__init__(): %s" % kwargs)
            return False
        return True
        
    @classmethod
    def _generate_id(cls):
        '''生成唯一的ID'''
        cls._id_counter += 1
        return cls._id_counter
    

# 定义游戏场次类
class Game:
    def __init__(self, players_data):
        self.players = {name: Player(name) for name in players_data.keys()}
        self.update_players_data(players_data)
    
    # 更新玩家数据
    def update_players_data(self, players_data):
        for player_name, stats in players_data.items():
            player = self.players[player_name]
            player.add_game(stats[0], stats[1], stats[2])


if __name__ == '__main__':
    game_data = [
        [Player(user_id=1, nickname="Catkin", adr=150, rws=9.9, kd=2.0), 
         Player(user_id=2, nickname="145", adr=150, rws=9.9, kd=2.0),
         Player(user_id=3, nickname="gpt", adr=150, rws=9.9, kd=2.0)],

        [Player(user_id=1, nickname="Catkin", adr=200, rws=9.9, kd=2.0), 
         Player(user_id=2, nickname="145", adr=150, rws=9.9, kd=2.0),
         Player(user_id=3, nickname="gpt", adr=150, rws=9.9, kd=2.0)],
    ]
    player = Player(user_id=1, nickname="Catkin", adr=150, rws=9.9, kd=2.0)
    print(player.user_id)
    print(player.nickname)
    print(player.adr)
    print(player.rws)
    print(player.kd)

    # 统计Catkin用户的平均ADR
    catkin_adr_sum = 0
    catkin_count = 0

    for game in game_data:
        for player in game:
            if player.nickname == "Catkin":
                catkin_adr_sum += player.adr
                catkin_count += 1

    if catkin_count > 0:
        catkin_avg_adr = catkin_adr_sum / catkin_count
        print(f"Catkin的平均ADR为: {catkin_avg_adr}")
    else:
        print("未找到Catkin的数据")
            