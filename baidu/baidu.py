# -*- coding: utf-8 -*-
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from collections import Counter
import jieba
import re

# ===========================
# 1. 启动浏览器
# ===========================
print("程序开始")

options = Options()
options.add_argument("--start-maximized")

print("准备启动浏览器")
driver = webdriver.Edge(options=options)
print("浏览器启动成功")

#关键词
keyword = ""
all_text = []

def get_page_source(keyword):
    search_url = f"https://www.baidu.com/s?wd={keyword}"
    driver.get(search_url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h3"))
    )

    print("成功进入搜索结果页")
    return driver.page_source

def parse_page(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    results = soup.find_all("div", class_="c-container")

    page_text = []

    for result in results:
        # 标题
        h3 = result.find("h3")
        if h3:
            title = h3.get_text()
            page_text.append(title)

        # 摘要
        abstract = result.find("div", class_=re.compile("content"))
        if abstract:
            description = abstract.get_text()
            page_text.append(description)

    return page_text

# ===========================
# 2. 抓取第一页
# ===========================
page_source = get_page_source(keyword)
texts = parse_page(page_source)
all_text.extend(texts)

# ===========================
# 3. 翻页抓取（可改页数）
# ===========================
#页数
num=9
for i in range(num):
    try:
        time.sleep(random.uniform(2,4))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        next_button = driver.find_element(By.LINK_TEXT, "下一页 >")
        next_button.click()
        time.sleep(3)

        page_source = driver.page_source
        texts = parse_page(page_source)
        all_text.extend(texts)

    except:
        break

driver.quit()

print("网页抓取完成")
print(len(all_text))
# ===========================
# 4. 文本处理
# ===========================
full_text = " ".join(all_text)

# 只保留中文
full_text = re.sub(r"[^\u4e00-\u9fa5]", "", full_text)

# 分词
words = jieba.cut(full_text)

# 停用词（可自改）
stopwords = ["的","了","是","在","和","与","为","对","中","等","及","也","将","年月日","暂停","相关","如何","为何","成为"]

filtered_words = [w for w in words if w not in stopwords and len(w) > 1]

word_freq = Counter(filtered_words)

# ===========================
# 5. 保存词频文件
# ===========================
with open("youth_night_school_wordfreq.txt", "w", encoding="utf-8") as f:
    for word, freq in word_freq.most_common():
        f.write(f"{word}: {freq}\n")

print("词频统计完成")

# ===========================
# 6. 生成词云
# ===========================

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator

#设置字体
font_path = "C:\\Windows\\Fonts\\simhei.ttf"

# 读取背景图
mask_image = np.array(Image.open("图片路径").convert("RGB"))


wordcloud = WordCloud(
    width=2048,
    height=2048,
    scale=3,
    font_path=font_path,
    mask=mask_image,
    background_color=None,
    mode="RGBA",
    max_words=200,
relative_scaling=0.8,
    min_font_size=10,
)

wordcloud.generate_from_frequencies(word_freq)

# 让词云颜色跟图片颜色一致
image_colors = ImageColorGenerator(mask_image)
wordcloud.recolor(color_func=image_colors)

plt.figure(figsize=(20,10))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.savefig("wordcloud.png", dpi=300)
plt.show()

print("词云生成完成")