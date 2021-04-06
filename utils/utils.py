"""
@Time : 2021/4/615:24
@Auth : 周俊贤
@File ：utils.py
@DESCRIPTION:

"""

def read_samples(filename):
    """读取文件

    :param filename:
    :return:
    """
    samples = []
    with open(filename, 'r', encoding='utf8') as file:
        for line in file:
            samples.append(line.strip())
    return samples

def write_samples(samples, file_path, opt='w'):
    """写入文件

    :param samples:
    :param file_path:
    :param opt:
    """
    with open(file_path, opt, encoding='utf8') as file:
        for line in samples:
            file.write(line)
            file.write('\n')

def isChinese(word):
    """是否为中文字符

    :param word:
    :return:
    """
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False