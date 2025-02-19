# -*- coding: utf-8 -*-
import asyncio
import uuid
from pathlib import Path

from flask import Flask, render_template, request, jsonify

from auth import auth_login, require_login
from comfyui_proxy import run_task
from models import *
from movie import create_video
from oss_utils import upload_stream, upload_local
from tts import create_voice

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './'
app.config['ALLOWED_EXTENSIONS'] = {'jpeg', 'png', 'jpg'}

cache_task = {}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/login', methods=['POST', 'GET'])
def login():
    return auth_login()


@app.route('/', methods=['GET'])
@require_login
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
@require_login
def handle_upload():
    """上传图片接口"""
    try:
        if 'file' not in request.files:
            return '未找到文件部分'
        file = request.files['file']
        if file.filename == '':
            return api_response(False, message="没有选择文件", status_code=400)
        if file and allowed_file(file.filename):
            file = request.files['file']
            oss_sign_url = upload_stream(file.filename, file.stream)
            data = extract_features(oss_sign_url)
            return api_response(True, data={"featuresPrompt": data})
        else:
            return api_response(False, message="文件类型不支持", status_code=409)
    except Exception as e:
        return api_response(False, message=f"服务器内部错误: {str(e)}", status_code=500)


@app.route('/api/makeChapters', methods=['POST'])
@require_login
def handle_make_chapters():
    """制作章节"""
    try:
        data = request.json
        subject = data.get('subject', '')
        traits_string = data.get('traits', '')
        if not subject:
            return api_response(False, message="主题提示词参数不能为空", status_code=400)
        if not traits_string:
            return api_response(False, message="人物特征参数不能为空", status_code=400)
        task_id = str(uuid.uuid4())
        cache_task[task_id] = make_chapters(subject, traits_string)
        return api_response(True, data={"task_id": task_id})
    except Exception as e:
        return api_response(False, message=f"服务器内部错误: {str(e)}", status_code=500)


@app.route('/api/makeImageAndVoice/<string:task_id>/<string:voice>', methods=['GET'])
@require_login
def handle_make_image_voice(task_id, voice):
    """绘制图片和合成旁白"""
    try:
        data = cache_task[task_id]
        chapters = data['chapters']
        traits_string = data['traits_prompt_en']
        scene_description_en = {}
        description = {}
        for chapter in chapters:
            index = chapter['chapter'] - 1
            description[str(index)] = chapter['content']
            scene_description_en[str(index)] = chapter['scene_description_en']
        mkdir(task_id)

        # 异步处理插图生成和语音合成
        async def create_task():
            task_images = run_task(data, traits_string, task_id)
            task_voice = create_voice(description, task_id, voice)
            return await asyncio.gather(task_images, task_voice)

        images_oss_url, voice_oss_url = asyncio.run(create_task())
        data['images_oss_url'] = images_oss_url
        data['voice_oss_url'] = voice_oss_url
        cache_task[task_id] = data
        return api_response(True)
    except Exception as e:
        return api_response(False, message=f"服务器内部错误: {str(e)}", status_code=500)


@app.route('/api/makeVideo/<string:task_id>', methods=['GET'])
@require_login
def handle_make_video(task_id):
    """合成视频"""
    try:
        data = cache_task[task_id]
        # 合成视频
        video_path = create_video(task_id)
        video_oss_url = upload_local(f"{task_id}/{task_id}.pm4", video_path)
        data['video_oss_url'] = video_oss_url
        cache_task[task_id] = data
        return api_response(True, data=data)
    except Exception as e:
        return api_response(False, message=f"服务器内部错误: {str(e)}", status_code=500)


def mkdir(prompt_id):
    dirs = [Path(f'factory/{prompt_id}/{subdir}') for subdir in ['audios', 'images', 'subtitles', 'out']]
    for path in dirs:
        os.makedirs(path, exist_ok=True)


def api_response(status, message='', data=None, status_code=200):
    """
    构造API响应的辅助函数。

    :param status: 响应状态（布尔值或字符串：例如 True/False 或 'success', 'error'）
    :param message: 响应消息（可选）
    :param data: 响应数据（可选，默认为空字典）
    :param status_code: HTTP状态码（默认200）
    :return: JSON格式的响应和HTTP状态码
    """
    # 根据布尔值转换status为相应的字符串
    if isinstance(status, bool):
        status = 'success' if status else 'error'

    response = {
        'status': status,
        'message': message,
        'data': data if data is not None else {}
    }
    return jsonify(response), status_code


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9000)
