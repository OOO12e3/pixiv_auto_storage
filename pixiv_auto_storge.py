# coding=utf-8
import json
import sqlite3
from token import EXACT_TOKEN_TYPES
from bs4 import BeautifulSoup
import time
import requests
import os
import re
import sqlite3
from ebooklib import epub

if not os.path.exists("novel"):
        os.makedirs("novel")

if not os.path.exists("img"):
    os.makedirs("img")

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
    "user_id": {
        "id": "",
        "comment": "enter your pixiv id"
    },
    "header": {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
    },
    "img_header": {
        "referer":"https://www.pixiv.net",
        "sec-ch-ua":"\"Not;A=Brand\";v=\"99\", \"Microsoft Edge\";v=\"139\", \"Chromium\";v=\"139\"",
        "sec-ch-ua-mobile":"?0",
        "sec-ch-ua-platform":"\"Linux\"",
        "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
    }
}
        json.dump(data, f, ensure_ascii=False, indent=4)

#storge = dict()
database  = sqlite3.connect("storage.db")
datacursor = database.cursor()
datacursor.execute("""CREATE TABLE IF NOT EXISTS novel (
                                id INT PRIMARY KEY NOT NULL,
                                title TEXT,
                                url TEXT NOT NULL,
                                api TEXT NOT NULL);""")
'''
try:
    with open("storge.json","r",encoding='utf-8') as f:                 #导入先前储存的文章
        storge = json.load(f)
except:
    with open("storge.json","w",encoding="utf-8") as f:
        data = {}
        json.dump(data,f,ensure_ascii=False,indent=4)
'''

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
img_header = config["img_header"]

response = requests.get("https://www.pixiv.net/ajax/user/"+config["user_id"]["id"]+"/novels/bookmarks?tag=&offset=0&limit=30&rest=show&lang=zh", cookies=cookie_dict, headers=header, timeout=5)

print("[{:^10}] require pixiv web |statue: {:^3}|".format(time.time(),response.status_code))

page = BeautifulSoup(response.text,"html.parser")


data = response.json()
total_page = int(data["body"]["total"])
page_limit = (total_page+30-1)//30



links = dict()
for i in range(page_limit):
    response = requests.get("https://www.pixiv.net/ajax/user/"+config["user_id"]["id"]+"/novels/bookmarks?tag=&offset="+str(30*i)+"&limit=30&rest=show&lang=zh", cookies=cookie_dict, headers=header)
    print("[{:^10}] require ep {:^3} of web |statue: {:^3}|".format(time.time(),i,response.status_code))
    data = response.json()
    for work in data["body"]["works"]:                                 #找到文章的名字与链接
        work_id = work["id"]
        work_title = work["title"]
        datacursor.execute('''SELECT EXISTS(SELECT 1 FROM novel WHERE id == {});'''.format(work_id))
        if datacursor.fetchone()[0]:                                             #判断链接是否之前被储存过
            pass
        else:
            url = "https://www.pixiv.net/novel/show.php?id="+work_id
            api = "https://www.pixiv.net/ajax/novel/"+work_id+"?lang=zh"
            datacursor.execute('''INSERT INTO novel (id, title, url, api) VALUES (?, ?, ?, ?);''',(int(work_id), work_title, url, api))
            #storge[work_id] = {"title":work_title,"url":"https://www.pixiv.net/novel/show.php?id="+work_id,"api":"https://www.pixiv.net/ajax/novel/"+work_id+"?lang=zh"}
            links[work_title] = "https://www.pixiv.net/ajax/novel/"+work_id+"?lang=zh"
    time.sleep(3)

'''
for title, api_link in links.items():
    response = requests.get(api_link, cookies=cookie_dict, headers=header)
    print("[{:^10}] require novel {} |statue: {:^3}|".format(time.time(),title,response.status_code))
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
'''

def download_img(url,id,cookie,header):
    try:
        res = requests.get(url,stream=True,cookies=cookie,headers=header)
        res.raise_for_status()
        with open("img/{}.jpg".format(id),"wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)
    except:
        print("download failed")

def change_to_html(json_content):
    if not json_content:  # 处理 None 或空字符串
        return "<p>none</p>"
    html_content = json_content
    html_content = re.sub(r'\n{3,}', '</p><p>', html_content)
    html_content = re.sub(r'\n{2}', '</p><p>', html_content)
    html_content = html_content.replace('\n', '<br/>')
    html_content= re.sub("\[uploadedimage:(\w+)\]",r"<img src=\"images/\1.jpg\">",html_content)
    return html_content

for title, api_link in links.items():
    response = requests.get(api_link, cookies=cookie_dict, headers=header)
    print("[{:^10}] require novel {} |statue: {:^3}|".format(time.time(),title,response.status_code))
    data = response.json()
    if not data["error"]:
        book = epub.EpubBook()
        title = data["body"]["title"]
        description = data["body"]["description"]
        content_html = data["body"]["content"]
        author = data["body"]["userName"]
        book.set_title(title)
        book.add_author(author)

        
        images_if = data["body"].get("textEmbeddedImages")
        if images_if:  # 只有在有图片时才执行
            for img_key, img_value in data["body"]["textEmbeddedImages"].items():
                download_img(img_value["urls"]["original"],img_key,cookie=cookie_dict,header=img_header)
                with open("img/{}.jpg".format(img_key),"rb") as f:
                    img_tmp = epub.EpubImage(uid=img_key, file_name='images/'+img_key+".jpg", media_type='image/jpeg', content=f.read())
                    book.add_item(img_tmp)
        
        book_description = epub.EpubHtml(title='description', file_name='description.xhtml', lang='zh')
        book_description.content = change_to_html(description)
        book.add_item(book_description)

        book_content = epub.EpubHtml(title="content",file_name="content.xhtml",lang="zh")
        book_content.content = change_to_html(content_html)
        book.add_item(book_content)

        img_key = "cover"
        download_img(data["body"]["coverUrl"],img_key,cookie=cookie_dict,header=img_header)
        with open("img/cover.jpg","rb") as f:
            book.set_cover("cover.jpg", f.read())

        
        book.spine = [book_description, book_content]
        epub.write_epub("novel/"+title+".epub",book,{})
    
        
    time.sleep(3)
    
'''
with open("storge.json","w",encoding="utf-8") as f:
    json.dump(storge,f,ensure_ascii=False,indent=4)
'''
try:
    database.commit()
except:
    pass
database.close()

print("end")

