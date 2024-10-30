import json
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

def extract_top_hosts(tweets):
    person_counter = Counter()

    for text in tweets:  
        if "hosts" in text.lower():  
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    person_counter[ent.text] += 1

    top_hosts = person_counter.most_common(2)
    return [host[0] for host in top_hosts]

with open("../resFiles/firstpass.json", "r") as f:
    tweets = json.load(f)

top_hosts = extract_top_hosts(tweets)

print("Top hosts:", top_hosts)
