"""
@Time : 2021/4/615:44
@Auth : 周俊贤
@File ：embed_replace.py
@DESCRIPTION:

"""
import os
import jieba
import numpy as np

from gensim.models import KeyedVectors, TfidfModel
from gensim.corpora import Dictionary
from utils.utils import read_samples, write_samples, isChinese
from gensim import matutils
from itertools import islice

class EmbedReplace():
    def __init__(self, sample_path, wv_path):
        self.samples = read_samples(sample_path)
        self.samples = [list(jieba.cut(sample)) for sample in self.samples]
        self.wv = KeyedVectors.load_word2vec_format(wv_path, binary=False)

        if os.path.exists('./tfidf_word2vec/tfidf.model'):
            self.tfidf_model = TfidfModel.load('tfidf_word2vec/tfidf.model')
            self.dct = Dictionary.load('tfidf_word2vec/tfidf.dict')
            self.corpus = [self.dct.doc2bow(doc) for doc in self.samples]
        else:
            self.dct = Dictionary(self.samples)
            self.corpus = [self.dct.doc2bow(doc) for doc in self.samples]
            self.tfidf_model = TfidfModel(self.corpus)
            self.dct.save('./tfidf_word2vec/tfidf.dict')
            self.tfidf_model.save('./tfidf_word2vec/tfidf.model')
            self.vocab_size = len(self.dct.token2id)

    def vectorize(self, docs, vocab_size):

        return matutils.corpus2dense(docs, vocab_size)

    def extract_keywords(self, dct, tfidf, threshold=0.2, topk=5):
        """ 提取关键词

        :param dct (Dictionary): gensim.corpora.Dictionary
        :param tfidf (list):
        :param threshold: tfidf的临界值
        :param topk: 前 topk 个关键词
        :return: 返回的关键词列表
        """
        tfidf = sorted(tfidf, key=lambda x: x[1], reverse=True)

        return list(islice([dct[w] for w, score in tfidf if score > threshold], topk))

    def replace(self, sample, doc):
        """用wordvector的近义词来替换，并避开关键词

        :param sample (list): reference token list
        :param doc (list): A reference represented by a word bag model
        :return: 新的文本
        """
        keywords = self.extract_keywords(self.dct, self.tfidf_model[doc])
        #
        num = int(len(sample) * 0.3)
        new_tokens = sample.copy()
        indexes = np.random.choice(len(sample), num)
        for index in indexes:
            token = sample[index]
            if isChinese(token) and token not in keywords and token in self.wv:
                new_tokens[index] = self.wv.most_similar(positive=token, negative=None, topn=1)[0][0]

        return ''.join(new_tokens)

    def generate_samples(self, write_path):
        """得到用word2vector词表增强后的数据

        :param write_path:
        """
        replaced = []
        for sample, doc in zip(self.samples, self.corpus):
            replaced.append(self.replace(sample, doc))
            write_samples(replaced, write_path, 'a')

if __name__ == '__main__':
    sample_path = './data/train.txt'
    wv_path = './tfidf_word2vec/sgns.weibo.word'
    replacer = EmbedReplace(sample_path, wv_path)
    replacer.generate_samples('./data/replaced.txt')
