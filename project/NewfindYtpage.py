# 使用python-embed版時要加這2行
import sys, os, time, re
sys.path.append(os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from db import *
# from db import updateCols



# 新增欄位
# updateCols("youtube", {"channel_name":"TEXT", "channel_ID":"TEXT", "subscribers":"INTEGER", "views":"INTEGER", "likes":"INTEGER", "dislikes":"INTEGER"})



keywords= "美食 健身 網球 汽車 .*"
# 最少要多少筆搜尋結果(&搜尋的時候的最大捲動次數)
firstSearchResult= 100
# 最大關聯層數(設1:只抓搜尋結果，不抓關聯影片)
relatedStack= 100


service = Service(executable_path=os.path.abspath(os.path.dirname(__file__)+"/data/geckodriver.exe"), log_path="NUL")
options = Options()

# 不跳實際的瀏覽器視窗出來(減少消耗無謂的效能)
# options.add_argument("--headless")
# 禁用通知
options.add_argument("--disable-notifications")
# 安裝return youtube dislike插件(chrome)
# options.add_extension(os.path.abspath(os.path.dirname(__file__)+'data/return dislike/return_dislike_chrome.crx'))


firefox= webdriver.Firefox(service=service, options=options)
# 隱含等待: 等待網頁載入完成後，再執行下面的程式，且只需設定一次，下面再有仔入網頁的動作時，無須再次設定，也會等待(最多10秒)網頁在入後再執行
firefox.implicitly_wait(5)

# 安裝return youtube dislike插件(firefox)
firefox.install_addon(os.path.abspath(os.path.dirname(__file__)+"/data/return dislike/return_dislike.xpi"), temporary=True)
# 安裝插件完後，從插件的分頁跳回原本的分頁
if len(firefox.window_handles) > 1:
    for i,window in enumerate(firefox.window_handles):
        if i != 0:
            firefox.switch_to.window(window_name=window)
            firefox.close()
    firefox.switch_to.window(window_name=firefox.window_handles[0])



firefox.get(f"https://www.youtube.com/results?search_query={keywords}")

# 從搜尋結果獲取第一批連結
def getFirstLinks():
    # 等到所有<ytd-video-renderer>元素載入
    firstLinks= WebDriverWait(firefox, 5).until(EC.presence_of_all_elements_located((By.TAG_NAME, "ytd-video-renderer")))
    # 尋找所有<ytd-video-renderer>中，所有的<a id="thumbnail">元素，並取得這些元素中的連結內容
    firstLinks= [firstLink.find_element(By.CSS_SELECTOR,"a#thumbnail").get_attribute("href") for firstLink in firstLinks]
    # 篩選掉連結不符合要求的
    firstLinks= [firstLink for firstLink in firstLinks if firstLink!=None and (firstLink.startswith("https://www.youtube.com/watch?") or firstLink.startswith("/watch?"))]
    return firstLinks

firstLinks= getFirstLinks()

# 如果第一批連結的數量少於100(firstSearchResult設定的數字)，則往下捲動，載入更連結後再重新拿一次第一批連結，最多捲動100(firstSearchResult設定的數字)次
for i in range(firstSearchResult):
    if len(firstLinks) >= firstSearchResult:
        break
    body= WebDriverWait(firefox, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-app")))
    firefox.execute_script("window.scrollTo(0,document.querySelector('ytd-app').scrollHeight)")
    firstLinks= getFirstLinks()
    # 如果頁面已經捲到底的話，按下"更多"或中斷迴圈
    soup= BeautifulSoup(firefox.page_source, "html.parser")
    results= soup.find_all("yt-formatted-string", {"id":"message"})
    if results:
        if results[0].get_text() == "沒有其他結果":
            break
    print(" 捲動次數:", i+1, "次, 共有", len(firstLinks), end="個連結\r")
print()



# 候選連結名單: 跑過的。以及已經抓到，但還沒跑的連結。避免一直跑重複的網頁
candidates= []+ firstLinks

def findRelated(href ,num:int):
    # 篩選掉含有時間戳和播放清單的部分
    href= href.split("&t=")[0].split("&list=")[0]
    
    if num>0:
        try:
            # firefox.get(href)
            # 改成開新分頁，看完再關掉這個分頁，以節省記憶體
            firefox.execute_script(f"window.open('{href}');")
            windowName= firefox.window_handles[-1]
            firefox.switch_to.window(window_name=windowName)
            
            
            # 確認title載入後，獲取title的文字
            title= WebDriverWait(firefox, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.style-scope.ytd-watch-metadata")))
            title= title.get_attribute("textContent").strip() or ""
            
            # 確認description載入後，獲取description的文字
            # 點擊展開說明欄，以獲取說明欄內完整文字
            WebDriverWait(firefox, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "tp-yt-paper-button#expand"))).click()
            description= WebDriverWait(firefox, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-text-inline-expander")))
            # tag是yt-attributed-string的元素有2個，一個有id="attributed-snippet-text"，是剛進入時的說明欄。另一個沒有id，是展開後的說明欄
            description= description.find_element(By.CSS_SELECTOR, "yt-attributed-string:not(#attributed-snippet-text)")
            description= description.get_attribute("textContent").strip() or ""
            
            # 抓取like
            likes= WebDriverWait(firefox, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[2]/div/div/ytd-menu-renderer/div[1]/ytd-segmented-like-dislike-button-renderer/yt-smartimation/div/div[1]/ytd-toggle-button-renderer/yt-button-shape/button/div[2]")))
            likes= likes.text
            if "萬" in likes: likes= int(float(likes.replace("萬",""))*10000)
            elif "億" in likes: likes= int(float(likes.replace("億",""))*100000000)
            elif likes.isdigit(): likes= int(likes)
            else: likes= 0
            # dislikes(要wait載入插件)
            dislikes= WebDriverWait(firefox, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[2]/div/div/ytd-menu-renderer/div[1]/ytd-segmented-like-dislike-button-renderer/yt-smartimation/div/div[2]/ytd-toggle-button-renderer/yt-button-shape/button")))
            dislikes= dislikes.text
            if "萬" in dislikes: dislikes= int(float(dislikes.replace("萬",""))*10000)
            elif "億" in dislikes: dislikes= int(float(dislikes.replace("億",""))*100000000)
            elif dislikes.isdigit(): dislikes= int(dislikes)
            else: dislikes= 0
            # 抓取views
            views= WebDriverWait(firefox, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/div[1]/yt-formatted-string/span[1]")))
            views= int( views.text.replace("觀看次數：",'').replace("次",'').replace(",",''))
            # 抓取subscribers
            subscribers= WebDriverWait(firefox, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='owner-sub-count']")))
            subscribers= subscribers.text.replace("位訂閱者","")
            if "萬" in subscribers: subscribers= int(float(subscribers.replace("萬",""))*10000)
            elif "億" in subscribers: subscribers= int(float(subscribers.replace("億",""))*100000000)
            else: subscribers= int(subscribers)
            # 抓取channel
            channel= WebDriverWait(firefox, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='text']/a")))
            channel_name= channel.text
            channel_id= channel.get_attribute("href").replace("https://www.youtube.com/",'')
            
            print(title)
            print("----")
            
            # 開始找右邊相關影片的其他連結
            results= WebDriverWait(firefox, 10).until(EC.presence_of_element_located((By.ID, "secondary")))
            results= results.find_elements(By.TAG_NAME, "a")
            results= [result.get_attribute("href") for result in results]
            # 篩選掉含有時間戳的網址(大該率是同一部影片的不同時間而已)
            results= [result for result in results if result!=None and "www.youtube.com/watch?" in result and '&t=' not in result]
            
            # 關閉分頁
            firefox.switch_to.window(window_name=windowName)
            firefox.close()
            firefox.switch_to.window(window_name=firefox.window_handles[-1])
            
            # 如果title或description中有包含關鍵字，就儲存到資料庫，並開始找相關連結
            reStr= f"({'|'.join(keywords.strip().split())})"
            if re.search(reStr, title+description):
                # 確認此連結不在資料庫裡，再新增
                if getData("youtube", "SELECT link FROM youtube WHERE link='{}';".format(href.replace("'", "''")))==[]:
                    insertData("youtube", {"title":title, "description":description, "link": href, "channel_name":channel_name, "channel_id":channel_id, "subscribers":subscribers, "views":views, "likes":likes, "dislikes":dislikes})
                
                for result in results:
                    if result not in candidates:
                        time.sleep(0.2)
                        candidates.append(result)
                        findRelated(result, num-1)
        except Exception as e:
            # 報錯時也要關閉分頁
            firefox.switch_to.window(window_name=windowName)
            firefox.close()
            firefox.switch_to.window(window_name=firefox.window_handles[-1])
            # print 錯第幾行
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)
            return




# 分別進入第一批連結，並取得資料與下一批連結
for i,firstLink in enumerate(firstLinks):
    print("---", i, "/", len(firstLinks), "---")
    findRelated(firstLink, relatedStack)

firefox.quit()




