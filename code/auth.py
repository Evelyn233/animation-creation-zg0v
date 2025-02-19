# -*- coding: utf-8 -*-
from flask import request, jsonify, redirect, make_response, url_for, render_template
import jwt
import datetime
import os
import hashlib


def get_md5(input_string):
    """
    计算输入字符串的MD5哈希值。
    """
    hash_object = hashlib.md5()
    hash_object.update(input_string.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    return hex_dig


def validate_token(token):
    """
    验证JWT令牌的有效性。
    """
    secret_key = get_md5(os.getenv('USER_PASSWORD'))
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        return True
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.DecodeError) as e:
        return False


def generate_token(user_id, secret_key, expires_in_minutes=24 * 60):
    """
    生成JWT令牌。
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes),
    }

    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def require_login(f):
    """
    检查用户是否已登录的装饰器。
    """

    def wrapper(*args, **kwargs):
        if os.getenv('ENABLE_LOGIN', 'false').lower() == 'true':
            token = request.cookies.get('auth_token')
            if not (token and validate_token(token)):
                if request.path.startswith('/api/'):
                    response = make_response(jsonify({'error': 'Unauthorized'}), 401)
                    return response
                else:
                    return redirect(url_for('login'))
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


def auth_login():
    """
    处理登录请求。
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not (username == os.getenv('USER_NAME') and get_md5(os.getenv('USER_PASSWORD')) == password):
            return jsonify({"msg": "Invalid credentials"}), 401
        access_token = generate_token(username, get_md5(os.getenv('USER_PASSWORD')))
        response = redirect(url_for('index'))
        response.set_cookie('auth_token', access_token, max_age=60 * 60 * 24 * 365)
        return response
    return render_template('login.html')
