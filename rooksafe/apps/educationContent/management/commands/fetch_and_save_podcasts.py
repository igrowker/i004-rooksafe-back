from django.core.management.base import BaseCommand
import requests
from site_app.settings.base import LISTEN_NOTES_API_KEY
from apps.educationContent.models import EducationContent

class Command(BaseCommand):
    help = 'Fetches Spanish cryptocurrency podcasts from Listen Notes and saves them to the database'

    def handle(self, *args, **kwargs):
        # Base URL for Listen Notes API
        BASE_URL = "https://listen-api.listennotes.com/api/v2/search"
        HEADERS = {'X-ListenAPI-Key': LISTEN_NOTES_API_KEY}

        # Define keywords for different levels
        level_keywords = {
            'básico': ['introducción', 'principiante', 'básico', 'fundamentos', 'qué es'],
            'intermedio': ['intermedio', 'técnicas', 'estrategias', 'cómo invertir', 'tutorial'],
            'avanzado': ['avanzado', 'experto', 'profesional', 'blockchain avanzado', 'trading avanzado']
        }

        # Number of podcasts per level
        for level, keywords in level_keywords.items():
            print(f"Fetching podcasts for level: {level}")
            podcasts_fetched = 0
            for keyword in keywords:
                if podcasts_fetched >= 3:
                    break

                # Make API request for podcasts
                params = {
                    'q': f"criptomoneda {keyword}",
                    'type': 'podcast',  # Search type
                    'language': 'Spanish',
                    'len_min': 0,
                    'len_max': 120,  # Max duration in minutes (2 hours)
                    'safe_mode': 1  # Explicit content filter
                }

                try:
                    response = requests.get(BASE_URL, headers=HEADERS, params=params)
                    response.raise_for_status()
                    data = response.json()

                    for item in data.get('results', []):
                        if podcasts_fetched >= 3:
                            break

                        try:
                            podcast_title = item.get('title_original', 'Unknown Title')
                            podcast_url = item.get('listennotes_url', '')
                            image_url = item.get('image', '')  # Get the podcast cover image

                            # Skip duplicates
                            if EducationContent.objects.filter(content_url=podcast_url).exists():
                                print(f"Duplicate podcast skipped: {podcast_url}")
                                continue

                            EducationContent.objects.update_or_create(
                                content_url=podcast_url,
                                defaults={
                                    'title': podcast_title,
                                    'content_type': 'podcast',
                                    'level': level,
                                    'image_url': image_url,
                                }
                            )
                            podcasts_fetched += 1
                            print(f"Saved podcast: {podcast_title} to {level}")
                        except Exception as e:
                            print(f"Error saving podcast to database: {e}")

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching podcasts: {e}")

        print("Finished fetching podcasts for all levels.")
