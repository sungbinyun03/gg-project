import json
from imdb import IMDb
from rapidfuzz import fuzz
import gender_guesser.detector as gender

# Initialize IMDb and gender detector
ia = IMDb()
detector = gender.Detector()

def clean_nominee_list(nominees, likely_winner=None):
    """Remove duplicates and likely winner from the nominee list."""
    # First convert to set to remove duplicates
    unique_nominees = set(nominees)
    
    # Remove likely winner from nominees if present
    if likely_winner:
        unique_nominees.discard(likely_winner)  # Using discard instead of remove to avoid KeyError
        
    return list(unique_nominees)

def gender_matches_award(award, person_name):
    """Check if the gender of the award matches the person's gender."""
    gender_term = "actor" if "actor" in award.lower() else "actress"
    person_gender = detector.get_gender(person_name.split()[0])

    if gender_term == "actor" and person_gender in ['male', 'mostly_male']:
        return True
    if gender_term == "actress" and person_gender in ['female', 'mostly_female']:
        return True
    return False

def promote_nominee_to_winner(valid_nominees, award):
    """Promote a valid nominee to winner if they match the award criteria."""
    if not valid_nominees:
        return None, []
    
    # Sort nominees to ensure consistent selection
    sorted_nominees = sorted(valid_nominees)
    promoted_winner = sorted_nominees[0]
    remaining_nominees = sorted_nominees[1:]
    
    return promoted_winner, remaining_nominees

def filter_nominees_by_imdb(award, likely_winner, others):
    valid_nominees = []

    # Process likely winner if valid
    if likely_winner:
        winner_search = ia.search_person(likely_winner)
        if winner_search:
            top_result = winner_search[0]['name']
            similarity_score = fuzz.ratio(likely_winner.lower(), top_result.lower())
            if similarity_score >= 90 and gender_matches_award(award, top_result):
                likely_winner = top_result
            else:
                likely_winner = None

    # Process other nominees
    for nominee in others:
        if nominee and nominee != likely_winner:  # Exclude likely winner
            nominee_search = ia.search_person(nominee)
            if nominee_search:
                top_result = nominee_search[0]['name']
                similarity_score = fuzz.ratio(nominee.lower(), top_result.lower())
                if similarity_score >= 90 and gender_matches_award(award, top_result):
                    valid_nominees.append(top_result)

    # If no likely winner but we have valid nominees, promote one
    if not likely_winner and valid_nominees:
        likely_winner, valid_nominees = promote_nominee_to_winner(valid_nominees, award)

    # Clean the nominee list to remove duplicates and likely winner
    valid_nominees = clean_nominee_list(valid_nominees, likely_winner)
    
    return award, likely_winner, valid_nominees

def associate_nominees_with_awards():
    # Load organized awards data
    with open('../resFiles/organized_awards_noMatching.json', 'r') as f:
        awards_data = json.load(f)

    awards_with_nominees = {}
    for award, data in awards_data.items():
        likely_winner = data.get("likely winner")
        others = data.get("others", [])
        
        # Filter nominees by IMDb and clean the lists
        award, likely_winner, valid_nominees = filter_nominees_by_imdb(award, likely_winner, others)
        
        # Additional cleanup: ensure likely winner is not in nominees list
        if likely_winner in valid_nominees:
            valid_nominees.remove(likely_winner)
            
        awards_with_nominees[award] = {
            "likely winner": likely_winner,
            "nominees": valid_nominees
        }
    
    return awards_with_nominees

def main():
    # Associate nominees with awards and filter based on IMDb and gender
    awards_with_nominees = associate_nominees_with_awards()
    
    # Save the cleaned awards data to JSON
    with open('../resFiles/organized_award_nominees_cleaned.json', 'w') as f:
        json.dump(awards_with_nominees, f, indent=4)
    
    print("Cleaned awards and nominees saved to organized_award_nominees_cleaned.json")

if __name__ == "__main__":
    main()