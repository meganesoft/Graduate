# -*- coding:utf-8 -*-
import MeCab
#text = open('./result/result.csv','r')
#print(text)
nouns,verbs,adjs,advs = [],[],[],[]
nounswords,verbswords,adjswords,advswords = [],[],[],[]
nounspoint, verbspoint, adjspoint, advspoint = [], [], [], []

def analyze(hinsi, words, point):
    #品詞分解したwordと辞書のwordが一致するかチェック
    global score, number
    for i in hinsi:
        cnt = 0
        for j in words:
            if i == j:
                print (j, point[cnt])
                score += float(point[cnt])
                number += 1
                cnt += 1
def feel_analyze(tweet)   
 #単語感情極性対応表を読み込む
    f = open('pn_ja.dic','r')
    for line in f:
        line = line.rstrip()
        x = line.split(':')
        if abs(float(x[3]))>0:
                if x[2] == '名詞':
                    nounswords.append(x[0])
                    nounspoint.append(x[3])
                if x[2] == '動詞':
                    verbswords.append(x[0])
                    verbspoint.append(x[3])
                if x[2] == '形容詞':
                    adjswords.append(x[0])
                    adjspoint.append(x[3])
                if x[2] == '副詞':
                    advswords.append(x[0])
                    advspoint.append(x[3])
    f.close()
    #mecabで文章を品詞分解する
    tagger = MeCab.Tagger('-Ochasen')
    #nodetext = text.encode('utf-8')
    #node = tagger.parseToNode(nodetext)
    node = tagger.parseToNode(tweet)
    #node = tagger.parseToNode(text.encode('utf-8'))
    while node:
        if node.feature.split(",")[0] == '名詞':
            nouns.append(node.surface)
        if node.feature.split(",")[0] == '動詞':
            verbs.append(node.surface)
        if node.feature.split(",")[0] == '形容詞':
            adjs.append(node.surface)
        if node.feature.split(",")[0] == '副詞':
            advs.append(node.surface)
        node = node.next


    #辞書を使って感情分析する
    score = number = 0
    analyze(nouns,nounswords,nounspoint)
    analyze(verbs,verbswords,verbspoint)
    analyze(adjs,adjswords,adjspoint)
    analyze(advs,advswords,advspoint)
    if number > 0:
       #print (score/number)

    if score > 0:
        return True
    else:
        return False

