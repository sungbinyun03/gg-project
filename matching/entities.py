import json
import spacy
from collections import defaultdict

nlp = spacy.load("en_core_web_trf")
def extract_entities():
    with open('./resFiles/firstpass.json', 'r') as f:
        tweets = json.load(f)

    people_tweets = defaultdict(list)
    other_entities_tweets = defaultdict(list)

    for tweet in tweets:
        doc = nlp(tweet)
        people_in_tweet = set()
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                people_in_tweet.add(ent.text)  
                people_tweets[ent.text].append(tweet)  
            else:
                other_entities_tweets[ent.text].append(tweet)  
        
        for person in people_in_tweet:
            people_tweets[person].append(tweet)

    sorted_people_tweets = dict(sorted(people_tweets.items(), key=lambda item: len(item[1]), reverse=True))

    with open('./resFiles/people.json', 'w') as f:
        json.dump(sorted_people_tweets, f, indent=4)

    print("@@@@ Entity extraction completed!!!")

if __name__ == "__main__":
    extract_entities()