# news/utils.py
import os
import string
import logging
import posixpath
from collections import Counter
from email.utils import parsedate_to_datetime

import nltk
import feedparser
from gtts import gTTS
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from django.conf import settings

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

logger = logging.getLogger(__name__)

def generate_summary(text, article_title="", num_sentences=3):
    """
    Generates an extractive summary of the given text using sentence scoring.
    """
    if not text or not isinstance(text, str):
        return "No content available to summarize."

    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text

    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english') + list(string.punctuation))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]

    word_frequencies = Counter(filtered_words)

    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                sentence_scores[i] = sentence_scores.get(i, 0) + word_frequencies[word]

    top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    final_summary = [sentences[i] for i in sorted(top_indices)]

    return " ".join(final_summary)


def fetch_news_from_rss(url, source_name):
    """
    Fetches articles from the given RSS feed URL.
    """
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        content = entry.get('summary', '')
        article = {
            'title': entry.title,
            'link': entry.link,
            'publication_date': parsedate_to_datetime(entry.published) if 'published' in entry else None,
            'content': content,
            'source': source_name,
            'author': entry.get('author', 'Unknown'),
        }
        articles.append(article)

    return articles


def generate_audio_summary(text, article_id):
    """
    Converts the given text into an MP3 audio file and saves it under media/news_audio/.
    Returns the relative media URL for use in templates.
    """
    if not text:
        logger.warning(f"No text provided for audio summary for article_id: {article_id}")
        return None

    filename = f"summary_{article_id}.mp3"
    audio_dir = os.path.join(settings.MEDIA_ROOT, 'news_audio')
    os.makedirs(audio_dir, exist_ok=True)

    filepath = os.path.join(audio_dir, filename)

    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filepath)
        logger.info(f"Generated audio summary for article {article_id} at {filepath}")
        return posixpath.join(settings.MEDIA_URL, 'news_audio', filename)
    except Exception as e:
        logger.error(f"Error generating audio for article {article_id}: {e}")
        return None
from gtts import gTTS
import os

def text_to_speech(text, filename):
    tts = gTTS(text)
    audio_path = os.path.join("media/audio", filename)
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    tts.save(audio_path)
    return f"audio/{filename}" 