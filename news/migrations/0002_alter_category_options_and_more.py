# Generated by Django 5.0 on 2025-07-21 16:56

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name']},
        ),
        migrations.AlterUniqueTogether(
            name='readinghistory',
            unique_together={('user', 'article')},
        ),
    ]
