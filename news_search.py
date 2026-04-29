import urllib.request
import xml.etree.ElementTree as ET

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

# Using Google News RSS for US/Israel news
url = "https://news.google.com/rss/search?q=US+Israel+conflict+war+latest&hl=en-US&gl=US&ceid=US:en"
news = fetch_rss(url)

if isinstance(news, list):
    print(f"Found {len(news)} latest news items related to US-Israel conflict:")
    for i, item in enumerate(news[:10]):
        print(f"{i+1}. {item['title']}")
        print(f"   Link: {item['link']}")
else:
    print(f"Error fetching news: {news}")
