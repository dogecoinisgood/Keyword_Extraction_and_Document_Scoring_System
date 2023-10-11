import os, sqlite3




db2_path= "data/data_not_relate.db"
db1_path= "data/data_relate.db"






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

cursor.execute('''CREATE TABLE IF NOT EXISTS youtube2(
        ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        link TEXT,
        company TEXT,
        videoContent TEXT
    );''')


for row in data2:
    title2,description2,link2,videoContent2= row
    
    cursor.execute(f"INSERT INTO youtube2 (title,description,link,videoContent) VALUES (?,?,?,?);", (title2, description2, description2, videoContent2))

conn.commit()
conn.close()


