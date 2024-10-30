import spacy
import gender_guesser.detector as gender
from imdb import Cinemagoer, IMDbDataAccessError
from rapidfuzz import fuzz
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import time

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize gender detector and Cinemagoer
ia = Cinemagoer()

# Load tweets
with open('firstpass.json', 'r') as f:
    tweets = json.load(f)

# Cache to store previously seen tokens and their classifications (loaded from file)
cache_file = 'classification_cache.json'
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        classification_cache = json.load(f)
else:
    classification_cache = {}

entities_dict = defaultdict(list)
media_dict = defaultdict(list)
etc = defaultdict(list)

skipped_movie_queries = 0

def clean_name(name):
    # Remove any non-alphanumeric characters, and filter short or malformed names
    return ' '.join(word for word in name.split() if word.isalpha() and len(word) > 1)

def get_full_name(name):
    if name in classification_cache:
        return classification_cache[name]

    cleaned_name = clean_name(name)
    if not cleaned_name:
        classification_cache[name] = None
        return None
    
    attempts = 0
    while attempts < 3:
        try:
            people = ia.search_person(cleaned_name)
            if people:
                full_name = people[0]['name']
                classification_cache[name] = full_name  # Cache the result
                return full_name
            classification_cache[name] = None  # Cache as None if not found
            return None
        except IMDbDataAccessError as e:
            print(f"Error accessing IMDb for name '{cleaned_name}': {e}")
            attempts += 1
            time.sleep(2 ** attempts)  # Exponential backoff
            if attempts >= 3:
                print(f"Skipping name '{cleaned_name}' after 3 failed attempts.")
                classification_cache[name] = None  # Cache as None on failure
                return None

def get_full_movie_title(title):
    global skipped_movie_queries
    if title in classification_cache:
        return classification_cache[title]
    
    attempts = 0
    while attempts < 2:
        try:
            movies = ia.search_movie(title)
            if movies:
                full_title = movies[0]['title']
                classification_cache[title] = full_title  # Cache the result
                return full_title
            classification_cache[title] = None  # Cache as None if not found
            return None
        except IMDbDataAccessError as e:
            print(f"Error accessing IMDb for title '{title}': {e}")
            attempts += 1
            time.sleep(2 ** attempts)  # Exponential backoff
            if attempts >= 2:
                print(f"Skipping title '{title}' after 2 failed attempts.")
                skipped_movie_queries += 1
                classification_cache[title] = None  # Cache as None on failure
                return None

def match_person_with_fuzz(noun):
    if noun in classification_cache:
        return classification_cache[noun]
    
    print("matching", noun)
    full_name = get_full_name(noun)
    print("full name:", full_name)
    if full_name:
        similarity_score = fuzz.ratio(noun, full_name.lower())
        print("@@@@ SCORE", similarity_score)
        if similarity_score > 60: 
            classification_cache[noun] = full_name  # Cache the result
            return full_name

    print("returning none")
    classification_cache[noun] = None  # Cache as None if not a match
    return None

def process_tweet_batch(tweets_batch):
    local_entities_dict = defaultdict(list)
    local_media_dict = defaultdict(list)

    for tweet in tweets_batch:
        doc = nlp(tweet)
        tokens = list(doc)
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if (token.pos_ == "PROPN" and i + 1 < len(tokens) and tokens[i + 1].pos_ == "PROPN"
                and (token.dep_ == "nsubj" or tokens[i + 1].dep_ == "nsubj")):
                full_name_candidate = f"{token.text} {tokens[i + 1].text}"
                if full_name_candidate in classification_cache and classification_cache[full_name_candidate] is not None:
                    local_entities_dict[classification_cache[full_name_candidate]].append(tweet)
                    i += 2
                    continue
                
                possible_person = match_person_with_fuzz(full_name_candidate)
                if possible_person:
                    local_entities_dict[possible_person].append(tweet)
                    classification_cache[full_name_candidate] = possible_person
                    i += 2
                    continue
            
            if token.pos_ == "PROPN" and token.dep_ == "nsubj":
                if token.text in classification_cache and classification_cache[token.text] is not None:
                    local_entities_dict[classification_cache[token.text]].append(tweet)
                else:
                    possible_person = match_person_with_fuzz(token.text)
                    if possible_person:
                        local_entities_dict[possible_person].append(tweet)
                    else:
                        full_title = get_full_movie_title(token.text)
                        if full_title:
                            local_media_dict[full_title].append(tweet)
            i += 1

    return local_entities_dict, local_media_dict

# Distribute tweets among multiple threads for parallel processing
def process_tweets_in_parallel(tweets, batch_size=50):
    results = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(process_tweet_batch, tweets[i:i + batch_size]) for i in range(0, len(tweets), batch_size)]
        for future in as_completed(futures):
            results.append(future.result())

    # Consolidate results from all threads
    for local_entities_dict, local_media_dict in results:
        for key, value in local_entities_dict.items():
            entities_dict[key].extend(value)
        for key, value in local_media_dict.items():
            media_dict[key].extend(value)

# Process tweets in parallel
process_tweets_in_parallel(tweets)

# Save updated cache to file
with open(cache_file, 'w') as f:
    json.dump(classification_cache, f)

# Output results
# print("Entities:", dict(entities_dict))
# print("Media:", dict(media_dict))
# print(f"Total skipped IMDb queries: {skipped_movie_queries}")

# Save results to JSON file
with open('classified_entities.json', 'w') as f:
    json.dump({
        "Entities": dict(entities_dict),
        "Media": dict(media_dict),
        "SkippedIMDbQueries": skipped_movie_queries
    }, f, indent=4)
