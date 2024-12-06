from django.core.management.base import BaseCommand
import feedparser
import requests
from bs4 import BeautifulSoup
from langdetect import detect
from apps.educationContent.models import EducationContent
from apps.educationContent.serializers import sanitize_text


class Command(BaseCommand):
    help = 'Fetches articles based on keywords, includes images, classifies by level, and saves to the database'

    def handle(self, *args, **kwargs):
        rss_feeds = {
            "CoinTelegraph en Español": "https://es.cointelegraph.com/rss",
            "CryptoNoticias": "https://www.criptonoticias.com/feed/"
        }

        # Keywords mapped to levels
        level_keywords = {
            'básico': ['bitcoin', 'blockchain', 'monedero'],
            'intermedio': ['estrategias', 'análisis', 'ICO', 'Altcoins'],
            'avanzado': ['DeFi', 'trading', 'contratos', 'investigación']
        }

        # Limit to 3 articles per level
        level_limits = {level: 0 for level in level_keywords.keys()}
        max_articles_per_level = 3

        def fetch_articles_from_rss(url, keyword):
            """
            Fetch articles from an RSS feed and filter them by a keyword.
            """
            feed = feedparser.parse(url)
            articles = []

            for entry in feed.entries:
                title = entry.title if 'title' in entry else ''
                description = entry.description if 'description' in entry else ''
                link = entry.link if 'link' in entry else ''

                # Extract image URL if available
                image_url = ''
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url'] if entry.media_content else ''
                elif 'links' in entry:
                    for link_obj in entry.links:
                        if link_obj.get('type', '').startswith('image/'):
                            image_url = link_obj['href']
                            break

                if keyword.lower() in title.lower() or keyword.lower() in description.lower():
                    articles.append({
                        'title': sanitize_text(title),
                        'description': sanitize_text(description),
                        'link': link,
                        'image_url': image_url
                    })
            return articles

        def is_spanish(text):
            """
            Check if a piece of text is in Spanish.
            """
            try:
                return detect(text) == 'es'
            except Exception:
                return False

        def save_article(article, level):
            """
            Save an article to the database if it doesn't already exist.
            """
            if level_limits[level] >= max_articles_per_level:
                return False  # Skip if limit reached

            # Skip duplicates
            if EducationContent.objects.filter(content_url=article['link']).exists():
                print(f"Duplicate article skipped: {article['title']}")
                return False

            try:
                EducationContent.objects.update_or_create(
                    content_url=article['link'],
                    defaults={
                        'title': article['title'],
                        'content_type': 'articulo',
                        'level': level,
                        'image_url': article['image_url'],
                    }
                )
                level_limits[level] += 1
                print(f"Saved article: {article['title']} (Level: {level}) with image: {article['image_url']}")
                return True
            except Exception as e:
                print(f"Error saving article to database: {e}")
                return False

        # Fetch articles from all RSS feeds and classify them
        for level, keywords in level_keywords.items():
            for keyword in keywords:
                if level_limits[level] >= max_articles_per_level:
                    break  # Skip if level limit reached

                print(f"\nFetching articles for level '{level}' with keyword: {keyword}")

                # Fetch from RSS feeds
                for name, url in rss_feeds.items():
                    print(f"Checking RSS feed: {name}...")
                    articles = fetch_articles_from_rss(url, keyword)

                    for article in articles:
                        if not is_spanish(article['title']):
                            print(f"Skipping non-Spanish article: {article['title']}")
                            continue

                        save_article(article, level)

        print("\nFinished fetching and saving articles.")
        print(f"Totals: {level_limits}")
