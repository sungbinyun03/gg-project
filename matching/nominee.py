import json
import re
from collections import defaultdict
import gender_guesser.detector as gender
from difflib import SequenceMatcher

detector = gender.Detector(case_sensitive=False)


def detect_gender(name):
    person_gender = detector.get_gender(name)
    if person_gender in ['male', 'mostly_male']:
        return 'male'
    elif person_gender in ['female', 'mostly_female']:
        return 'female'
    else:
        return 'unknown'

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def is_valid_name(name):
    if len(name.strip().split()) >= 2:
        return True
    return False

def get_people_nom():
    with open('./resFiles/likely_nominees.json', 'r') as f:
        likely_nominees = json.load(f)

    with open('./resFiles/organized_awards.json', 'r') as f:
        organized_awards = json.load(f)

    with open('./resFiles/categorized_media.json', 'r') as f:
        categorized_media = json.load(f)

    with open('./resFiles/people.json', 'r') as f:
        people = json.load(f)

    valid_people = set(name.lower() for name in people.keys())

    likely_winners = set()
    winner_to_award = {}
    for award, info in organized_awards.items():
        winner = info.get('likely winner', '').lower()
        likely_winners.add(winner)
        winner_to_award[winner] = award

    award_phrases = {}
    award_winners = {}
    for award in organized_awards.keys():
        phrase = re.sub(r'best\s+', '', award, flags=re.IGNORECASE)
        phrase = phrase.lower()
        award_phrases[award] = phrase
        award_winners[award] = organized_awards[award]['likely winner'].lower()

    media_titles = {}
    for media_type, categories in categorized_media.items():
        for category, titles in categories.items():
            for title in titles:
                title_lower = title.lower()
                media_titles[title_lower] = {'media_type': media_type, 'category': category}

    award_nominees = defaultdict(set)  # Use set to avoid duplicates



    # process likely winners and their linked persons
    for winner_name, winner_data in likely_nominees.items():
        winner_name_lower = winner_name.lower()
        if winner_name_lower in likely_winners:
            award = winner_to_award.get(winner_name_lower)
            if award:
                linked_persons = winner_data.get('linked person', [])
                for linked_person in linked_persons:
                    linked_person_lower = linked_person.lower()
                    if linked_person_lower in likely_nominees:
                        if linked_person_lower not in valid_people:
                            continue
                        if not is_valid_name(linked_person):
                            continue
                        award_nominees[award].add(linked_person)
                award_nominees[award].add(winner_name)

    for nominee in likely_nominees.keys():
        nominee_lower = nominee.lower()
        if nominee_lower in likely_winners:
            continue
        if nominee_lower not in valid_people:
            continue
        if not is_valid_name(nominee):
            continue

        nominee_tweets = likely_nominees[nominee]['tweets']

        nominee_award_points = defaultdict(int)

        for tweet in nominee_tweets:
            tweet_lower = tweet.lower()

            best_matches = re.findall(r'best\s+([a-z\s\-]+)', tweet_lower)
            for match in best_matches:
                match = match.strip()
                for award, phrase in award_phrases.items():
                    sim_score = similarity(match, phrase)
                    if sim_score > 0.7:
                        nominee_award_points[award] += 10

            for award, winner in award_winners.items():
                if winner in tweet_lower and nominee_lower in tweet_lower:
                    nominee_award_points[award] += 12

            for title, info in media_titles.items():
                if title in tweet_lower:
                    gender_of_nominee = detect_gender(nominee.split()[0])
                    if gender_of_nominee == 'unknown':
                        continue
                    if info['media_type'] == 'TV':
                        if info['category'] == 'Drama':
                            if gender_of_nominee == 'male':
                                award = 'best actor in a television series - drama'
                            elif gender_of_nominee == 'female':
                                award = 'best actress in a television series - drama'
                            nominee_award_points[award] += 3
                        elif info['category'] == 'Comedy or Musical':
                            if gender_of_nominee == 'male':
                                award = 'best actor in a television series - comedy or musical'
                            elif gender_of_nominee == 'female':
                                award = 'best actress in a television series - comedy or musical'
                            nominee_award_points[award] += 3
                    elif info['media_type'] == 'Film':
                        if info['category'] == 'Drama':
                            if gender_of_nominee == 'male':
                                award = 'best actor in a motion picture - drama'
                            elif gender_of_nominee == 'female':
                                award = 'best actress in a motion picture - drama'
                            nominee_award_points[award] += 3
                        elif info['category'] == 'Comedy or Musical':
                            if gender_of_nominee == 'male':
                                award = 'best actor in a motion picture - comedy or musical'
                            elif gender_of_nominee == 'female':
                                award = 'best actress in a motion picture - comedy or musical'
                            nominee_award_points[award] += 3

        if nominee_award_points:
            max_points = max(nominee_award_points.values())
            if max_points >= 8:
                top_awards = [award for award, points in nominee_award_points.items() if points == max_points]
                for award in top_awards:
                    award_nominees[award].add(nominee)
                    linked_persons = likely_nominees[nominee].get('linked person', [])
                    for linked_person in linked_persons:
                        linked_person_lower = linked_person.lower()
                        if linked_person_lower in likely_nominees:
                            if linked_person_lower not in valid_people:
                                continue
                            if not is_valid_name(linked_person):
                                continue
                            award_nominees[award].add(linked_person)

    final_output = {}
    for award in organized_awards.keys():
        modified_award = award
        if re.search(r'\bbest\s+actor\b', award, re.IGNORECASE):
            modified_award = re.sub(r'\bbest\s+(actor\b)', r'best performance by an \1', award, flags=re.IGNORECASE)
        elif re.search(r'\bbest\s+actress\b', award, re.IGNORECASE):
            modified_award = re.sub(r'\bbest\s+(actress\b)', r'best performance by an \1', award, flags=re.IGNORECASE)
        nominees = list(award_nominees.get(award, []))
        likely_winner = organized_awards[award]['likely winner']
        if likely_winner not in nominees:
            nominees.append(likely_winner)
        final_output[modified_award] = nominees

    final_output['cecil b. demille award'] = []
    with open('./resFiles/people_nominees.json', 'w') as f:
        json.dump(final_output, f, indent=4)
    print("@@@@PEOPLE NOM DONE!!!")

if __name__ == "__main__":
    get_people_nom()
