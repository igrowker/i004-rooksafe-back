from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Runs all article-fetching commands sequentially'

    def handle(self, *args, **kwargs):

        commands_to_run = [
            'fetch_and_save_articles',
            'fetch_and_save_videos',
            'spotify_fetch_and_save_podcasts',
        ]

        print("Starting to execute all commands...")

        for command in commands_to_run:
            try:
                print(f"\nRunning command: {command}")
                call_command(command)
                print(f"Successfully ran command: {command}")
            except Exception as e:
                print(f"Error while running command {command}: {e}")

        print("\nAll commands executed.")
