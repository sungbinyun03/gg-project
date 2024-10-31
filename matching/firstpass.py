import json
import re
from collections import Counter
from .constants import WINNING_PHRASES

def preprocess_tweet(tweet_text):
    tweet_text = re.sub(r"http\S+|www\S+|https\S+", '', tweet_text)  # Remove URLs
    tweet_text = re.sub(r'@(\w+)', r'\1', tweet_text)  # Remove the '@' sign but keep the mention
    tweet_text = re.sub(r'\#\w+', '', tweet_text)  # Remove hashtags
    tweet_text = re.sub(r'[^A-Za-z0-9 ]+', '', tweet_text)  # Remove non-alphanumeric characters
    
    # Add ")" after the next word following "RT"
    tweet_text = re.sub(r'(RT\s+\w+)', r'\1)', tweet_text)
    
    return tweet_text

def run_firstpass(year):
    try:
        file_path = f'gg{year}.json'
        
        with open(file_path, 'r') as f:
            tweets = json.load(f)

        filtered_text_only = set()
        filtered_tweets_full = []

        for tweet in tweets:
            processed_text = preprocess_tweet(tweet['text'])
            if any(phrase in processed_text for phrase in WINNING_PHRASES):
                filtered_text_only.add(processed_text)

                tweet['text'] = processed_text
                filtered_tweets_full.append(tweet)

        unique_filtered_texts = list(filtered_text_only)

        with open('./resFiles/firstpass.json', 'w') as f:
            json.dump(unique_filtered_texts, f, indent=4)

        print(f"@@ FIRSTPASS COMPLETE FOR {year}!!")

    except FileNotFoundError:
        print(f"Error: Dataset for year {year} not found.")

if __name__ == "__main__":
    run_firstpass(2013)
