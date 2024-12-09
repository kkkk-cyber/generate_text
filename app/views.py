import os
from app.model.commentMain.mergeHot import gen_comment
from app.model.commentMain.mergeHot import merge_event
from flask import (request,url_for)
from app import app
from flask import render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from generate import generate
import random




#孔超娜 博文生成接口


#渲染前端界面
@app.route('/blog_generate', methods=['GET'])
def blogGenerate():
    generated_blog = "这是一个生成的博文内容。"
    return render_template('./blogGenerate/blogGenerate.html', generated_text=generated_blog)
#获取数据库中人物名，在前端展示
@app.route('/get_portraits', methods=['GET'])
def get_portraits():
    # 查询所有人物画像
    portraits = Portrait.query.all()
    portrait_list = [{'nikename': portrait.nikename} for portrait in portraits]  # 获取ID和名称

    # 返回JSON格式的用户数据
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










# 渲染评论生成页面
@app.route('/comment_generate', methods=['GET'])
def commentGenerate():
    return render_template('./commentGenerate/commentGenerate.html')


# 爬取热点新闻接口
@app.route('/fetch_hot_news', methods=['GET'])
def fetch_hot_news():
    # 这里可以实现爬虫逻辑来获取实时的热点新闻
    # 目前是模拟热点新闻
    num = 20
    # https://weibo.com/hot/search，cookie要及时更换
    cookie = "_s_tentry=passport.weibo.com; Apache=5356384594706.857.1732158290069; SINAGLOBAL=5356384594706.857.1732158290069; ULV=1732158290073:1:1:1:5356384594706.857.1732158290069:; XSRF-TOKEN=vqdI8EGm_Pgfbu1ln7L5AdK5; SCF=ApCWAFu5yJO5cpd1D4-YBSJoVH02Yi5t3eBtcOFJZSXZlQjBaMZl6AJd5-mUDeO1wN1sKEfKMG414D9fXt6m2gs.; SUB=_2A25KOtYUDeRhGeFH6FoV8ibKzDiIHXVpNlfcrDV8PUNbmtANLW3MkW9Ne0Aw6piIB3wnFtQsGQnUjWCSdecK4LoW; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWMm3Tr_kFV-IHzgH.qfOz25NHD95QN1KeRShzRSoMXWs4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNS0.01hBE1hqNS5tt; ALF=02_1734751044; WBPSESS=Dt2hbAUaXfkVprjyrAZT_CLC_xNFOh_gPaNKI3YVKGRUqr42n6g6MTugOsZawkLxNVCKh6Lxt1fP30GDrt6VmsGTf1zmTltOmGv4qZCM0xL92nJztTIzWOMOoJ9k5nIPesyG0_bRLrlCq3xi18KS3dkogkudKo_r29DMGnbz4BRHW6It5vT7QX-C4BmdN1-Zr_1fnJQNxw-yczartljVCg=="
    results = merge_event(num, cookie)
    # 将每个子列表转换为所需的格式
    formatted_results = [
        [f"{i + 1}. {sublist[0]} {sublist[1]} 链接：{sublist[2]} 内容：{sublist[3]}"] for i, sublist in enumerate(results)
    ]
    formatted_results.append([])
    formatted_results.append(["数据已保存到 weibo_hot_search.xlsx"])

    # 输出结果
    return jsonify({'hot_news': formatted_results})


# 生成评论接口
@app.route('/generate_comment', methods=['GET'])
def generate_comment():
    # 生成一个静态评论
    # static_comment = "这真是一个非常有趣的热点，大家对此议论纷纷，值得关注！"

    num = 2
    # https://weibo.com/hot/search，即使更换
    cookie = "_s_tentry=passport.weibo.com; Apache=5356384594706.857.1732158290069; SINAGLOBAL=5356384594706.857.1732158290069; ULV=1732158290073:1:1:1:5356384594706.857.1732158290069:; XSRF-TOKEN=vqdI8EGm_Pgfbu1ln7L5AdK5; SCF=ApCWAFu5yJO5cpd1D4-YBSJoVH02Yi5t3eBtcOFJZSXZlQjBaMZl6AJd5-mUDeO1wN1sKEfKMG414D9fXt6m2gs.; SUB=_2A25KOtYUDeRhGeFH6FoV8ibKzDiIHXVpNlfcrDV8PUNbmtANLW3MkW9Ne0Aw6piIB3wnFtQsGQnUjWCSdecK4LoW; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWMm3Tr_kFV-IHzgH.qfOz25NHD95QN1KeRShzRSoMXWs4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNS0.01hBE1hqNS5tt; ALF=02_1734751044; WBPSESS=Dt2hbAUaXfkVprjyrAZT_CLC_xNFOh_gPaNKI3YVKGRUqr42n6g6MTugOsZawkLxNVCKh6Lxt1fP30GDrt6VmsGTf1zmTltOmGv4qZCM0xL92nJztTIzWOMOoJ9k5nIPesyG0_bRLrlCq3xi18KS3dkogkudKo_r29DMGnbz4BRHW6It5vT7QX-C4BmdN1-Zr_1fnJQNxw-yczartljVCg=="
    res = gen_comment(num, cookie)
    print(res)
    # 将每个子列表转换为所需的格式
    for_results = [
        [f"{i + 1}. {sublist[1]}"] for i, sublist in enumerate(res)
    ]
    # 返回生成的评论
    return jsonify({'comment': for_results})


