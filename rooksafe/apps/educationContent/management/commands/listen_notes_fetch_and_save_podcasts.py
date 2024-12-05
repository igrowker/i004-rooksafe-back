from django.core.management.base import BaseCommand
import requests

from apps.educationContent.models import EducationContent

# LISTEN_NOTES_API_KEY=os.environ['LISTEN_NOTES_API_KEY']
class Command(BaseCommand):
    help = 'Fetches one latest episode per level from Listen Notes and saves them to the database'

    def handle(self, *args, **kwargs):
        # Base URL for Listen Notes API
        BASE_URL = "https://listen-api.listennotes.com/api/v2/search"
        HEADERS = {'X-ListenAPI-Key': LISTEN_NOTES_API_KEY}
        request_count = 0
        

        # Define keywords for each level
        level_keywords = {
            'básico': ['fundamentos', 'que es', 'como comprar', 'como invertir'],
            'intermedio': ['análisis técnico', 'técnicas', 'estrategias', 'trading'],
            'avanzado': ['noticias','hablando', 'blockchain avanzado', 'trading avanzado']
        }

        for level, keywords in level_keywords.items():
            print(f"Fetching latest episode for level: {level}")
            episode_saved = False  # Flag to stop requests once an episode is saved

            for keyword in keywords:
                if episode_saved:  # Skip further requests if an episode is already saved
                    break

                # Build request parameters
                params = {
                    'q': f"cripto {keyword}",
                    'type': 'episode',  # Fetch episodes directly
                    'language': 'es',  # Language set to Spanish
                    'sort_by_date': 0,  # Sort by latest date
                    'len_min': 0,
                    # 'len_max': 120,  # Maximum duration in minutes
                    'safe_mode': 1  # Explicit content filter
                }

                try:
                    response = requests.get(BASE_URL, headers=HEADERS, params=params)
                    remaining_requests = response.headers.get('X-RateLimit-Remaining')
                    print(f"Remaining API requests: {remaining_requests}")
                    request_count += 1  # Increment request counter
                    print(f"API Request #{request_count} for level {level}, keyword '{keyword}'")
                    response.raise_for_status()
                    data = response.json()

                    # Process the first result from the API
                    for item in data.get('results', []):
                        episode_title = item.get('title_original', 'Unknown Title')
                        episode_url = item.get('listennotes_url', '')
                        podcast_title = item.get('podcast', {}).get('title_original', 'Unknown Podcast')
                        image_url = item.get('image', '')  # Episode cover image

                        # Avoid duplicates in the database
                        if EducationContent.objects.filter(content_url=episode_url).exists():
                            print(f"Duplicate episode skipped: {episode_url}")
                            continue

                        # Save to the database
                        EducationContent.objects.update_or_create(
                            content_url=episode_url,
                            defaults={
                                'title': f"{podcast_title}: {episode_title}",
                                'content_type': 'podcast',  # Align with model
                                'level': level,
                                'image_url': image_url,
                            }
                        )

                        # Mark this level as fetched and stop further requests
                        episode_saved = True
                        print(f"Saved episode: {podcast_title}: {episode_title} to level {level}")
                        break

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching episodes for level {level}: {e}")

        print("Finished fetching one episode per level.")
