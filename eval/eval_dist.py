import argparse
import json
import logging
import os
import nltk
from tqdm import tqdm
from collections import defaultdict
from functools import partial
import multiprocessing as mp
from collections import Counter
def _norm(x):
    return " ".join(x.strip().split())  # 去除多余空格并标准化


def tokenize(x):
    tokens = nltk.word_tokenize(_norm(x))  # 分词
    return tokens


def calculate_distinct(generation):
    # 对单个 generation 文本进行分词
    tokenized_generation = tokenize(generation)

    lengths = len(tokenized_generation)  # 文本长度
    distinct = []

    # 计算 n-gram（1-gram, 2-gram, 3-gram）
    for n in range(1, 4):
        ngrams = list(zip(*[tokenized_generation[i:] for i in range(n)]))  # 提取 n-gram
        ngrams_count = Counter(ngrams)  # 统计 n-gram 频次
        if lengths > 0:
            distinct.append(len(ngrams_count) / lengths)  # 计算 distinct 比例
        else:
            distinct.append(0)  # 防止除以 0

    return distinct


def evaluate(args):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    pool = mp.Pool(mp.cpu_count() * 2)  # 创建多进程池

    for infer_data_path in args.infer_data_paths:
        generation_file = infer_data_path + '/gen.json'

        # 读取生成文件
        generations = [json.loads(e)['generation'] for e in open(generation_file)]

        # 通过并行计算 distinct
        distinct = [e for e in pool.imap(calculate_distinct, tqdm(generations, dynamic_ncols=True, total=len(generations)))]

        # 将 distinct 结果写入文件
        with open(infer_data_path + '/dist_list.txt', 'w') as f:
            for d in distinct:
                f.write(json.dumps(d) + '\n')


def main():
    #########################################################################
    # Prepare Parser
    ##########################################################################

    parser = argparse.ArgumentParser()
    parser.add_argument('--context_file', type=str, required=True)
    parser.add_argument('--infer_data_paths', type=str, nargs='+')

    args = parser.parse_args()
    evaluate(args)


if __name__ == '__main__':
    main()