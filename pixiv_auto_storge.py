
import json
from bs4 import BeautifulSoup
import time
import requests
import os
import re

if not os.path.exists("./novel"):
        os.makedirs("./novel")

try:
    with open("script_config.json","r",encoding='utf-8') as f:          #导入用户网站
        config = json.load(f)
except:
    with open("script_config.json","w",encoding="utf-8") as f:
        data = {
        "website": {
        "url": "",
        "comment": "user's pixiv page"
    },
    "user_id":{
    "id":"",
    "comment":"enter your pixiv id"
    },
        "header": {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
            }
}
        json.dump(data, f, ensure_ascii=False, indent=4)

storge = dict()
try:
    with open("storge.json","r",encoding='utf-8') as f:                 #导入先前储存的文章
        storge = json.load(f)
except:
    with open("storge.json","w",encoding="utf-8") as f:
        data = {}
        json.dump(data,f,ensure_ascii=False,indent=4)

try:
    with open("cookie.json","r",encoding="utf-8") as f:                 #导入cookie
        cookie = json.load(f)
except:
    with open("cookie.json","w",encoding="utf-8") as f:
        data = {}
        json.dump(data,f,ensure_ascii=False,indent=4)


url = config["website"]["url"]
header = config["header"]
cookie_dict = {item["name"]: item["value"] for item in cookie}

response = requests.get("https://www.pixiv.net/ajax/user/"+config["user_id"]["id"]+"/novels/bookmarks?tag=&offset=0&limit=30&rest=show&lang=zh", cookies=cookie_dict, headers=header, timeout=5)

print("[{:^10}] require pixiv web |statue: {:^3}|".format(time.time(),response.status_code))

page = BeautifulSoup(response.text,"html.parser")


data = response.json()
total_page = int(data["body"]["total"])
page_limit = (total_page+30-1)//30



links = dict()
for i in range(page_limit):
    print("[{:^10}] require ep {:^3} of web |statue: {:^3}|".format(time.time(),i,response.status_code))
    response = requests.get("https://www.pixiv.net/ajax/user/"+config["user_id"]["id"]+"/novels/bookmarks?tag=&offset="+str(30*i)+"&limit=30&rest=show&lang=zh", cookies=cookie_dict, headers=header)
    data = response.json()
    for work in data["body"]["works"]:                                 #找到文章的名字与链接
        work_id = work["id"]
        work_title = work["title"]
        if work_id in storge:                                             #判断链接是否之前被储存过
            pass
        else:
            storge[work_id] = {"title":work_title,"url":"https://www.pixiv.net/novel/show.php?id="+work_id,"api":"https://www.pixiv.net/ajax/novel/"+work_id+"?lang=zh"}
            links[work_title] = "https://www.pixiv.net/ajax/novel/"+work_id+"?lang=zh"
    time.sleep(3)

for title, api_link in links.items():
    print("[{:^10}] require novel {} |statue: {:^3}|".format(time.time(),title,response.status_code))
    response = requests.get(api_link, cookies=cookie_dict, headers=header)
    data = response.json()
    if not data["error"]:
        title = data["body"]["title"]
        content_html = data["body"]["content"]
    
    
        page = BeautifulSoup(content_html, "html.parser")
    
        for br in page.find_all("br"):
            br.replace_with("\n")
    
        content_text = page.get_text()
    
        safe_title = re.sub(r'[\/:*?"<>|]', '_', title)

        with open("./novel/" + safe_title + ".txt", "w", encoding="utf-8") as f:
            f.write(f"title {title}\n")
            f.write("\ncontent: \n\n")
            f.write(content_text)
    time.sleep(3)

with open("storge.json","w",encoding="utf-8") as f:
    json.dump(storge,f,ensure_ascii=False,indent=4)


print("end")

