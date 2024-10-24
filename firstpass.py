import json
import re
from collections import Counter


winning_phrases = [' win ', 'WIN', 'WINS', 'WON', 'Wins', 'Win', 'Nominated', 'Winner', 
 ' won ', ' winner ', ' wins ', ' awarded ', ' takes', ' got ', ' nom', ' nominated ', ]

def preprocess_tweet(tweet_text):
    tweet_text = re.sub(r"http\S+|www\S+|https\S+", '', tweet_text)  # Remove URLs
    tweet_text = re.sub(r'@(\w+)', r'\1', tweet_text)  # Remove the '@' sign but keep the mention
    tweet_text = re.sub(r'\#\w+', '', tweet_text)  # Remove hashtags
    tweet_text = re.sub(r'[^A-Za-z0-9 ]+', '', tweet_text)  # Remove non-alphanumeric characters
    # tweet_text = tweet_text.lower()  # Convert to lowercase
    return tweet_text


with open('gg2013.json', 'r') as f:
    tweets = json.load(f)

tweets_text = [preprocess_tweet(tweet['text']) for tweet in tweets]
filtered_tweets = [tweet for tweet in tweets_text if any(phrase in tweet for phrase in winning_phrases)]
unique_filtered_tweets = list(set(filtered_tweets))

with open('firstpass.json', 'w') as f:
    json.dump(unique_filtered_tweets, f, indent=4)

print(f"total tweets: {len(tweets)}")
print(f"Total filtered tweets: {len(filtered_tweets)}")


with open('firstpass.json', 'r') as f:
    tweets = json.load(f)

tweet_counts = Counter(tweets)

sorted_tweets = sorted(tweet_counts.items(), key=lambda x: x[1], reverse=True)

with open('sorted_tweets_by_frequency.json', 'w') as f:
    json.dump(sorted_tweets, f, indent=4)


    