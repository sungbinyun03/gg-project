import json
import re
from collections import Counter

# Winning phrases to look for
winning_phrases = [' win ', 'WIN', 'WINS', 'WON', 'Wins', 'Win', 'Nominated', 'Winner', 
                   ' won ', ' winner ', ' wins ', ' awarded ', ' takes', ' got ', ' nom', ' nominated ']

def preprocess_tweet(tweet_text):
    tweet_text = re.sub(r"http\S+|www\S+|https\S+", '', tweet_text)  # Remove URLs
    tweet_text = re.sub(r'@(\w+)', r'\1', tweet_text)  # Remove the '@' sign but keep the mention
    tweet_text = re.sub(r'\#\w+', '', tweet_text)  # Remove hashtags
    tweet_text = re.sub(r'[^A-Za-z0-9 ]+', '', tweet_text)  # Remove non-alphanumeric characters
    
    # Add ")" after the next word following "RT"
    tweet_text = re.sub(r'(RT\s+\w+)', r'\1)', tweet_text)
    
    return tweet_text

# Load original tweets from gg2013.json
with open('gg2013.json', 'r') as f:
    tweets = json.load(f)

# Preprocess, filter, and store tweets for first pass and timestamped pass
filtered_text_only = set()  # To collect unique texts for `firstpass.json`
filtered_tweets_full = []  # To store full tweet structure for `firstpass_timeStamp.json`

for tweet in tweets:
    processed_text = preprocess_tweet(tweet['text'])
    if any(phrase in processed_text for phrase in winning_phrases):
        # Add preprocessed text to set for `firstpass.json`
        filtered_text_only.add(processed_text)

        # Add entire tweet with timestamp for sorting
        tweet['text'] = processed_text  # Update text to preprocessed version
        filtered_tweets_full.append(tweet)

# Convert filtered_text_only set to a list and remove duplicates
unique_filtered_texts = list(filtered_text_only)

# Sort the filtered full tweets by timestamp_ms
sorted_filtered_tweets_full = sorted(filtered_tweets_full, key=lambda x: x['timestamp_ms'])

# Save results to JSON
# with open('./resFiles/firstpass.json', 'w') as f:
#     json.dump(unique_filtered_texts, f, indent=4)

with open('./resFiles/firstpass_timeStamp.json', 'w') as f:
    json.dump(sorted_filtered_tweets_full, f, indent=4)

print(f"Total tweets: {len(tweets)}")
print(f"Total filtered tweets: {len(filtered_tweets_full)}")
print(f"Total unique filtered texts: {len(unique_filtered_texts)}")
