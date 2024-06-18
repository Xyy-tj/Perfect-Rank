import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.logger import Ranker_Logger

logger = Ranker_Logger.get_logger()

import json
import sqlite3
import random
import requests
import threading
import time, datetime

from flask import Flask, request, jsonify
from flask_sslify import SSLify
from flask_cors import CORS


from utils.decorator import require_authorize
from functools import wraps
from entity.player.player import Player
from flask import g


license_check_flag = False
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
sslify = SSLify(app)
global_scene_id = 1
global_step = 1


from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('game_data.db')
    return db


# 授权license装饰器
def require_license(func):
    from utils.license import license_check
    @wraps(func)
    def decorated_license(*args, **kwargs):
        global license_check_flag  # 声明使用全局变量
        # 编写授权逻辑，可根据需要进行身份验证、权限检查等
        if license_check_flag:
            return func(*args, **kwargs)
        elif license_check():
            license_check_flag = True
            return func(*args, **kwargs)
        else:
            return jsonify({'message': 'License Failed.'}), 401

    return decorated_license
    

@app.route('/get-players', methods=['GET'])
def get_players():
    '''获取玩家数据'''
    return {'message': 'Get players successfully.'}

@app.route('/player-stats', methods=['GET'])
def player_stats():
    nickname = request.args.get('nickname')
    if not nickname:
        return "Error: No nickname provided.", 400
    n = request.args.get('n', type=int)  # 获取请求参数中的 'n'，并将其转换为整数
    if n is None:
        return "Error: No 'n' parameter provided.", 400
    # 连接SQLite数据库
    conn = sqlite3.connect('game_data.db')
    c = conn.cursor()

    try:
        # 根据nickname查询player_id
        c.execute("SELECT player_id FROM Player WHERE nickname = ?", (nickname,))
        result = c.fetchone()
        if result is None:
            return f"Error: Player with nickname '{nickname}' not found.", 400

        player_id = result[0]

        # 查询该玩家参与的所有游戏的game_id
        c.execute("""
            SELECT game_id
            FROM GamePlayer
            WHERE player_id = ?
        """, (player_id,))
        game_ids = [row[0] for row in c.fetchall()]

        if not game_ids:
            return f"Error: No game data found for player with nickname '{nickname}'.", 400
        
        # 根据game_time字段排序，获取最近N场比赛的game_id
        c.execute(f"""
            SELECT game_id
            FROM Game
            WHERE game_id IN ({','.join('?' for _ in game_ids)})
            ORDER BY game_time DESC
            LIMIT ?
        """, (*game_ids, n))
        recent_game_ids = [row[0] for row in c.fetchall()]
        logger.info(f"recent_game_ids: {recent_game_ids}")

        if not recent_game_ids:
            return f"Error: No recent game data found for player with nickname '{nickname}'.", 400

        # 查询这些比赛中的几项数据的平均值
        c.execute(f"""
            SELECT AVG(adr) as avg_adr, AVG(rws) as avg_rws, AVG(kd) as avg_kd
            FROM GamePlayer
            WHERE player_id = ? AND game_id IN ({','.join('?' for _ in recent_game_ids)})
        """, (player_id, *recent_game_ids))
        averages = c.fetchone()

        if averages is None:
            return f"Error: No game data found for player with nickname '{nickname}'.", 400

        avg_adr, avg_rws, avg_kd = averages

        response = {
            "nickname": nickname,
            "avg_adr": avg_adr,
            "avg_rws": avg_rws,
            "avg_kd": avg_kd
        }

        return jsonify(response)

    except sqlite3.Error as e:
        return f"Database error: {e}", 500
    finally:
        # 关闭数据库连接
        conn.close()


@app.route('/add-game', methods=['GET'])
def add_game():
    '''添加游戏场次数据'''
    data_str = request.data.decode('utf-8')  # 获取JSON字符串
    data = json.loads(data_str)  # 将JSON字符串转换为字典

    game_id = data.get('game_id')
    game_time = data.get('game_time')
    game_map = data.get('map')
    players_data = data.get('players')

    # 连接SQLite数据库
    conn = sqlite3.connect('game_data.db')
    c = conn.cursor()

    try:
        # 开始一个事务
        c.execute("INSERT INTO Game (game_id, game_time, map) VALUES (?, ?, ?)",
                  (game_id, game_time, game_map))

        for player_data in players_data:
            nickname = player_data.get('nickname')

            # 根据nickname查询player_id
            c.execute("SELECT player_id FROM Player WHERE nickname = ?", (nickname,))
            result = c.fetchone()
            if result is None:
                conn.rollback()
                return f"Error: Player with nickname '{nickname}' not found.", 400

            player_id = result[0]


            adr = player_data.get('adr')
            rws = player_data.get('rws')
            kd = player_data.get('kd')

            c.execute("INSERT INTO GamePlayer (game_id, player_id, adr, rws, kd) VALUES (?, ?, ?, ?, ?)",
                      (game_id, player_id, adr, rws, kd))

        # 提交事务
        conn.commit()
    except sqlite3.IntegrityError as e:
        # 处理唯一约束错误
        conn.rollback()
        return f"IntegrityError: {e}", 400
    except sqlite3.OperationalError as e:
        # 处理数据库锁定错误
        conn.rollback()
        return f"OperationalError: {e}", 500
    finally:
        # 关闭数据库连接
        conn.close()

    return "Game data for all players added successfully!"


@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        # OCR需要的库，环境没装，先注释
        # from PIL import Image
        # import pytesseract

        # image = Image.open(file)
        # text = pytesseract.image_to_string(image)
        text = 'Hello OCR'
        return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True, port=9999, host='0.0.0.0')
