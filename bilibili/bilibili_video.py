import requests,pandas as pd,time,random
from tqdm import tqdm

headers={
    "User-Agent":"Mozilla/5.0",
    "Referer":"https://www.bilibili.com/",
    "Origin":"https://www.bilibili.com",
    "Accept-Language":"zh-CN,zh;q=0.9"
}

cookies={
    "SESSDATA":"yourSESSDATA"
}

#修改关键词
keywords=["keyword"]

#页数
pages_per_keyword=10
output_file= "bilibili_youth_consumption.csv"

search_url="https://api.bilibili.com/x/web-interface/search/type"
tag_url="https://api.bilibili.com/x/tag/archive/tags"

session=requests.Session()
session.headers.update(headers)
session.cookies.update(cookies)

all_data=[]

def safe_get(url,params,retry=3):
    for i in range(retry):
        try:
            r=session.get(url,params=params,timeout=15)

            if r.status_code==200:
                return r

            elif r.status_code==412:
                wait=10*(i+1)
                print("412等待",wait,"秒")
                time.sleep(wait)
        except:
            pass
    return None

def get_tags(bvid):
    r=safe_get(tag_url,{"bvid":bvid})
    if not r:
        return ""

    try:
        data=r.json()
        if data.get("data"):
            return ",".join(
                [
                    x["tag_name"]
                    for x in data["data"]
                ])
    except:
        pass
    return ""

for kw in keywords:
    print("\n关键词:",kw)
    for page in range(1,pages_per_keyword+1):
        print("页:",page)

        r=safe_get(search_url,
            {"search_type":"video",
             "keyword":kw,
             "page":page})

        if not r:
            print("搜索失败")
            continue

        try:
            data=r.json()

            if data.get("code")!=0:
                print("接口异常")
                continue

            videos=data["data"]["result"]

        except:
            continue

        for v in tqdm(videos):

            try:
                if v.get("type")!="video":
                    continue

                aid=int(v.get("aid",0))
                bvid=v.get("bvid","")

                tags=get_tags(bvid)

                row={
                    "keyword":kw,
                    "title":v.get("title",""),
                    "up_name":v.get("author",""),
                    "play":v.get("play",0),
                    "like":v.get("like",0),
                    "favorite":v.get("favorites",0),
                    "comment_count":v.get("review",0),
                    "pub_time":time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(v.get("pubdate",0))),
                    "search_tags":v.get("tag",""),
                    "full_tags":tags,
                    "aid":aid,
                    "bvid":bvid}

                all_data.append(row)

                time.sleep(random.uniform(1.5,3))

            except:
                continue
        time.sleep(random.uniform(5,10))

df=pd.DataFrame(all_data)

print("去重前:",len(df))
df.drop_duplicates(subset="bvid",inplace=True)

print("去重后:",len(df))
df.to_csv(output_file,index=False,encoding="utf-8-sig")

print("完成:",output_file)