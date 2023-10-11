# ckiptagger: 中研院開發之繁體中文專用斷詞程式；功能與jieba類似

import os, re
from ckiptagger import WS, POS, NER
from db import getData
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


# ----------------------------------------------------------------------------------------------------------------------- #


corpus= getData("youtube","SELECT videoContent FROM youtube")

corpus= [row[0] for row in corpus][:330]  # [:N] 取用N篇文本


# 導入CKIPtagger 斷詞模型
ws = WS('D:\desktopD\git\Page-Project-Kuo\Page-Project\Page-Project-KUO\crawler\ws_model')

# 讀取文本（corpus）
# path = r'C:\Users\User\Desktop\cosmetic_1.txt'  # 測試單一一篇文本時使用此區塊
# with open(path, 'r', encoding='utf-8') as f :
#     corpus = f.readlines()

# 文本清理，刪除 "【】"、"《》"、"「」" 等符號
collect_corpus = []
for i in corpus:
    clean_c = re.sub('[【】《》「」]', '', i)
    if len(clean_c) > 0:
        collect_corpus.append(clean_c)

# 執行斷詞
word_segment = ws(collect_corpus,
                  sentence_segmentation=True,
                  segment_delimiter_set={'?', '？', '!', '！', '。', '.', ',', '，', ';', ':', '、'})

# ----------------------------------------------------------------------------------------------------------------------- #

#斷好的結果用「空白格（Space）」連接起來
cut_corpus = []
for i in word_segment:
    cut_corpus.append(' '.join(i))

for c in cut_corpus:
    # print (c)
    pass

# ----------------------------------------------------------------------------------------------------------------------- #



# 讀取stop-words.txt  # 此處為網友提供之個人stopwords詞庫
with open(r'D:\desktopD\git\Page-Project-Kuo\Page-Project\Page-Project-KUO\crawler\stop_words.txt', encoding='utf-8') as f:
    stop_word = f.read()

# 整理 stop-word
sw = stop_word.split('\n')

# ----------------------------------------------------------------------------------------------------------------------- #

text_cv = CountVectorizer(max_df=1.0, min_df=0.0, stop_words=sw)  # 某 term 出現在總文本的比率若超過 > 80% or < 50% 就剔除


td_matrix = text_cv.fit_transform(cut_corpus)

print(td_matrix.shape)
# result >> (12,7)  # 12個句子(文本)，共提出7個關鍵字 # example

print(text_cv.vocabulary_.keys())

# print(text_cv.vocabulary_)  # result >> {'xxx':N, 'xxx':M, ...}
# print(sorted(text_cv.vocabulary_.items(), key=lambda x:x[1], reverse=True))  # result >> [('xxx':M, 'xxx':N, ...)]降冪排序(非couont數)
# result >> dict_keys(['韓國瑜', '夫婦', '房產', '韓氏', '雲林', '韓辦', '貸款'])

# print(len(text_cv.vocabulary_.keys()))  # result >> 共提出幾個關鍵字數，數目
# result >> 7  # 儲存關鍵字的dictionary的長度(含有幾個元素)

# print(text_cv.vocabulary_)
# print(sorted(text_cv.vocabulary_.items(), key=lambda x:x[1], reverse=True))
# result >> dict_keys(['韓國瑜', '夫婦', '房產', '韓氏', '雲林', '韓辦', '貸款'])  # example

# print(len(text_cv.vocabulary_.keys()))
# result >> 7  # 儲存關鍵字的dictionary的長度(含有幾個元素)  # example



# # ----------------------------------------------------------------------------------------------------------------------- #
# 以下測試出現錯誤，待調整。潛在應用: 了解優質業配文，使用這個關鍵字的權重


# tfidf = TfidfTransformer()

# tfidf_matrix = tfidf.fit_transform(td_matrix)

# # print(td_matrix)

# tfidf.idf_
# result >> array([1.48550782, 1.48550782, 1.77318989, 1.77318989, 1.36772478, 1.61903921, 1.61903921]) 
        
# ----------------------------------------------------------------------------------------------------------------------- #


# import pandas as pd
# df = pd.DataFrame(tfidf_matrix.T.toarray(), index=text_cv.vocabulary_.keys())  
# print(df)


# # ----------------------------------------------------------------------------------------------------------------------- #
# # 計算每個關鍵字在data篇文本中的權重平均值
# keyword_row_mean = df.mean(axis=1)
# print(keyword_row_mean)

# ----------------------------------------------------------------------------------------------------------------------- #
# 將計算結果匯出為csv檔案

# Specify the name of the excel file
# file_name = 'keywords_extraction_output-1.csv'  # 自訂檔名

# # saving the excelsheet
# keyword_row_mean.to_csv(file_name)
# print('Extracxted keywords successfully exported into csv File!')




# 原範本:
# 【綜合報導】韓國瑜、李佳芬夫婦房產大公開！韓國瑜遭《壹週刊》連續踢爆購買總價逾7300萬元台北巿南港第1豪宅「日升月恆」，及3910萬元的內湖工業宅「峰哲」，「庶民」形象破功。為挽救選情，韓國瑜競選辦公室昨「直球對決」，公布韓氏夫婦自1993年至2019年所有房產交易紀錄，外界才知原來韓國瑜在台北、雲林兩地先後曾擁6筆房產，6買5賣，獲利553萬餘元，現僅剩雲林1戶自宅。
# 韓國瑜公布的資料中，《蘋果》發現韓國瑜的6筆房產中，在雙北的3戶豪宅，都是以購預售屋的方式投資，其中「東方明珠」完工後一年即賣出，大賺約1642萬元，而南港豪宅「日升月恆」在完工同年賣出，但因當時房市反轉，大賠428萬元，內湖「峰哲」則因工業宅賣出不易，才於去年底以3620萬元賣出，賠了290萬元。
# 豪宅風波延燒不止，國民黨總統參選人韓國瑜日前預告，將會開記者會一次說清楚。韓辦昨開記者會，公布韓氏夫婦房屋買賣紀錄。據韓辦公布資料，1993年、韓國瑜36歲時，展開了買屋置產之路。當時韓是立委，以700萬元價格在立法院附近的鎮江街，買了17餘坪的房子作為落腳處，當時沒有向銀行貸款，後來競選立委連任失利，韓決定回雲林，2001年賣出鎮江街住所。
# 2002年韓氏夫婦在雲林古坑斥資1220萬買下天下第一家建案，並向銀行貸款1000萬元。這戶房產就是遭《蘋果》獨家踢爆的違建農舍。
# 到了2007年時，韓氏夫婦在新北巿板橋區「東方明珠」建案，購買總價4177萬元、117.89坪的豪宅。韓辦說，頭期款約800萬元，是韓氏夫婦的積蓄，再加上部分家中長輩的資助。2010年因為考慮移居台北市出售，因房價起飛，轉手賺了1642萬9129元。
# 韓國瑜房產中，除了「東方明珠」賺錢之外，其他都賠錢。2010年，韓氏夫婦先到台北巿內湖區以總價3910萬元，買下知名建案「峰哲」67.57坪房屋一戶。韓辦說，購屋後發現附近交通並不如預期方便，且屋內使用空間不足，隔年透過仲介介紹，購入南港「無雙社區」（後改名日升月恆），總價7378萬元。
# 最多同時擁4間房 韓辦：庶民不等於貧民
# 韓辦說，但因為貸款負擔實在太重，評估未來恐怕負擔不起，因此趕在「日升月恆」交屋前，2015年就以賠本價格6950萬元轉手。2018年，韓國瑜南下高雄發展，出售內湖「峰哲」房產，虧損290萬元。
# 韓辦說，韓國瑜在雙北買房，都是為了自用，以「換屋」方式進行交易。孫大千說，目前韓國瑜夫婦只剩下雲林唯一自住的房子，這些過去買賣的房產如果被貼上「炒房」的標籤，那全國買賣房子的民眾也是炒房嗎？另韓辦也表示韓國瑜大女兒韓冰名下，也有一戶旁系長輩所贈與的加拿大地下室26.6坪住宅。
# 韓國瑜競選辦公室副執行長、藍委許淑華強調：「庶民不等於貧民，每個庶民都買得起房子。」副執行長孫大千也說，「庶民不代表沒有經濟能力」，呼籲總統蔡英文也公布房產資料。對此，蔡英文競選辦公室回應，蔡所有房產早已在2015年信託，網路都查得到；韓在4年間可向銀行貸款9300萬元買賣房屋，遠非多數國民能力所及，是否符合庶民說法社會自有公評。
# 《蘋果》比對韓國瑜的說法，發現他從2015年2月到12月期間，同時擁有「日升月恆」、「峰哲」、雲林農舍、斗六比佛利莊園4間房舍。
# 不具名仲介認為，韓氏夫婦包括「東方明珠」、「日升月恆」都持有僅3到4年，加上不到30年累積多筆交易，的確有投資意味，但還不到投機客程度。但引人注意的是，韓國瑜36歲時，能夠以不到千萬元價格買下北市蛋黃區大樓，台灣房屋智庫經理陳炳辰表示，該地段位置不差，鄰近博愛特區、台北車站，換算現在房價高達1500萬元，若是在沒有貸款的情況下購買，資產實力還不錯。
