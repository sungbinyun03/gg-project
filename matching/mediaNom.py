import json
import re
from collections import defaultdict
import spacy
from .constants import AWARD_CATEGORIES, ADDITIONAL_AWARD_KEYWORDS


nlp = spacy.load("en_core_web_sm")

def extract_core_entity(entity_text, award_keyword):
    cleaned_entity = re.sub(rf"\b{award_keyword}\b", '', entity_text, flags=re.IGNORECASE).strip()
    cleaned_entity = re.sub(r"(for|motion picture|best)", '', cleaned_entity, flags=re.IGNORECASE).strip()
    return cleaned_entity

def extract_top_entities(tweets, keyword):
    entity_counts = defaultdict(int)
    keyword_pattern = re.compile(rf"\b{keyword}\b", re.IGNORECASE)
    
    for tweet in tweets:
        if keyword_pattern.search(tweet):
            doc = nlp(tweet)
            for ent in doc.ents:
                if ent.label_ in ["WORK_OF_ART", "ORG"]:
                    core_entity = extract_core_entity(ent.text, keyword)
                    if core_entity:
                        entity_counts[core_entity] += 1
    
    sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return [ent for ent, count in sorted_entities]

def get_media_nom():
    top_nominees = {}
    with open('./resFiles/categorized_media.json', 'r') as f:
        media_data = json.load(f)
    with open('./resFiles/firstpass.json', 'r') as f:
        tweets = json.load(f)

    for award, titles in AWARD_CATEGORIES.items():
        if titles:
            mention_counts = []
            unique_titles = {title.strip() for title in titles}
            for title in unique_titles:
                mentions = sum(1 for tweet in tweets if re.search(rf"\b{re.escape(title)}\b", tweet, re.IGNORECASE))
                mention_counts.append((title, mentions))
            sorted_nominees = sorted(mention_counts, key=lambda x: x[1], reverse=True)[:5]
            top_nominees[award] = [title for title, mentions in sorted_nominees]
        else:
            keyword = ADDITIONAL_AWARD_KEYWORDS.get(award, "")
            if keyword:
                top_nominees[award] = extract_top_entities(tweets, keyword)
    top_nominees["best mini-series or motion picture made for television"] = []
    with open('./resFiles/media_nominees.json', 'w') as f:
        json.dump(top_nominees, f, indent=4)
    print("@@@@PEOPLE NOM DONE!!!")


if __name__ == "__main__":
    get_media_nom()
