import os, sqlite3




# copy db2的資料，進到db1
db1_path= "data/data_not_relate.db"
db2_path= "data/data_not_relate5.db"




base_path= os.path.abspath(os.path.dirname(__file__))



# 取得db2的資料
conn = sqlite3.connect(os.path.join(base_path,db2_path))
cursor= conn.cursor()
result= cursor.execute("SELECT title,description,link,videoContent FROM youtube")
data2= result.fetchall()
# conn.close()

# insert 進入db1
conn = sqlite3.connect(os.path.join(base_path,db1_path))
cursor= conn.cursor()

for row in data2:
    title2,description2,link2,videoContent2= row
    link2= link2.replace("'", "''")
    videoContent2= (videoContent2 or "").replace("'", "''")
    result= cursor.execute(f"SELECT id,link,videoContent FROM youtube WHERE link='{link2}';").fetchone()
    # 如果db1根本沒有這一筆資料，就從db2插入
    if not result:
        title2= title2.replace("'", "''")
        description2= description2.replace("'", "''")
        cursor.execute(f"INSERT INTO youtube (title,description,link,videoContent) VALUES ('{title2}','{description2}','{link2}','{videoContent2}');")
   
    else:
        id1,link1,videoContent1= result
        # 如果已經有這筆資料，若db1的videoContent為空，則從db2抓取
        if not videoContent1:
            cursor.execute(f"UPDATE youtube SET videoContent='{videoContent2}' WHERE link='{link2}';")
conn.commit()
conn.close()


