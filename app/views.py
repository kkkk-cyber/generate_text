import os
from app.model.commentMain.mergeHot import gen_comment
from app.model.commentMain.mergeHot import merge_event
from flask import (request,url_for)
from app import app
from flask import render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from generate import generate
import random

#渲染前端界面
@app.route('/blog_generate', methods=['GET'])
def blogGenerate():
    generated_blog = "这是一个生成的博文内容。"
    return render_template('./blogGenerate/blogGenerate.html', generated_text=generated_blog)
@app.route('/get_portraits', methods=['GET'])
def get_portraits():
    portraits = Portrait.query.all()
    portrait_list = [{'nikename': portrait.nikename} for portrait in portraits]  # 获取ID和名称
    return jsonify(portrait_list)
 
# 接收前端请求并返回生成文本的路由
@app.route('/generate_text', methods=['POST'])
def generate_text():
    # 获取前端传递的 JSON 数据
    data = request.get_json()
    print(data)
    generation_type = data.get('generation_type')
    emotion = data.get('emotion')
    theme = data.get('theme')
    user = data.get('user')
    print(user)

    if generation_type == 1:
        # 纯文本生成逻辑
        print("纯文本生成逻辑")
        generated_text = generate(img=1,user=user, topic=theme,emtion=emotion)
        return jsonify({'generated_text': generated_text, 'generated_image': None})
    elif generation_type == 2:
        # 图文生成逻辑
        generated_text= generate(img=2,user=user, topic=theme,emtion=emotion)
        generated_image = url_for('static', filename='images/img.jpg')  # 模拟生成的图片路径
        return jsonify({'generated_text': generated_text, 'generated_image': generated_image})
    else:
        return jsonify({'generated_text': '无效的生成类型', 'generated_image': None})
