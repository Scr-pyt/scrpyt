import requests
from bs4 import BeautifulSoup
import time

def get_baidu_news():
    url = "https://news.baidu.com/"  # 百度新闻首页
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'  # 百度使用 utf-8
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 百度新闻的热点新闻在 class="hotnews" 的 ul 中
        hot_news = soup.find('ul', class_='hotnews')
        if not hot_news:
            # 备用选择器：查找所有 a 标签，过滤新闻标题
            items = soup.find_all('a', target='_blank')
            news_list = []
            for a in items:
                title = a.get_text(strip=True)
                link = a.get('href')
                if title and link and len(title) > 5 and 'http' in link:
                    news_list.append((title, link))
            return news_list[:20]  # 取前20条
        
        # 提取热点新闻
        news_items = []
        for li in hot_news.find_all('li'):
            a = li.find('a')
            if a:
                title = a.get_text(strip=True)
                link = a.get('href')
                if link and not link.startswith('javascript'):
                    news_items.append((title, link))
        return news_items
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

if __name__ == '__main__':
    print("===== 今日热点新闻 =====")
    news = get_baidu_news()
    for idx, (title, link) in enumerate(news[:15], 1):
        print(f"{idx}. {title}")
        print(f"   链接: {link}\n")
        time.sleep(0.5)  # 打印间隔
