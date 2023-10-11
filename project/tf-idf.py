# 使用python-embed版時要加這2行，才能import本地module
import sys, os
sys.path.append(os.path.dirname(__file__))


import re, math
from ckiptagger import WS, POS, NER, data_utils
from db import getData
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer



data= getData("youtube","SELECT videoContent,views,likes,dislikes FROM youtube WHERE category='美妝'")



# 文本清理，刪除 "【】"、"《》"、"「」" 等符號
collect_corpus = []
for row in data:
    clean_c = re.sub('[【】《》「」]', '', row[0])
    if len(clean_c) > 0:
        collect_corpus.append(clean_c)


# data_utils.download_data_gdown("./data/ckip/")
ws = WS('D:\desktopD\git\Page-Project-Kuo\Page-Project\Page-Project-KUO\crawler\ws_model')

print("-- ws start --")
# 執行斷詞
word_segment = ws(collect_corpus,
                  sentence_segmentation=True,
                  segment_delimiter_set={'?', '？', '!', '！', '。', '.', ',', '，', ';', ':', '、'})

print("-- ws finished --")


# 暫存成json (測試用) (不然前面斷詞每次都要跑20分鐘)
with open("data/word_segment.json", "w", encoding='utf-8') as f:
    import json
    json.dump(word_segment, f, indent=4)
# with open("data/word_segment.json", "r", encoding='utf-8') as f:
#     import json
#     word_segment= json.load(f)





articlesCounter= Counter()
# 獲取1篇文章的所有字詞Counter (ex: {"你好":2, ...})
for article in word_segment:
    contentGramFreqs= Counter(article)
    
    # 將Counter裡面每一個字的單位從次數轉為頻率(次數/總詞數)
    wordsNum= sum(contentGramFreqs.values())
    for item, count in contentGramFreqs.items():
        contentGramFreqs[item] /= wordsNum
    
    # 再加到總counter裡面
    articlesCounter+= contentGramFreqs



notRelate_data= getData("youtube","SELECT videoContent FROM youtube2")
notRelate_data= [row[0] for row in notRelate_data]

# 對每一個詞做idf
for word in articlesCounter:
    # 將Counter(所有文章的頻率總和)轉換為平均頻率
    articlesCounter[word] /= len(word_segment)
    # freq * log(相關和不相關的文章總數/ 出現文章數)
    articlesCounter[word] *= math.log(
            (1+len(notRelate_data))
            /(sum([1 for article in notRelate_data if word in article])+ 1)
        )
    # articlesCounter[word] *= math.log(
    #         (len(word_segment)+len(notRelate_data))
    #         /(sum([1 for article in notRelate_data if word in article])+ len(word_segment))
    #     )




# print出前50&後50的(測試用)
for i,m in enumerate(articlesCounter.most_common()):
    if i < 50:
        print(m[0], "\ttf-idf:", m[1])
    if i > len(articlesCounter)-50:
        print(m[0], "\ttf-idf:", m[1])
print("總詞數:", len(articlesCounter))

# 存成csv
import pandas as pd
df= pd.DataFrame([[''.join(words),articlesCounter[words]] for words in articlesCounter])
df= df.sort_values(by=[1], ascending=False)
df.to_csv("data/tf-idf.csv", index=False, header=False, encoding='utf-8')