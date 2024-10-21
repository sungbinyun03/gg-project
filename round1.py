import json
import re
import csv
from rapidfuzz import fuzz

def extract_award_nominees(data):
    awards = data.get("award_data", {})
    result = {}

    for award_name, details in awards.items():
        nominees = details.get("nominees", [])
        winner = details.get("winner")
        if winner and winner not in nominees:
            nominees.append(winner)
        result[award_name] = nominees
    
    return result

def normalize_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()

def count_nominee_mentions(tweets, award_nominees):
    winner_patterns = [
        r"\b(wins?|won|winner|awarded)\b",
        r"\b(is|are)\s+(the)?\s*winners?\b",
        r"\b(the\s*winner\s*is)\b",
        r"\b(goes\s*to)\b"
    ]

    winner_regex = re.compile("|".join(winner_patterns), re.IGNORECASE)

    nominee_counts = {award: {nominee: 0 for nominee in nominees} for award, nominees in award_nominees.items()}
    for tweet_data in tweets:
        tweet = normalize_text(tweet_data["text"])
        if winner_regex.search(tweet):
            for award, nominees in award_nominees.items():
                for nominee in nominees:
                    normalized_nominee = normalize_text(nominee)
                    if fuzz.partial_ratio(normalized_nominee, tweet) > 80:
                        nominee_counts[award][nominee] += 1

    for award, counts in nominee_counts.items():
        print(f"Award: {award}")
        for nominee, count in counts.items():
            print(f"  {nominee}: {count} mentions")

    winners = {}
    for award, counts in nominee_counts.items():
        if counts:
            winners[award] = max(counts, key=counts.get) if max(counts.values()) > 0 else None
    
    export_to_csv(nominee_counts)
    
    return winners

def export_to_csv(nominee_counts):
    with open('nominee_mentions.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Award", "Nominee", "Mentions"])
        for award, counts in nominee_counts.items():
            for nominee, count in counts.items():
                writer.writerow([award, nominee, count])

with open('gg2013answers.json', 'r') as f:
    data = json.load(f)

award_nominees = extract_award_nominees(data)

with open('gg2013.json', 'r') as f:
    tweets = json.load(f)

winners = count_nominee_mentions(tweets, award_nominees)

print(json.dumps(winners, indent=4))