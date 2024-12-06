from django.core.management.base import BaseCommand
import feedparser
import requests
from bs4 import BeautifulSoup
from langdetect import detect
from apps.educationContent.models import EducationContent
from apps.educationContent.serializers import sanitize_text


class Command(BaseCommand):
    help = 'Fetches Spanish cryptocurrency educational articles from RSS feeds and Medium and saves them to the database'

    def handle(self, *args, **kwargs):
        rss_feeds = {
            "CoinTelegraph en Español": "https://es.cointelegraph.com/rss",
            "CryptoNoticias": "https://www.criptonoticias.com/feed/"
        }

        # Keywords to identify educational content
        education_keywords = {
            'básico': ['introducción', 'principiante', 'básico', 'fundamentos', 'empezar', 'qué es', 'cómo funciona'],
            'intermedio': ['intermedio', 'tutorial', 'estrategias', 'cómo invertir', 'guía'],
            'avanzado': ['avanzado', 'experto', 'profundizado', 'blockchain avanzado', 'trading avanzado']
        }

        def parse_rss_feed(url):
            feed = feedparser.parse(url)
            articles = []
            for entry in feed.entries:
                # Extract image URL if available
                image_url = ''
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url'] if entry.media_content else ''
                elif 'links' in entry:
                    for link in entry.links:
                        if link.get('type', '').startswith('image/'):
                            image_url = link['href']
                            break

                articles.append({
                    'title': sanitize_text(entry.title) if 'title' in entry else '',
                    'link': entry.link if 'link' in entry else '',
                    'published': entry.published if 'published' in entry else None,
                    'description': sanitize_text(entry.description) if 'description' in entry else '',
                    'image_url': image_url
                })
            return articles

        def scrape_medium_articles(query, language="es"):
            medium_url = f"https://medium.com/tag/{query}/latest"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(medium_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            for article in soup.find_all('article'):
                title_tag = article.find('h2')
                link_tag = article.find('a', href=True)
                img_tag = article.find('img')  # Fetch first image in the article
                if title_tag and link_tag:
                    sanitized_title = sanitize_text(title_tag.text.strip())
                    image_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else ''
                    articles.append({
                        'title': sanitized_title,
                        'link': link_tag['href'],
                        'snippet': sanitize_text(article.text.strip()[:150]),  # Short snippet
                        'image_url': image_url
                    })
            return articles

        def is_spanish(text):
            try:
                return detect(text) == "es"
            except Exception:
                return False

        def match_education_level(text):
            for level, keywords in education_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        return level
            return 'general'

        all_articles = []

        # Parse RSS Feeds
        for name, url in rss_feeds.items():
            print(f"Fetching articles from {name}...")
            articles = parse_rss_feed(url)
            all_articles.extend(articles)

        # Scrape Medium Articles
        query = "educación criptomoneda"
        print("Scraping Medium for educational cryptocurrency articles in Spanish...")
        medium_articles = scrape_medium_articles(query)
        all_articles.extend(medium_articles)

        # Save articles to database
        for article in all_articles:
            try:
                # Filter by language
                if not is_spanish(article['title']):
                    print(f"Skipping non-Spanish article: {article['title']}")
                    continue

                # Determine education level
                level = match_education_level(article['title'] + ' ' + article.get('description', ''))

                if EducationContent.objects.filter(content_url=article['link']).exists():
                    print(f"Duplicate article skipped: {article['link']}")
                    continue

                EducationContent.objects.update_or_create(
                    content_url=article['link'],
                    defaults={
                        'title': article['title'],
                        'content_type': 'artículo educativo',  # Mark as educational content
                        'level': level,  # Save the determined level
                        'image_url': article['image_url'],  # Save the image URL
                    }
                )
                print(f"Saved educational article: {article['title']} (Level: {level}) with image: {article['image_url']}")
            except Exception as e:
                print(f"Error saving article to database: {e}")

        print(f"Finished fetching and saving {len(all_articles)} articles.")
