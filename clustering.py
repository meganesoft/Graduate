#cording:utf-8
import re
import MeCab
import numpy as np
from sklearn.cluster import KMeans
from gensim import corpora, matutils


FILE_NAMEs = ["kinoko_4874055276_3097179103.csv",
			  "tweet.csv",
			 ]
WORDs	   = []

m = MeCab.Tagger("-d /usr/lib/mecab/dic/mecab-ipadic-neologd")

for FILE_NAME in FILE_NAMEs:
	MEISHI    = []
	f = open(FILE_NAME,"r")

	text=""
	for line in f:
		line = line.replace("\\n" , " ") #\nの除去
		line = re.sub(r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+" , " " , line)#URLの除去
		text+= line

	parsed = m.parse(text).replace("\t","")#分かち書きとタブの除去
	for line in parsed.split("\n"):
		if line.find("名詞,") > 0:
			if len(line.split("名詞,")[0]) == 1 or line.split("名詞,")[0].isdigit():#1文字の名詞と数字の除去
				continue
			MEISHI.append( line.split("名詞,")[0] )
	WORDs.append(MEISHI)

dictionary = corpora.Dictionary(WORDs)

#dictionary.filter_extremes(no_below=20, no_above=0.3)
# no_berow: 使われてる文章がno_berow個以下の単語無視
# no_above: 使われてる文章の割合がno_above以上の場合無視

dictionary.save_as_text('tweetdic.txt')

data = []
for WORD in WORDs:
	tmp   = dictionary.doc2bow(WORD)
	dense = list(matutils.corpus2dense([tmp], num_terms=len(dictionary)).T[0])
	data.append(dense)
print(data)

result = KMeans(n_clusters=2).fit_predict(data)
print(result)


#######
#http://qiita.com/yasunori/items/31a23eb259482e4824e2
#http://qiita.com/satzz/items/69beb439ed440d459585#bag-of-words%E3%82%92%E4%BD%9C%E3%82%8B
#http://qiita.com/satzz/items/a3a3986750c52fd360d0
#
#