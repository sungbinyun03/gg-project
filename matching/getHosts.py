import json
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

def extract_top_hosts(tweets):
    
    """Extract the top two most mentioned hosts in tweets containing 'hosts'."""
    person_counter = Counter()

    for text in tweets:  
        if "hosts" in text.lower():  
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    person_counter[ent.text] += 1

    top_hosts = person_counter.most_common(2)
    return [host[0] for host in top_hosts]
