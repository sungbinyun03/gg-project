import json
import re
import csv
from rapidfuzz import fuzz
from .constants import WINNER_PATTERNS, AWARD_NOMINEES

def normalize_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()

def count_nominee_mentions(tweets, award_nominees):
    winner_regex = re.compile("|".join(WINNER_PATTERNS), re.IGNORECASE)

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


def get_winners(year):
    file_path = f'gg{year}.json'
        
    with open(file_path, 'r') as f:
        tweets = json.load(f)

    winners = count_nominee_mentions(tweets, AWARD_NOMINEES)

    print(json.dumps(winners, indent=4))
    return winners