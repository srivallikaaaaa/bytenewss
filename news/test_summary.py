from news.utils import generate_summary

text = """
India won the match against Australia in a thrilling finish.
The crowd was ecstatic as Virat Kohli hit the winning runs.
Earlier, Australia had set a target of 250 runs.
India chased the total in the final over.
The match was held in Mumbai.
"""

summary = generate_summary(text, num_sentences=2)
print("Summary:", summary)
