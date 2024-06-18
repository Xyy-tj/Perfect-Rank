#  TTTTTTTTTT      JJJJJJJJ         NNNN     NN        AAAA        MMMMM     MMMM    IIIIIIIII
#  TTTTTTTTTT      JJJJJJJJ         NNNNN    NN      AAAAAAAA      MMMMMM   MMMMM      IIII
#     TTTT            JJJJ          NNNNNN   NN     AAAA  AAAA     MMMMMMM MMMMMMM     IIII
#     TTTT            JJJJ          NNNNNNN  NN    AAAA    AAAA    MMMM MMMMM MMMM     IIII
#     TTTT            JJJJ          NNNN NN  NN   AAAAAAAAAAAAAA   MMMM  MMM  MMMM     IIII
#     TTTT            JJJJ          NNNN  NN NN  AAAAAAAAAAAAAAAA  MMMM       MMMM     IIII
#     TTTT         J  JJJJ      J   NNNN   NNNN  AAAA        AAAA  MMMM       MMMM     IIII
#     TTTT         J  JJJJ      J   NNNN    NNN AAAA          AAAA MMMM       MMMM     IIII
#     TTTT         JJJJJJJJ    JJ   NNNN     NN AAAA          AAAA MMMM       MMMM    IIIIIIIII
#     TTTT         JJJJJJJJ    JJ   NNNN     NN AAAA          AAAA MMMM       MMMM    IIIIIIIII
#

import logging
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# 加载.env文件中的环境变量
load_dotenv()

# 定义不同颜色的日志输出格式
class ColorFormatter(logging.Formatter):
    COLORS = {
        '资源性优势评估得分': '\033[94m',  # Blue
        '规则性优势评估得分': '\033[93m',  # Yellow
        '优势评估规则写入': '\033[92m',  # Green
        '威胁分析': '\033[91m',  # Red
        'END': '\033[0m',
        'RED':'\033[91m',
    }

    def format(self, record):
        message = super(ColorFormatter, self).format(record)
        log_time = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        log_level = record.levelname
        log_message = record.getMessage()
        log_source = f"{record.filename}:{record.lineno}"

        if record.levelname == 'ERROR':
            return f"{self.COLORS['RED']}[{log_time}] [{log_level}] [{log_source}] {message}{self.COLORS['END']}"
        
        for keyword, color_code in self.COLORS.items():
            if keyword in message:
                return f"{color_code}[{log_time}] [{log_level}] [{log_source}] {message}{self.COLORS['END']}"

        return f"[{log_time}] [{log_level}] [{log_source}] {message}"



class CustomBufferingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.converter = self.beijing_time_converter

    def emit(self, record):
        log_record = (self.formatTime(record, "%Y-%m-%d %H:%M:%S"), record.levelname, f"{record.filename}:{record.lineno}", record.getMessage())
        Ranker_Logger.log_buffer.append(log_record)

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            s = "%s,%03d" % (t, record.msecs)
        return s

    def beijing_time_converter(self, timestamp):
        utc_time = datetime.utcfromtimestamp(timestamp)
        beijing_time = utc_time + timedelta(hours=8)
        return beijing_time.timetuple()

class Ranker_Logger:
    _instance = None
    log_buffer = []
    flag = {"adv_warning": True}

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Ranker_Logger, cls).__new__(cls)
            cls._instance.logger = logging.getLogger(__name__)
            debug_mode = os.getenv('LOG_LEVEL')
            print('debug_mode:',debug_mode)
            if debug_mode == "DEBUG":
                cls._instance.logger.setLevel(logging.DEBUG)
            elif debug_mode == "INFO":
                cls._instance.logger.setLevel(logging.INFO)
            elif debug_mode == "WARNING":
                cls._instance.logger.setLevel(logging.WARNING)
            elif debug_mode == "ERROR":
                cls._instance.logger.setLevel(logging.ERROR)
            elif debug_mode == "CRITICAL":
                cls._instance.logger.setLevel(logging.CRITICAL)
            else:
                cls._instance.logger.setLevel(logging.INFO)
            
            # 创建自定义颜色格式化器的实例
            color_formatter = ColorFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # 控制台处理器使用颜色格式化器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(color_formatter)
            
            # 文件处理器可以使用默认格式化器，或者也可以使用颜色格式化器
            file_handler = logging.FileHandler('logs/logfile.log')
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

            # 自定义缓冲处理器
            buffering_handler = CustomBufferingHandler()

            # 添加处理器到logger
            cls._instance.logger.addHandler(console_handler)
            cls._instance.logger.addHandler(file_handler)
            cls._instance.logger.addHandler(buffering_handler)

            # 启动定时推送日志到SQLite数据库的线程
            # threading.Thread(target=cls._instance.push_logs_to_buffer_periodically, daemon=True).start()
            threading.Thread(target=cls._instance.push_logs_to_db_periodically, daemon=True).start()


            print(cls._instance.logger)
        # print(cls._instance)
        # print(dir(cls._instance))
        # print(cls._instance.log)
        return cls._instance

    # def push_logs_to_buffer_periodically(self):
    #     while True:
    #         time.sleep(5)  # 每5秒推送一次日志到数据库
    #         self.push_logs_to_db()

    def push_logs_to_db_periodically(self):
        while True:
            time.sleep(5)  # 每5秒推送一次日志到数据库
            self.push_logs_to_db()

    def push_logs_to_db(self):
        # print(len(self.log_buffer))

        if len(self.log_buffer) > 0:
            print('日志服务器心跳事件检测到日志缓存，推送日志到数据库...缓存日志数量: %s' % len(self.log_buffer))
            conn = sqlite3.connect('game_data.db')
            c = conn.cursor()
            c.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_time TEXT NOT NULL,
                log_level TEXT NOT NULL,
                log_source TEXT NOT NULL,
                log_message TEXT NOT NULL,
                log_mark INTEGER DEFAULT 3
            )
            ''')
            # c.execute('CREATE TABLE IF NOT EXISTS logs (log_id INTEGER PRIMARY KEY AUTOINCREMENT, log_time TEXT, log_level TEXT, log_mark TEXT)')
            # c.execute('CREATE TABLE IF NOT EXISTS logs (time TEXT, level TEXT, source TEXT, message TEXT)')
            for log_record in self.log_buffer[:]:

                # c.execute('INSERT INTO logs VALUES (?, ?, ?, ?)', log_record)
                c.execute('INSERT INTO logs (log_time, log_level, log_source, log_message) VALUES (?, ?, ?, ?)', log_record)
                self.log_buffer.remove(log_record)

            conn.commit()
            conn.close()
            # self.log_buffer.clear()
        else:
            print('日志服务器心跳正常，无日志推送到数据库...')

    def log_to_db(self, log_record):
        self.log_buffer.append(log_record)

    def log(self, level, source, message):
        print('启动了这个函数log启动了这个函数log启动了这个函数log启动了这个函数log启动了这个函数log启动了这个函数log启动了这个函数log启动了这个函数log')
        log_record = (time.strftime('%Y-%m-%d %H:%M:%S'), level, source, message)
        self.log_to_db(log_record)
        self.logger.log(logging.getLevelName(level), message, extra={'source': source})

    @classmethod
    def get_logger(cls):
        # print('启动了这个函数get_logger')
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance.logger