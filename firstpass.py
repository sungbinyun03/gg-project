import json
import re
from collections import Counter


winning_phrases = [' win ', ' won ', ' winner ', ' wins ', ' awarded ']

def preprocess_tweet(tweet_text):
    tweet_text = re.sub(r"http\S+|www\S+|https\S+", '', tweet_text)
    tweet_text = re.sub(r'\@\w+|\#\w+', '', tweet_text)
    tweet_text = re.sub(r'[^A-Za-z0-9 ]+', '', tweet_text)
    tweet_text = tweet_text.lower()
    return tweet_text


with open('gg2013.json', 'r') as f:
    tweets = json.load(f)

tweets_text = [preprocess_tweet(tweet['text']) for tweet in tweets]
filtered_tweets = [tweet for tweet in tweets_text if any(phrase in tweet for phrase in winning_phrases)]

with open('firstpass.json', 'w') as f:
    json.dump(filtered_tweets, f, indent=4)

print(f"Total filtered tweets: {len(filtered_tweets)}")


with open('firstpass.json', 'r') as f:
    tweets = json.load(f)

tweet_counts = Counter(tweets)

sorted_tweets = sorted(tweet_counts.items(), key=lambda x: x[1], reverse=True)

with open('sorted_tweets_by_frequency.json', 'w') as f:
    json.dump(sorted_tweets, f, indent=4)

for tweet, count in sorted_tweets:
    print(f"{tweet}: {count}")
    