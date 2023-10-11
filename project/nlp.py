# 使用python-embed版時要加這2行
import sys, os, time, re
sys.path.append(os.path.dirname(__file__))

import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from db import *
from db import getData



newArtical= '''
粉底液是彩妝界的不可或缺之物，而今我們要向大家介紹一款絕對值得擁有的粉底液。這個產品來自一個知名的品牌，以其高品質的彩妝產品而聞名，絕對不會讓你失望。
首先，讓我們談談這款粉底液的色號。它提供了多種不同的色號選擇，可以滿足各種不同膚色的需要，無論你是白皙的膚色還是深色的膚色，都能找到合適的選擇。
這款粉底液的質地非常柔滑，容易推開，而且上妝後能呈現出自然的霧面光澤。這種光澤讓你的皮膚看起來更加漂亮，不會有過於油膩的感覺。此外，它的包裝也非常精緻，絕對是你化妝包的一大亮點。
不僅如此，這款粉底液的持久性也非常優秀，讓你整天都能保持好看的底妝，不需要經常修補。它適用於各種皮膚類型，不管你是乾性皮膚還是油性皮膚，都能夠輕鬆搭配。
總結來說，這款粉底液絕對是一款值得推薦的產品。它不僅能讓你的皮膚看起來自然漂亮，還能夠保持長時間的好看效果。無論你是新手還是彩妝達人，這款粉底液都會是你化妝必備的好用產品。不要錯過機會，嘗試一下這個讓你擁有完美底妝的粉底液吧！
'''


if os.path.exists("data/sentence-transformers/paraphrase-multilingual-mpnet-base-v2"):
    model = SentenceTransformer('data/sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
else:
    model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    model.save("data/sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

# 中文測試
# wordpairs = [['老師', '教師', '泰國'], 
#              ['商品', '貨物', '跑步'],
#              ['商品', '商品', '產品'],
#              ['哈囉你好嗎','珍重再見','期待再相逢']
#             ]
# for wordpair in wordpairs:
#     embeddings = model.encode(wordpair)
#     print(wordpair[0], 'vs',  wordpair[1], 'distance =', util.pytorch_cos_sim(embeddings[0], embeddings[1]))
#     print(wordpair[0], 'vs',  wordpair[2], 'distance =', util.pytorch_cos_sim(embeddings[0], embeddings[2]))
#     print(wordpair[1], 'vs',  wordpair[2], 'distance =', util.pytorch_cos_sim(embeddings[1], embeddings[2]))

data= getData("youtube", "SELECT videoContent,views,likes,dislikes FROM youtube")

#((likes-dislikes)/views)  data做排序後小->大改成大->小
data= sorted(data, key=lambda x:(x[2]-x[3])/x[1], reverse=True)

# for row in data[:50]:
#     print(row[0][:15], row[1], row[2], row[3], (row[2]-row[3])/row[1], sep='\t')


# data= [row[0] or '' for row in data][:30]
#取第30~330
data2 = data[31:330]
#取第1~30
data= data[:30]

# sentence_embeddings = model.encode(data, show_progress_bar=True)
#生成文章和文章做embedding
embeddings = model.encode([row[0] for row in data]+[newArtical])
embeddings2 = model.encode([row[0] for row in data2]+[newArtical])

diss= []
for i,row in enumerate(data):
    diss.append(util.pytorch_cos_sim(embeddings[i], embeddings[-1]))
    #取前10個字後觀看有哪些文章
    print(i, row[0][:10], diss[-1], sep='\t')
# diss= [util.pytorch_cos_sim(embeddings[i], embeddings[-1]) for i,row in enumerate(data)]

#diss由大到小排序後放入diss2[:30]
diss2=sorted(diss, reverse=True)
#取相似度Top10
diss2= diss2[:10]
#加總平均
diss2= sum(diss2)/len(diss2)

#data[31:300]
diss3=[util.pytorch_cos_sim(embeddings2[i], embeddings2[-1]) for i,row in enumerate(data2)]
#加總平均
diss3=sum(diss3)/len(diss3)

print(diss2,diss3)