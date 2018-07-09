#-*-coding:utf-8-*-
import contextlib
import glob
import os
import MeCab
from gensim.models import word2vec
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',level=logging.INFO)

out = glob.glob('./run/result/wakati/*.csv')#出力結果のディレクトリのパスが入る

@contextlib.contextmanager
def scoped_chdir(dir):
    curdir = os.getcwd()
    os.chdir(dir)
    try: yield
    finally:os.chdir(curdir)

with scoped_chdir('./run/result/wakati'):
    os.makedirs('model',exist_ok=True)
for o in out:

    osp = o.split("/")
    #Word2Vecの学習に使用する分かち書き済みのテキストファイルの準備
    sentences = word2vec.Text8Corpus(o)
    
    #Word2Vecのインスタンス作成
    #size 出力するベクトルの次元数
    # min_count この数値よりも登場回数が少ない単語は無視する
    #window ひとつの単語に対してこの数値分だけ前後をチェックする
    model = word2vec.Word2Vec(sentences,size=200,min_count=10,window=15)

    #学習結果を出力する
    model.save(osp[4]+"_vec.model")


