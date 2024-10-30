import json
from imdb import IMDb
from fuzzywuzzy import fuzz
from collections import defaultdict
import time

# Initialize IMDbPY object
ia = IMDb()

# Load the people.json dictionary
with open('../resFiles/people.json', 'r') as f:
    people_dict = json.load(f)

# Dictionary to store matched results
matched_people = defaultdict(list)
unmatched = defaultdict(list)

# Helper function to retry IMDb queries
def safe_imdb_search(search_function, query, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            return search_function(query)
        except Exception as e:
            print(f"Error searching IMDb for '{query}': {e}")
            retries += 1
            time.sleep(1)  # Wait 1 second between retries
    print(f"Skipping '{query}' after {max_retries} failed attempts.")
    return None

# Threshold for people count
target_people_count = 100

# Process each name in people.json until we reach the target count
for name, tweets in people_dict.items():
    if len(matched_people) >= target_people_count:
        break  # Stop searching once the people target is reached

    cleaned_name = name.strip().lower()
    
        # Multi-word names or names that do not match an existing full name follow the regular flow
    if len(matched_people) < target_people_count:
        people = safe_imdb_search(ia.search_person, cleaned_name)
        if people:
            imdb_person_name = people[0]['name']
            similarity_score = fuzz.ratio(cleaned_name, imdb_person_name.lower())
            print(f"@@@@ SCORE (Person) {similarity_score} for {name} -> IMDb Name: {imdb_person_name}")

            if similarity_score >= 70:
                matched_people[imdb_person_name].extend(tweets)
                continue  # Skip to the next name if matched with a person

    # If neither match is close enough, add to unmatched
    unmatched[name] = tweets

# Save the results to JSON files
with open('../resFiles/matched_people.json', 'w') as f:
    json.dump(matched_people, f, indent=4)

with open('../resFiles/unmatched.json', 'w') as f:
    json.dump(unmatched, f, indent=4)

print("Matching completed. Results saved to matched_people.json and unmatched.json.")
