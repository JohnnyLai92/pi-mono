import urllib.request
import xml.etree.ElementTree as ET
import datetime

def fetch_rss(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            items = []
            for item in root.findall('.//item'):
                title = item.find('title').text
                link = item.find('link').text
                items.append({'title': title, 'link': link})
            return items
    except Exception as e:
        return str(e)

url = 'https://news.google.com/rss/search?q=Japan+earthquake+latest&hl=en-US&gl=US&ceid=US:en'
news = fetch_rss(url)

print(f"--- 📅 日本地震最新新聞摘要 ({datetime.date.today()}) ---")
if isinstance(news, list):
    if not news:
        print("目前沒有搜尋到今日顯著的地震新聞。")
    else:
        for i, item in enumerate(news[:8]):
            t = item['title']
            l = item['link']
            print(f"{i+1}. {t}")
            print(f"   Link: {l}")
else:
    print(f"Error: {news}")
