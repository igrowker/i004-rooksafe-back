import requests
import time
from django.core.management.base import BaseCommand
from apps.educationContent.models import EducationContent
import os

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
TOKEN_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"


class Command(BaseCommand):
    help = 'Fetch Spotify podcasts by levels and save them to the database'

    def __init__(self):
        super().__init__()
        self.access_token = None
        self.token_expires_at = 0

    def get_access_token(self):
        """Get a new access token using Client Credentials Flow."""
        if time.time() < self.token_expires_at:
            return self.access_token

        print("Refreshing access token...")
        auth_response = requests.post(
            TOKEN_URL,
            headers={
                "Authorization": f"Basic {self.encode_credentials()}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
        )

        if auth_response.status_code == 200:
            token_data = auth_response.json()
            self.access_token = token_data["access_token"]
            self.token_expires_at = time.time() + token_data["expires_in"]
            return self.access_token
        else:
            raise Exception(
                f"Failed to fetch access token: {auth_response.status_code} {auth_response.text}"
            )

    def encode_credentials(self):
        """Encode Client ID and Secret as Base64."""
        import base64

        credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        return base64.b64encode(credentials.encode()).decode()

    def search_podcasts(self, query, market="ES"):
        """Search for podcasts using Spotify API."""
        token = self.get_access_token()
        response = requests.get(
            SEARCH_URL,
            headers={"Authorization": f"Bearer {token}"},
            params={"q": query, "type": "show", "market": market},
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to fetch podcasts: {response.status_code} {response.text}"
            )

    def is_relevant_to_crypto(self, show):
        """Check if the podcast is specifically relevant to crypto."""
        crypto_keywords = ["cripto", "crypto", "blockchain", "bitcoin", "ethereum"]
        name = show.get('name', '').lower()
        description = show.get('description', '').lower()

        # Check if any crypto-related keyword is in the name or description
        return any(keyword in name or keyword in description for keyword in crypto_keywords)

    def save_to_database(self, show, level):
        """Save podcast to the database."""
        podcast_name = show['name']
        podcast_url = show['external_urls']['spotify']
        image_url = show['images'][0]['url']
        # description = show['description']

        # Avoid duplicates
        if EducationContent.objects.filter(content_url=podcast_url).exists():
            print(f"Duplicate podcast skipped: {podcast_url}")
            return False

        EducationContent.objects.create(
            title=podcast_name,
            content_type='podcast',
            level=level,
            image_url=image_url,
            content_url=podcast_url,
        )
        print(f"Saved podcast: {podcast_name} for level {level}")
        return True

    def handle(self, *args, **kwargs):
        """Main entry point for the management command."""
        level_keywords = {
            'básico': ['fundamentos', 'que es', 'como comprar', 'como invertir'],
            'intermedio': ['análisis técnico', 'técnicas', 'estrategias', 'trading'],
            'avanzado': ['noticias', 'hablando', 'blockchain avanzado', 'trading avanzado']
        }

        for level, keywords in level_keywords.items():
            print(f"Fetching podcasts for level: {level}")
            podcasts_saved = 0

            for keyword in keywords:
                if podcasts_saved >= 3:
                    break

                try:
                    print(f"Searching podcasts with keyword: {keyword}")
                    # Use phrase matching and validate relevance
                    podcast_data = self.search_podcasts(query=f'"cripto {keyword}"')
                    shows = podcast_data.get("shows", {}).get("items", [])

                    for show in shows:
                        if podcasts_saved >= 3:
                            break

                        if not self.is_relevant_to_crypto(show):
                            print(f"Skipped unrelated podcast: {show.get('name', 'Unknown Podcast')}")
                            continue

                        if self.save_to_database(show, level):
                            podcasts_saved += 1

                except Exception as e:
                    print(f"Error fetching podcasts for level {level} with keyword {keyword}: {e}")

            if podcasts_saved < 3:
                print(f"Warning: Only saved {podcasts_saved} podcasts for level {level}.")
            else:
                print(f"Successfully saved 3 podcasts for level {level}.")

        print("Finished fetching podcasts for all levels.")
