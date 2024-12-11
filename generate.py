import pymysql
import torch
import json
import re
import argparse
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, HfArgumentParser, GenerationConfig
from peft import PeftModel
from typing import Union
import queue
import random
import requests  
import traceback
import jieba.analyse as ana
import jieba
import jieba.posseg as jp
from gensim import corpora, models
from generate_text.generate_llama3 import generate_text
from TextToImage.EnChImage import generate_img
root_path = "./text"
def create_directory_and_file(user_id, topic, emotion):
    # 定义目录名称
    directory_name = f"user_{user_id}"
    # 获取当前目录并创建用户目录路径
    user_directory = os.path.join(root_path, directory_name)

    # 创建目录
    if not os.path.exists(user_directory):
        os.mkdir(user_directory)
        print(f"Directory '{directory_name}' created successfully.")
    else:
        print(f"Directory '{directory_name}' already exists.")

    topic_directory_name = f"topic_{topic}-emotion_{emotion}"
    topic_directory = os.path.join(user_directory, topic_directory_name)
    # 创建子目录
    if not os.path.exists(topic_directory):
        os.mkdir(topic_directory)
        print(f"Directory '{topic_directory_name}' created successfully.")
    else:
        print(f"Directory '{topic_directory_name}' already exists.")

    print(topic_directory)
    return topic_directory

def download_picture(html,file_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintoosh; Intel Mac OS X 10_14_68) '
                             'AppleWebKit/538.36 (KHTML, like Gecko) Chrome/76.0.3904.97 Safari/537.36'}
    pic_url = re.findall('"objURL":"(.*?)",', html, re.S)  # 找到符合正则规则的目标网站
    num = len(pic_url)

    txt_path = file_path + '/download_detail.txt'
    print('现在开始下载图片...')

    each = random.choice(pic_url)
    a = '正在下载，图片地址为:' + str(each) + '\n'
    # print(a)
    path = file_path + '/image'
    try:
        if not os.path.exists(path):
            pic = requests.get(each, headers=headers, timeout=10)
            with open(path + '.jpg', 'wb') as f:
                f.write(pic.content)
                f.close()
            with open(txt_path, 'a') as f:
                f.write(a)
                f.close()
    except:
        traceback.print_exc()
        print('【错误】当前图片无法下载')

def get_input(nikename,topic,emtion):
    #读取数据库得到用户信息
    db = pymysql.connect(
        host="host"
        , user="root"
        , passwd="123456"
        , database="db"
        , port=port
    )

    # 创建游标并执行查询
    cursor = db.cursor()
    columns = ["job_title", "hobbies"]  # 要查询的列名列表
    columns_str = ", ".join(columns)  # 将列名组合成字符串
    # SQL 查询，查找特定元素
    query = f"SELECT {columns_str} FROM person_output WHERE nikename = %s"
    cursor.execute(query, (nikename,))
    # 获取查询结果
    result = cursor.fetchone()

    job = result[0].strip()  
    hobbies = result[1].strip() 

    hobby_list = hobbies.split(",") 
    hobby_list = [h.replace('and', '').strip() for h in hobby_list]
    print(hobby_list)
    target_hobby = random.choice(hobby_list)
    # input = f'[job:{job};hobby:{target_hobby};topic:{topic};emotion:{emtion}]'
    input = f'[job:marketing manager;hobby:playing guitar;topic:Health;emotion:Anxiety]'
    print(input)
    return input

def main(img,user,topic,emtion,style):
    # 根据参数调用不同的函数
    input = get_input(user, topic, emtion)
    text = generate_blog(input, style)
    direction_path = create_directory_and_file(user, topic, emtion)
    file_name = f"text.txt"
    file_path = os.path.join(direction_path, file_name)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)

    if img:
        html = generate_img(text)
        download_picture(html, direction_path)
        print(f"image written and saved to blog")

main(img=False,user="user_name", topic="Hometown",emtion="Pride",style="xxx Style")  # 将会生成文本 

