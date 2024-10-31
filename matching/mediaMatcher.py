import wikipedia
import json
from .constants import CATEGORIES

def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_wikipedia_summary(title, media_type, year):
    try:
        query = f"{media_type} {title} {year}"
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Disambiguation error for '{title}': {e.options}")
    except wikipedia.exceptions.PageError:
        print(f"Page error: '{title}' not found.")
    except Exception as e:
        print(f"Error fetching Wikipedia data for '{title}': {e}")
    return ""

def categorize_media(summary_text, media_type):
    if media_type in CATEGORIES:
        for subcategory, keywords in CATEGORIES[media_type].items():
            if any(keyword.lower() in summary_text.lower() for keyword in keywords):
                return subcategory
    return None

def classify_media_titles(media_entries):
    categorized_media = {
        "TV": {"Drama": [], "Comedy or Musical": []},
        "Film": {"Foreign Film": [], "Animated Film": [], "Comedy or Musical": [], "Drama": [], }
    }
    
    for media in media_entries:
        try:
            title, kind, year = media  # Unpack the media list
            media_type = "TV" if "tv" in kind else "Film"
            
            summary = get_wikipedia_summary(title, media_type, year)
            
            subcategory = categorize_media(summary, media_type)
            
            if subcategory:
                categorized_media[media_type][subcategory].append(title)
            else:
                print(f"Could not categorize '{title}' into a subcategory.")
                print("@@@@ SUMMARY: ", summary)
                print("@@@@ MEDIA TYPE: ", media_type)
                
        except Exception as e:
            print(f"An error occurred with '{media}': {e}")
    
    return categorized_media

def match_media():
    data = load_json('./resFiles/mediaShouldHave.json')
    media_entries = data.get("Media", [])
    
    categorized_media = classify_media_titles(media_entries)
    
    with open('./resFiles/categorized_media.json', 'w') as outfile:
        json.dump(categorized_media, outfile, indent=4)

# Execute the main function
if __name__ == "__main__":
    match_media()
