#*-coding:utf-8-*-
import contextlib
import glob
import os
import MeCab

out = glob.glob('./run/result/*.csv')#出力結果のディレクトリのパスが入る
root,ext = os.path.splitext('./run/result'+out[1])#拡張子判定をしたいファイルのパスを入れる

@contextlib.contextmanager
def scoped_chdir(dir):
	curdir = os.getcwd()
	os.chdir(dir)
	try: yield
	finally:os.chdir(curdir)

#print(root,ext)

if ext == ".csv":
	with scoped_chdir('./run/result'):
		os.makedirs('wakati',exist_ok=True)
	#os.chdir('./wakati')
	for o in out:
		f = open(o,"r")#ファイル読みこみ
		for line in f:
			ls = line.split(",")
			osp = o.split("/")
			with scoped_chdir('./run/result/wakati'):
				print(osp)#デバッグ用
				print(ls[0])#デバッグ用
				with open(osp[3]+"_wakati.txt","w") as file:
                                        tagger = MeCab.Tagger("-Owakati")
                                        result = tagger.parse(ls[0])
                                        file.write(result)
else:
	print("ミスってる")
