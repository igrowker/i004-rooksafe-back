from django.core.management.base import BaseCommand
from googleapiclient.discovery import build
from django.conf import settings
from apps.educationContent.models import EducationContent
from apps.educationContent.serializers import sanitize_text


class Command(BaseCommand):
    help = 'Fetches Spanish cryptocurrency videos from YouTube and saves them to the database'

    def handle(self, *args, **kwargs):
        youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)

        level_keywords = {
            'básico': ['introducción', 'principiante', 'básico', 'fundamentos', 'empezar', 'qué es'],
            'intermedio': ['intermedio', 'técnicas', 'estrategias', 'cómo invertir', 'tutorial'],
            'avanzado': ['avanzado', 'experto', 'profesional', 'profundizado', 'blockchain avanzado', 'trading avanzado']
        }

        # 3 videos per level
        for level, keywords in level_keywords.items():
            print(f"Fetching videos for level: {level}")
            videos_fetched = 0
            for keyword in keywords:
                if videos_fetched >= 3:
                    break

                # "criptomoneda" + level keyword
                query = f"criptomoneda {keyword}"

                # Request with combined query
                request = youtube.search().list(
                    q=query,
                    part='snippet',
                    type='video',
                    videoCaption='any',
                    videoDuration='any',
                    videoEmbeddable='true',
                    videoSyndicated='true',
                    relevanceLanguage='es',
                    regionCode='ES',
                    maxResults=3,
                    publishedAfter='2023-01-01T00:00:00Z'
                )

                response = request.execute()

                for item in response.get('items', []):
                    if videos_fetched >= 3:
                        break

                    try:
                        video_id = item['id']['videoId']
                        title = sanitize_text(item['snippet']['title'])
                        description = sanitize_text(item['snippet']['description'])
                        url = f'https://www.youtube.com/watch?v={video_id}'

                        # Skip duplicates
                        if EducationContent.objects.filter(content_url=url).exists():
                            print(f"Duplicate video skipped: {url}")
                            continue

                        EducationContent.objects.update_or_create(
                            content_url=url,
                            defaults={
                                'title': title,
                                'content_type': 'video',
                                'level': level,
                            }
                        )
                        videos_fetched += 1
                        print(f"Saved video: {title} to {level}")
                    except KeyError as e:
                        print(f"Missing key in video item: {e}")
                    except Exception as e:
                        print(f"Error saving video to database: {e}")

        print("Finished fetching videos for all levels.")
