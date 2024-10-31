import re
from rapidfuzz import fuzz
import json
import spacy
import gender_guesser.detector as gender
from imdb import IMDb
from .constants import OFFICIAL_AWARDS, AWARD_SYNONYMS, POSITIVE_PHRASES, NEGATIVE_PHRASES

# Initialize resources
detector = gender.Detector(case_sensitive=False)
nlp = spacy.load("en_core_web_sm", disable=["parser", "tagger", "lemmatizer"])
ia = IMDb()

# Load IMDb cache
try:
    with open('imdb_cache.json', 'r') as f:
        imdb_cache = json.load(f)
except FileNotFoundError:
    imdb_cache = {}

def expand_award_names(award):
    expanded_awards = [award]
    for term, synonyms in AWARD_SYNONYMS.items():
        for synonym in synonyms:
            if term in award:
                expanded_awards.append(award.replace(term, synonym))
    return expanded_awards

def categorize_by_award(matched_people):
    categorized_awards = {award: {} for award in OFFICIAL_AWARDS}
    for person, tweets in matched_people.items():
        for tweet in tweets:
            if 'best' in tweet.lower():
                match = re.search(r'\bbest\b', tweet, re.IGNORECASE)
                if match:
                    start_index = match.end()
                    following_text = ' '.join(tweet[start_index:].split()[:10])
                    best_match, best_score = None, 0
                    for award in OFFICIAL_AWARDS:
                        for expanded_award in expand_award_names(award):
                            similarity = fuzz.partial_ratio(following_text.lower(), expanded_award.lower())
                            if similarity > best_score:
                                best_score, best_match = similarity, award
                    if best_score > 70 and best_match:
                        categorized_awards[best_match].setdefault(person, []).append(tweet)
    return categorized_awards

# Pre-compile regex patterns
POSITIVE_PATTERNS = [(re.compile(phrase, re.IGNORECASE), weight) for phrase, weight in POSITIVE_PHRASES.items()]
NEGATIVE_PATTERNS = [(re.compile(phrase, re.IGNORECASE), weight) for phrase, weight in NEGATIVE_PHRASES.items()]

def calculate_win_score(categorized_awards):
    awards_dict = {award: [] for award in OFFICIAL_AWARDS}
    for award, people in categorized_awards.items():
        for person, tweets in people.items():
            total_score = 0
            for tweet in tweets:
                tweet_score = sum(weight for pattern, weight in POSITIVE_PATTERNS if pattern.search(tweet))
                tweet_score += sum(weight for pattern, weight in NEGATIVE_PATTERNS if pattern.search(tweet))
                total_score += tweet_score
            awards_dict[award].append((person, total_score))
    return awards_dict

def correct_gender_award(awards_dict):
    corrected_awards_dict = {award: [] for award in OFFICIAL_AWARDS}
    gender_cache = {}
    for award, winners in awards_dict.items():
        for person, score in winners:
            if person in gender_cache:
                guessed_gender = gender_cache[person]
            else:
                guessed_gender = detector.get_gender(person.split()[0])
                gender_cache[person] = guessed_gender
            if 'actress' in award and guessed_gender in ['male', 'mostly_male']:
                corrected_award = award.replace('actress', 'actor')
            elif 'actor' in award and guessed_gender in ['female', 'mostly_female']:
                corrected_award = award.replace('actor', 'actress')
            else:
                corrected_award = award
            corrected_awards_dict[corrected_award].append((person, score))
    return corrected_awards_dict

def is_actor_on_imdb(name):
    # Clean the nominee's name
    cleaned_name = name.lower().strip()
    if cleaned_name in imdb_cache:
        return imdb_cache[cleaned_name]
    search_results = ia.search_person(cleaned_name)
    if search_results:
        imdb_person = search_results[0]
        imdb_person_name = imdb_person['name'].lower().strip()
        similarity_score = fuzz.ratio(cleaned_name, imdb_person_name)
        if similarity_score > 80:
            imdb_cache[cleaned_name] = imdb_person['name']
            return imdb_person['name']
    imdb_cache[cleaned_name] = None
    return None

def find_likely_nominees(matched_people):
    likely_nominees = {}
    for person, tweets in matched_people.items():
        unique_tweets = list(set(tweets))  # Process unique tweets only
        should_have_won_tweets = []
        linked_persons = {}
        # Batch process tweets
        docs = nlp.pipe(unique_tweets)
        for tweet, doc in zip(unique_tweets, docs):
            entities = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
            # Existing criterion: "should have won"
            if re.search(r'\bshould have won\b', tweet, re.IGNORECASE):
                should_have_won_tweets.append(tweet)
                # Record all other persons as linked persons
                other_persons = [name for name in entities if name.lower() != person.lower()]
                linked_persons.setdefault(person, set()).update(other_persons)
            elif re.search(r'\b(to win|over)\b', tweet, re.IGNORECASE):
                if person.lower() in [n.lower() for n in entities]:
                    should_have_won_tweets.append(tweet)
                    other_names = [n for n in entities if n.lower() != person.lower()]
                    linked_persons.setdefault(person, set()).update(other_names)
        if should_have_won_tweets:
            likely_nominees.setdefault(person, {"count": 0, "tweets": [], "linked person": set()})
            likely_nominees[person]["count"] += len(should_have_won_tweets)
            likely_nominees[person]["tweets"].extend(should_have_won_tweets)
            if person in linked_persons:
                likely_nominees[person]["linked person"].update(linked_persons[person])
    # Convert sets to lists for JSON serialization
    for nominee in likely_nominees.values():
        nominee["linked person"] = list(nominee["linked person"])
    return dict(sorted(likely_nominees.items(), key=lambda item: item[1]["count"], reverse=True))

def Winners():
    with open('./resFiles/people.json', 'r') as f:
        matched_people = json.load(f)

    categorized_awards = categorize_by_award(matched_people)
    
    awards_dict = calculate_win_score(categorized_awards)
    
    awards_dict = correct_gender_award(awards_dict)
    print("Awards organized with likely winners and others!")

    organized_awards = {}
    for award, nominees in awards_dict.items():
        likely_winner = max(nominees, key=lambda x: x[1], default=(None, 0))[0]
        if likely_winner:
            likely_winner_imdb = is_actor_on_imdb(likely_winner)
            if likely_winner_imdb:
                likely_winner = likely_winner_imdb
        guessed_gender = detector.get_gender(likely_winner.split()[0]) if likely_winner else None
        expected_gender = 'female' if 'actress' in award else 'male' if 'actor' in award else None

        if guessed_gender and expected_gender:
            if ('female' in guessed_gender and expected_gender == 'male') or ('male' in guessed_gender and expected_gender == 'female'):
                corrected_award = award.replace('actress', 'actor') if expected_gender == 'female' else award.replace('actor', 'actress')
                if corrected_award not in organized_awards:
                    organized_awards[corrected_award] = {"likely winner": None}
                likely_winner = None
                for nominee, score in sorted(nominees, key=lambda x: x[1], reverse=True):
                    nominee_gender = detector.get_gender(nominee.split()[0])
                    if (expected_gender == 'female' and 'female' in nominee_gender) or (expected_gender == 'male' and 'male' in nominee_gender):
                        likely_winner = nominee
                        break

        organized_awards[award] = {
            "likely winner": likely_winner,
        }

    with open('./resFiles/organized_awards.json', 'w') as f:
        json.dump(organized_awards, f, indent=4)

    likely_nominees = find_likely_nominees(matched_people)
    confirmed_actors = {}
    for nominee, data in likely_nominees.items():
        imdb_name = is_actor_on_imdb(nominee)
        if imdb_name:
            data['imdb_name'] = imdb_name
            confirmed_actors[imdb_name] = data

    for person, d in confirmed_actors.items():
        if person in matched_people:
            for tweet in matched_people[person]:
                if tweet not in d['tweets']:
                    d['tweets'].append(tweet)
                    d['count'] += 1

    for data in confirmed_actors.values():
        linked_persons = set()
        for name in data.get('linked person', []):
            imdb_name = is_actor_on_imdb(name)
            if imdb_name:
                linked_persons.add(imdb_name)
        data['linked person'] = list(linked_persons)

    with open('./resFiles/likely_nominees.json', 'w') as f:
        json.dump(confirmed_actors, f, indent=4)
    
    # Save IMDb cache
    with open('imdb_cache.json', 'w') as f:
        json.dump(imdb_cache, f)
    
    print("WIN PROB DONE")

if __name__ == "__main__":
    Winners()
