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

# Using Google News RSS for Taiwan political news regarding New Taipei integration
# We search for keywords in Traditional Chinese for better accuracy
query = "新北 藍白整合 市長"
encoded_query = urllib.parse.quote(query)
url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"

news = fetch_rss(url)

print(f"--- 📅 關於「新北藍白整合市長選戰」今日新聞摘要 ({datetime.date.today()}) ---")
if isinstance(news, list):
    if not news:
        print("目前沒有搜尋到相關的新聞。")
    else:
        for i, item in enumerate(news[:10]):
            print(f"{i+1}. {item['title']}")
            print(f"   Link: {item['link']}")
else:
    print(f"Error: {news}")
