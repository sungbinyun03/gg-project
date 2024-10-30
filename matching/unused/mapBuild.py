import json
import spacy
from collections import defaultdict
import gender_guesser.detector as gender


nlp = spacy.load("en_core_web_trf")
d = gender.Detector()

with open('../resFiles/matched_people.json', 'r') as f:
    matched_people = json.load(f)

correlation_mapping = defaultdict(int)

people_keys = set(matched_people.keys())

for person, tweets in matched_people.items():
    for tweet in tweets:
        doc = nlp(tweet)
        tweet_people = set()
        for ent in doc.ents:
            if ent.label_ == "PERSON" and ent.text in people_keys:
                tweet_people.add(ent.text)

        # For each co-occurrence of people in the tweet, increment the weight in correlation mapping
        for other_person in tweet_people:
            if other_person != person:
                person_pair = "-".join(sorted([person, other_person]))
                correlation_mapping[person_pair] += 1


print(json.dumps(correlation_mapping, indent=4))

for pair, weight in correlation_mapping.items():
    parts = pair.split("-")
    name1 = parts[0].strip()
    name2 = "-".join(parts[1:]).strip()

    gender1 = d.get_gender(name1.split()[0]) 
    gender2 = d.get_gender(name2.split()[0])

    valid_genders = {"male", "female"} 
    if gender1 in valid_genders and gender1 == gender2:
        correlation_mapping[pair] = weight



with open('correlation_mapping.json', 'w') as f:
    json.dump(correlation_mapping, f, indent=4)

print("Correlation mapping completed. Results saved to correlation_mapping.json.")
