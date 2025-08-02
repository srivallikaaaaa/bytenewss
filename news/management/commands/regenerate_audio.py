from django.core.management.base import BaseCommand
from news.models import Article
from news.utils import generate_audio_summary

class Command(BaseCommand):
    help = "Regenerate all audio summaries for articles"

    def handle(self, *args, **kwargs):
        for article in Article.objects.all():
            if article.summary:
                self.stdout.write(f"Generating audio for: {article.title}")
                audio_url = generate_audio_summary(article.summary, article.id)
                if audio_url:
                    article.audio_file = audio_url
                    article.save()
                    self.stdout.write(self.style.SUCCESS(f"✓ Audio generated: {audio_url}"))
                else:
                    self.stdout.write(self.style.ERROR(f"✗ Failed to generate for {article.title}"))
            else:
                self.stdout.write(f"⚠ Skipping {article.title} (no summary)")