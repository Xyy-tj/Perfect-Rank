import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.logger import Ranker_Logger
logger = Ranker_Logger.get_logger()

from functools import wraps
from flask import Flask, request, jsonify


# 授权装饰器
def require_authorize(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # 编写授权逻辑，可根据需要进行身份验证、权限检查等
        return func(*args, **kwargs)
    
        api_key = request.headers.get('Authorization')
        if api_key == 'Bearer tj-12345678':
            return func(*args, **kwargs)
        else:
            return jsonify({'message': 'Unauthorized Access.'}), 401

    return decorated_function