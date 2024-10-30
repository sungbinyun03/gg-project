import re
from rapidfuzz import fuzz
import json
import spacy
import gender_guesser.detector as gender
from imdb import IMDb

# Initialize gender detector and spaCy NLP model
detector = gender.Detector()
nlp = spacy.load("en_core_web_sm")
ia = IMDb()
# List of official awards with gendered categories
OFFICIAL_AWARDS = [
    'best actress in a motion picture - drama',
    'best actor in a motion picture - drama',
    'best actress in a motion picture - comedy or musical',
    'best actor in a motion picture - comedy or musical',
    'best actress in a supporting role in a motion picture',
    'best actor in a supporting role in a motion picture',
    'best director - motion picture',
    'best original score - motion picture',
    'best actress in a television series - drama',
    'best actor in a television series - drama',
    'best actress in a television series - comedy or musical',
    'best actor in a television series - comedy or musical',
    'best actress in a mini-series or motion picture made for television',
    'best actor in a mini-series or motion picture made for television',
    'best actress in a supporting role in a series, mini-series or motion picture made for television',
    'best actor in a supporting role in a series, mini-series or motion picture made for television'
]

# Synonyms for common terms in award names
AWARD_SYNONYMS = {
    'television': ['television', 'tv'],
    'motion picture': ['motion picture', 'film', 'movie'],
    'series': ['series', 'show'],
    'mini-series': ['mini-series', 'limited series']
}


POSITIVE_PHRASES = {
    r'\bwins\b.*\bBest\b': 3, r'\bawarded\b.*\bfor\b': 3,
    r'\bwon\b.*\baward\b': 3, r'\btakes home\b': 3,
    r'\breceives\b.*\baward\b': 2, r'\bbest\b.*\bgoes to\b': 3,
    r'\bwins everything\b': 2, r'\bhigh fives\b.*\bafter win\b': 2,
    r'\bGolden Globe winner\b': 3, r'\bso proud\b.*\baward\b': 1,
    r'\bdeserves\b.*\baward\b': 1, r'\bcongratulations\b.*\bnominated\b': 1,
    r'\bshould win\b': 1
}

NEGATIVE_PHRASES = {
    r'\bdidn\'t win\b': -3, r'\blost\b.*\baward\b': -2,
    r'\brobbed\b': -2, r'\bshould have won\b': -1,
    r'\bdeserved\b.*\bwin\b': -1, r'\bso sad\b.*\bdeserved to win\b': -1,
    r'\bwas hoping\b.*\bto win\b': -1, r'\bnever wins\b': -2
}


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
                    if person not in categorized_awards[best_match]:
                        categorized_awards[best_match][person] = []
                    categorized_awards[best_match][person].append(tweet)
    return categorized_awards

def calculate_win_score(categorized_awards):
    awards_dict = {award: [] for award in OFFICIAL_AWARDS}
    for award, people in categorized_awards.items():
        for person, tweets in people.items():
            total_score, max_score = 0, len(tweets) * 3
            for tweet in tweets:
                tweet_score = sum(weight for phrase, weight in POSITIVE_PHRASES.items() if re.search(phrase, tweet, re.IGNORECASE))
                tweet_score += sum(weight for phrase, weight in NEGATIVE_PHRASES.items() if re.search(phrase, tweet, re.IGNORECASE))
                total_score += tweet_score
            awards_dict[award].append((person, total_score))
    return awards_dict

def correct_gender_award(awards_dict):
    corrected_awards_dict = {award: [] for award in OFFICIAL_AWARDS}
    for award, winners in awards_dict.items():
        for person, score in winners:
            guessed_gender = detector.get_gender(person.split()[0])
            if 'actress' in award and guessed_gender in ['male', 'mostly_male']:
                corrected_award = award.replace('actress', 'actor')
            elif 'actor' in award and guessed_gender in ['female', 'mostly_female']:
                corrected_award = award.replace('actor', 'actress')
            else:
                corrected_award = award
            corrected_awards_dict[corrected_award].append((person, score))
    return corrected_awards_dict

# Separate function to identify likely nominees based on "should have won" mentions
def find_likely_nominees(matched_people):
    likely_nominees = {}
    for person, tweets in matched_people.items():
        should_have_won_tweets = [tweet for tweet in tweets if re.search(r'\bshould have won\b', tweet, re.IGNORECASE)]
        if should_have_won_tweets:
            likely_nominees[person] = {
                "count": len(should_have_won_tweets),
                "tweets": should_have_won_tweets
            }
    # Order nominees by mention count
    return dict(sorted(likely_nominees.items(), key=lambda item: item[1]["count"], reverse=True))


def is_actor_on_imdb(name):
    # Clean the nominee's name
    cleaned_name = name.lower().strip()
    
    search_results = ia.search_person(cleaned_name)
    
    if search_results:
        imdb_person = search_results[0]
        imdb_person_name = imdb_person['name'].lower().strip()
        
        similarity_score = fuzz.ratio(cleaned_name, imdb_person_name)
        
        if similarity_score > 80:
           return search_results[0]['name']
    return None

# Main flow to filter nominees who are confirmed actors



def main():
    # Load matched people data from JSON file
    with open('../resFiles/people.json', 'r') as f:
        matched_people = json.load(f)

    # Step 1: Categorize by award mention
    categorized_awards = categorize_by_award(matched_people)
    
    # Step 2: Calculate win scores based on positive/negative phrases
    awards_dict = calculate_win_score(categorized_awards)
    
    # Step 3: Correct gender misplacements
    awards_dict = correct_gender_award(awards_dict)
    print("Awards organized with likely winners and others!")

    # Save organized award results to a JSON file
    organized_awards = {}
    # Determine the likely winner with a gender check
    for award, nominees in awards_dict.items():
        # Determine the likely winner based on the highest score
        likely_winner = max(nominees, key=lambda x: x[1], default=(None, 0))[0]
        likely_winner = is_actor_on_imdb(likely_winner)        
        # Check the gender of the likely winner
        guessed_gender = detector.get_gender(likely_winner.split()[0]) if likely_winner else None
        expected_gender = 'female' if 'actress' in award else 'male' if 'actor' in award else None
        
        # Ensure gender alignment for likely winner
        if guessed_gender and expected_gender:
            if ('female' in guessed_gender and expected_gender == 'male') or ('male' in guessed_gender and expected_gender == 'female'):
                # Move the incorrectly gendered winner to the corresponding award category
                corrected_award = award.replace('actress', 'actor') if expected_gender == 'female' else award.replace('actor', 'actress')
                
                # Initialize corrected award list if it doesn’t already exist
                if corrected_award not in organized_awards:
                    organized_awards[corrected_award] = {"likely winner": None, "others": []}
                    
                # Assign the mismatched likely winner to the corrected award's "others"
                organized_awards[corrected_award]["others"].append(likely_winner)
                
                # Update the likely winner for the original award with the next top-scoring candidate matching the expected gender
                likely_winner = None
                for nominee, score in sorted(nominees, key=lambda x: x[1], reverse=True):
                    nominee_gender = detector.get_gender(nominee.split()[0])
                    if (expected_gender == 'female' and 'female' in nominee_gender) or (expected_gender == 'male' and 'male' in nominee_gender):
                        likely_winner = nominee
                        likely_winner_score = score
                        break
        
        # Populate the organized awards dictionary with the final winner and others
        organized_awards[award] = {
            "likely winner": likely_winner,
        }


    with open('../resFiles/organized_awards_noMatching.json', 'w') as f:
        json.dump(organized_awards, f, indent=4)


    # Step 4: Separately identify likely nominees based on "should have won" mentions
    likely_nominees = find_likely_nominees(matched_people)
    confirmed_actors = {}
    for nominee, data in likely_nominees.items():
        # Check if the name is confirmed as an actor on IMDb
        imdb_name = is_actor_on_imdb(nominee)

        if imdb_name:
            confirmed_actors[imdb_name] = data

    for person, d in confirmed_actors.items():
        if person in matched_people:
            for tweet in matched_people[person]:
                d['tweets'].append(tweet)

    with open('../resFiles/likely_nominees.json', 'w') as f:
        json.dump(confirmed_actors, f, indent=4)
    
    print("Likely nominees saved separately based on 'should have won' mentions.")

# Execute the main function
if __name__ == "__main__":
    main()