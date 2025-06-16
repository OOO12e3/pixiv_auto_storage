# coding=utf-8
import json
import sqlite3

data = dict()
with open("storge.json","r") as f:
    data = json.load(f)

database = sqlite3.connect("storage.db")
cur = database.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS novel (
                                id INT PRIMARY KEY NOT NULL,
                                title TEXT,
                                url TEXT NOT NULL,
                                api TEXT NOT NULL);""")

for i,j in data.items():
    cur.execute('''INSERT OR IGNORE INTO novel VALUES(?,?,?,?)''',(int(i),j["title"],j["url"],j["api"]))

database.commit()
database.close()
print("end")