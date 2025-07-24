# news/utils.py
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone


def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.get_text(separator=' ', strip=True)


def fetch_news_from_rss(feed_url, source_name):
    articles_data = []

    try:
        response = requests.get(
            feed_url,
            headers={'User-Agent': 'ByteNewsScraper/1.0'},
            timeout=10
        )
        response.raise_for_status()

        feed = feedparser.parse(response.content)

        for entry in feed.entries:
            title = entry.title
            link = entry.link

            raw_content = entry.get('summary', entry.get('description', ''))
            cleaned_content = clean_html(raw_content)  # ✅ Clean HTML

            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'published'):
                try:
                    published_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
                    published_date = published_date.replace(tzinfo=timezone.utc)
                except Exception:
                    published_date = None

            articles_data.append({
                'title': title,
                'link': link,
                'content': cleaned_content,
                'publication_date': published_date,
                'source': source_name
            })

        return articles_data

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not fetch from {source_name}: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Unexpected error from {source_name}: {e}")
        return []