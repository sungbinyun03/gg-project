import re
import json
import spacy
from imdb import Cinemagoer
from rapidfuzz import fuzz

# Initialize IMDbPY object, SpaCy model, and cache
ia = Cinemagoer()
nlp = spacy.load("en_core_web_trf")
imdb_cache = {}

# Load tweets from JSON file
with open('../resFiles/firstpass.json', 'r') as f:
    tweets = json.load(f)

# Keywords for filtering
keywords = re.compile(r"should have won|is nominated|was nominated", re.IGNORECASE)

# Filter tweets containing specified phrases
filtered_tweets = [tweet for tweet in tweets if keywords.search(tweet)]

# Extract potential media entities
entities = []
for tweet in filtered_tweets:
    doc = nlp(tweet)
    # Filter only for entities labeled as WORK_OF_ART or ORG
    entities.extend([ent.text for ent in doc.ents if ent.label_ in {"WORK_OF_ART", "ORG"}])

# Remove duplicates by converting to a set and back to a list
unique_entities = list(set(entities))

# Dictionary to store categorized results (only media)
results = {"Media": []}

# Helper function to classify entities as media, with caching
def classify_media_entity(entity):
    # Check cache first
    if entity in imdb_cache:
        return imdb_cache[entity]
    
    try:
        # Search IMDb for movies and check top result similarity
        media_results = ia.search_movie(entity)
        if media_results:
            imdb_media_title = media_results[0]['title']
            # print("@@@@@: ", media_results[0].keys())
            similarity_score = fuzz.ratio(entity.lower(), imdb_media_title.lower())
            if similarity_score >= 90:
                imdb_cache[entity] = [imdb_media_title,media_results[0]['kind'], media_results[0]['year']]   # Cache the result
                return [imdb_media_title,media_results[0]['kind'], media_results[0]['year']]
    except Exception as e:
        print(f"Error encountered for entity '{entity}': {e}")
    
    # Cache as None if no match found, to skip in future checks
    imdb_cache[entity] = None
    return None

# Classify each unique entity as media if it passes IMDb check
for entity in unique_entities:
    media = classify_media_entity(entity)
    if media:
        results["Media"].append(media)

# Save results and cache
with open('../resFiles/shouldHaves_media_only.json', 'w') as f:
    json.dump(results, f, indent=4)
with open('../resFiles/imdb_cache.json', 'w') as cache_file:
    json.dump(imdb_cache, cache_file, indent=4)

print("Media entities saved to shouldHaves_media_only.json")
