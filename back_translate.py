"""
@Time : 2021/4/614:50
@Auth : 周俊贤
@File ：back_translate.py
@DESCRIPTION: 采用回译的方法来实现文本的数据增强
"""

import jieba
import http.client
import hashlib
import urllib
import random
import json
import time
from utils.utils import write_samples
import os

def translate(q, src_lang, tgt_lang):
    """请求百度通用翻译API，详细请看 https://api.fanyi.baidu.com/doc/21

    :param q:
    :param src_lang:
    :param tgt_lang:
    :return:
    """
    appid = ''  # Fill in your AppID
    secretKey = ''  # Fill in your key

    httpClient = None
    myurl = '/api/trans/vip/translate'

    salt = random.randint(0, 4000)
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = '/api/trans/vip/translate' + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + src_lang + '&to=' + tgt_lang + '&salt=' + str(salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        # response is HTTPResponse object
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        return result

    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()

def back_translate(q, src_lang="zh", tgt_lang="en"):
    """

    :param q: 文本
    :param src_lang: 原始语言
    :param tgt_lang: 目前语言
    :return: 回译后的文本
    """
    en = translate(q, src_lang, tgt_lang)['trans_result'][0]['dst']
    time.sleep(1.5)
    target = translate(en, tgt_lang, src_lang)['trans_result'][0]['dst']
    time.sleep(1.5)

    return target

def translate_continue(sample_path, translate_path):
    """ 主函数，把原始数据文件里的每一条样本通过回译生成新的样本

    :param sample_path: 原始数据路径
    :param translate_path: 增强数据路径
    """
    if os.path.exists(translate_path):
        with open(translate_path, 'r+', encoding='utf8') as file:
            exit_len = len(list(file))
    else:
        with open(translate_path, 'w', encoding='utf8') as file:
            exit_len = 0

    translated = []
    count = 0
    with open(sample_path, 'r', encoding='utf8') as file:
        for line in file:
            count += 1
            print(count)
            if count <= exit_len:
                continue
            #
            line = back_translate(line.strip())
            translated.append(line)
            #  storage back_translate result
            print(count)
            write_samples(translated, translate_path, 'a')
            translated = []

if __name__ == '__main__':
    sample_path = './data/train.txt'
    translate_path = './data/translated.txt'
    translate_continue(sample_path, translate_path)
