import json
import spacy
from collections import defaultdict

# Load SpaCy's English language model
nlp = spacy.load("en_core_web_trf")

# Load tweets from firstpass.json
with open('../resFiles/firstpass.json', 'r') as f:
    tweets = json.load(f)

# Dictionaries to store people entities and other entities
people_tweets = defaultdict(list)
other_entities_tweets = defaultdict(list)

# Process each tweet with SpaCy to identify entities
for tweet in tweets:
    doc = nlp(tweet)
    people_in_tweet = set()
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            people_in_tweet.add(ent.text)  # Track all person entities in this tweet
            people_tweets[ent.text].append(tweet)  # Append tweet to each person entity's list
        else:
            other_entities_tweets[ent.text].append(tweet)  # Append tweet to other entity's list
    
    # If there are multiple people, append tweet to each one’s list
    for person in people_in_tweet:
        people_tweets[person].append(tweet)

# Sort the dictionaries by the length of the list of tweets for each entity, in descending order
sorted_people_tweets = dict(sorted(people_tweets.items(), key=lambda item: len(item[1]), reverse=True))
sorted_other_entities_tweets = dict(sorted(other_entities_tweets.items(), key=lambda item: len(item[1]), reverse=True))

# Save the sorted dictionaries to JSON files
with open('../resFiles/people.json', 'w') as f:
    json.dump(sorted_people_tweets, f, indent=4)

with open('../resFiles/other_entities.json', 'w') as f:
    json.dump(sorted_other_entities_tweets, f, indent=4)

print("Entity extraction, tweet aggregation, and sorting completed. Results saved to sorted_people_tweets.json and sorted_other_entities_tweets.json")
