import json
import re
from collections import defaultdict
# Load categorized media data
with open('../resFiles/categorized_media.json', 'r') as f:
    media_data = json.load(f)
with open('../resFiles/firstpass.json', 'r') as f:
    tweets = json.load(f)
# Define award categories mapped to their respective media types without scoring
AWARD_CATEGORIES = {
    "best television series - drama": media_data["TV"]["Drama"],
    "best television series - comedy or musical": media_data["TV"]["Comedy or Musical"],
    "best motion picture - drama": media_data["Film"]["Drama"],
    "best motion picture - comedy or musical": media_data["Film"]["Comedy or Musical"],
    "best animated feature film": media_data["Film"]["Animated Film"],
    "best foreign language film": media_data["Film"]["Foreign Film"],
    "best screenplay - motion picture": [],
    "best mini-series or motion picture made for television": []
}

def clean_text(text):
    """Normalize text by removing special characters and converting to title case."""
    cleaned_text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    return cleaned_text.title().strip()  # Convert to title case
def count_mentions(tweets, title):
    """Count the number of mentions of a given title in a list of tweets."""
    count = 0
    title_pattern = re.compile(rf"\b{re.escape(title)}\b", re.IGNORECASE)
    for tweet in tweets:
        if title_pattern.search(tweet):
            count += 1
    return count

# Process each award category, clean titles, and remove duplicates
award_nominees = {}
for award, titles in AWARD_CATEGORIES.items():
    # Normalize and deduplicate titles
    unique_titles = {clean_text(title) for title in titles}
    award_nominees[award] = [{"title": title} for title in sorted(unique_titles)]

# Save the cleaned and deduplicated results to JSON
top_nominees = {}

for award, nominees in award_nominees.items():
    mention_counts = []

    # Count mentions for each nominee title in the tweets
    for nominee in nominees:
        title = nominee["title"]
        mentions = count_mentions(tweets, title)
        mention_counts.append((title, mentions))

    # Sort titles by mention count in descending order and take the top 5
    sorted_nominees = sorted(mention_counts, key=lambda x: x[1], reverse=True)[:5]
    top_nominees[award] = [{"title": title, "mentions": mentions} for title, mentions in sorted_nominees]

# Save the top 5 nominees for each award category to a JSON file
with open('../resFiles/top_nominees.json', 'w') as f:
    json.dump(top_nominees, f, indent=4)

print("Top 5 nominees by mentions saved to top_nominees.json")
print("Cleaned and deduplicated nominees saved to potential_nominees_cleaned.json")
