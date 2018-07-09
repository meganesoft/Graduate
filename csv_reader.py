#coding: utf-8
import csv
import re

pattern = r'\n'
repatter = re.compile(pattern)

with open('kinoko.csv',encoding='utf-8') as fin:
    reader = csv.reader(fin)
    villains = [row for row in reader]

print(villains[0])