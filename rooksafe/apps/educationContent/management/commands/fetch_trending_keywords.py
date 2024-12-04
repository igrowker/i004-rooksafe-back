from django.core.management.base import BaseCommand
from pytrends.request import TrendReq
from apps.educationContent.models import TrendingKeyword

class Command(BaseCommand):
    help = 'Fetch and save trending cryptocurrency keywords for each level in Spanish'

    def handle(self, *args, **kwargs):
        level_keywords = {
            'básico': 'criptomoneda principiantes',
            'intermedio': 'cripto estrategias',
            'avanzado': 'cripto expertos'
        }

        # Initialize pytrends with Spanish locale
        pytrends = TrendReq(hl='es-ES', tz=360)

        for level, topic in level_keywords.items():
            try:
                self.stdout.write(f"Fetching keywords for level: {level} and topic: {topic}")

                # Build the payload for the specific topic
                pytrends.build_payload([topic], geo='ES', timeframe='today 7-d')

                # Fetch related queries
                trending_data = pytrends.related_queries()

                # Check if there are 'top' results
                top_queries = trending_data.get(topic, {}).get('top')
                if top_queries is not None:
                    for query in top_queries['query']:
                        TrendingKeyword.objects.update_or_create(
                            level=level,
                            keyword=query.strip()
                        )
                        self.stdout.write(f"Saved keyword: {query} ({level})")
                else:
                    self.stderr.write(f"No trending data found for {topic} at level {level}")

            except Exception as e:
                self.stderr.write(f"Error fetching keywords for {level} ({topic}): {e}")
