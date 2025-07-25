# news/utils.py
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import string
import nltk
nltk.download('punkt')  # Add only temporarily!



def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.get_text(separator=' ', strip=True)


def fetch_news_from_rss(feed_url, source_name):
    articles_data = []

    try:
        response = requests.get(
            feed_url,
            headers={'User-Agent': 'ByteNewsScraper/1.0'},
            timeout=10
        )
        response.raise_for_status()

        feed = feedparser.parse(response.content)

        for entry in feed.entries:
            title = entry.title
            link = entry.link

            raw_content = entry.get('summary', entry.get('description', ''))
            cleaned_content = clean_html(raw_content)  # ✅ Clean HTML

            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'published'):
                try:
                    published_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
                    published_date = published_date.replace(tzinfo=timezone.utc)
                except Exception:
                    published_date = None

            articles_data.append({
                'title': title,
                'link': link,
                'content': cleaned_content,
                'publication_date': published_date,
                'source': source_name
            })

        return articles_data

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not fetch from {source_name}: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Unexpected error from {source_name}: {e}")
        return []
    

def summarize_text(text, num_sentences=3):
    # 1. Sentence tokenization
    sentences = sent_tokenize(text)

    # 2. Word tokenization and stop word removal
    stop_words = set(stopwords.words('english'))
    word_frequencies = {}
    
    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        for word in words:
            if word not in stop_words and word not in string.punctuation:
                if word not in word_frequencies:
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

    # 3. Normalize frequencies
    if not word_frequencies:
        return 'No summary could be generated.'
    
    max_freq = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] /= max_freq

    # 4. Score sentences
    sentence_scores = {}
    for sentence in sentences:
        sentence_lower = sentence.lower()
        sentence_scores[sentence] = 0
        for word in word_tokenize(sentence_lower):
            if word in word_frequencies:
                sentence_scores[sentence] += word_frequencies[word]

    # 5. Select top N sentences
    sorted_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    summary_sentences = sorted(sorted_sentences[:num_sentences], key=sentences.index)

    # 6. Return summary
    return ' '.join(summary_sentences)    


def generate_summary(text,title="", num_sentences=3):
    if not text or not isinstance(text, str):
        return "No content available to summarize."

    # 1. Sentence tokenization
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text  # Article is too short to summarize

    # 2. Word tokenization and filtering
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]

    if not filtered_words:
        return "Text contains no meaningful content to summarize."

    # 3. Calculate word frequencies
    word_frequencies = Counter(filtered_words)

    # 4. Score each sentence
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        sentence_words = word_tokenize(sentence.lower())
        for word in sentence_words:
            if word in word_frequencies:
                if i not in sentence_scores:
                    sentence_scores[i] = 0
                sentence_scores[i] += word_frequencies[word]

    if not sentence_scores:
        return "Unable to score sentences for summarization."

    # 5. Select top N sentences
    top_indices = sorted(
        sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
    )
    selected_sentences = [sentences[i[0]] for i in top_indices]

    return " ".join(selected_sentences)