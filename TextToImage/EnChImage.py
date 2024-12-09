import re  # 正则表达式，解析网页
from random import *
import requests  # 请求网页
import traceback
import jieba
import jieba.posseg as jp
from gensim import corpora, models
import re
from translate import Translator
import os
import textwrap

# 定义最大字符数，确保每次查询不会超过限制
MAX_QUERY_LENGTH = 500

root = './blog'
# headers = {'user-agent': 'Mozilla/5.0'}  # 浏览器伪装，因为有的网站会反爬虫，通过该headers可以伪装成浏览器访问，否则user-agent中的代理信息为python
# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
headers = {'User-Agent': 'Mozilla/5.0 (Macintoosh; Intel Mac OS X 10_14_68) '
                         'AppleWebKit/538.36 (KHTML, like Gecko) Chrome/76.0.3904.97 Safari/537.36'}


def translate_english_to_chinese(text):
    # 创建一个翻译器实例，设置目标语言为中文
    translator = Translator(to_lang="zh")

    # 使用 textwrap.wrap 按字符长度分割文本，确保每段不超过 MAX_QUERY_LENGTH 字符
    chunks = textwrap.wrap(text, MAX_QUERY_LENGTH)

    # 翻译每个分块，并将结果拼接起来
    translated_chunks = [translator.translate(chunk) for chunk in chunks]

    # 将翻译后的结果拼接为一个完整的字符串
    translation = ' '.join(translated_chunks)
    return translation


# def download_picture(html):
#     pic_url = re.findall('"objURL":"(.*?)",', html, re.S)  # 找到符合正则规则的目标网站
#     num = len(pic_url)
#     # print("num-------------", num)
# 
#     sub_root = root
#     txt_path = sub_root + '/download_detail.txt'
# 
#     print('现在开始下载图片...')
# 
#     each = choice(pic_url)
#     a = '正在下载，图片地址为:' + str(each) + '\n'
#     print(a)
#     path = sub_root + '/1'
#     try:
#         if not os.path.exists(sub_root):
#             os.mkdir(sub_root)
#         if not os.path.exists(path):
#             pic = requests.get(each, headers=headers, timeout=10)
#             with open(path + '.jpg', 'wb') as f:
#                 f.write(pic.content)
#                 f.close()
#             with open(txt_path, 'a') as f:
#                 f.write(a)
#                 f.close()
#     except:
#         traceback.print_exc()
#         print('【错误】当前图片无法下载')


def get_stopword_list():
    stop_word_path = './TextToImage/KeywordExtraction/stop_words.txt'
    stopword_list = [sw.replace('\n', '') for sw in open(stop_word_path, encoding='UTF-8').readlines()]
    return stopword_list


def generate_img(inputWords):
    # 分词过滤条件
    jieba.load_userdict("./TextToImage/KeywordExtraction/userDict.txt")
    flags = ('n', 'nr', 'ns', 'nt')  # 词性，选取了名词、人名、地名、机构团体
    stopwords = get_stopword_list()

    inputWord = translate_english_to_chinese(inputWords)
    # 分词
    words_ls = []
    words = []
    for w in jp.cut(inputWord):
        if w.flag in flags and w.word not in stopwords and len(w.word) > 1:
            words.append(w.word)
    words_ls.append(words)

    # 构造词典
    dictionary = corpora.Dictionary(words_ls)
    # 基于词典，使【词】→【稀疏向量】，并将向量放入列表，形成【稀疏向量集】
    corpus = [dictionary.doc2bow(words) for words in words_ls]
    # lda模型，num_topics设置主题的个数
    lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=1)
    resWords = []

    # 打印所有主题，每个主题显示8个词
    for topic in lda.print_topics(num_words=8):
        # 正则表达式提取词语及其权重
        matches = re.findall(r'([\d\.]+)\*\"(.*?)\"', topic[1])
        # 提取的结果
        words = [match[1] for match in matches]
        result_string = "".join(words)
        resWords.append(result_string)

    # strWord = "".join(ana.tfidf(word, topK=8, allowPOS=('n', 'nr', 'ns', 'nt')))
    # print("TF-IDF提取到的关键词为：", strWord)

    strWord = resWords[0]
    # global root
    # root = root + strWord
    #
    # if not os.path.exists(root):
    #     os.mkdir(root)

    # 假设最多有100页,随机生成一个页面偏移量
    pageId = randint(0, 100)
    # print("pageId----------", pageId)

    # url = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=' + word + "&pn=" + \
    #       str(pageId) + "&gsm=?&ct=&ic=0&lm=-1&width=0&height=0"
    url = 'http://image.baidu.com/search/flip?tn=resultjson_com&ipn=rj&ct=201326592&fp=result&queryWord=' + strWord + \
          '&cl=2&lm=-1&ie=utf-8&oe=utf-8&st=-1&ic=0&word=' + strWord + '&face=0&istype=2nc=1&pn=' + str(
        pageId) + '&rn=1'

    # print("url-------------", url)

    proxies = {
        'http': None,
        'https': None
    }
    html = requests.get(url, headers=headers, proxies=proxies)
    # print(html.text)  # 打印网页源码
    return html.text
    # download_picture(html.text)
