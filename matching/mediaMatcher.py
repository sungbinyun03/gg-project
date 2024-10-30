import wikipedia
import json

# Define categories and keywords for sub-classification
CATEGORIES = {
    "TV": {
        "Drama": ["drama", "crime", "thriller", "mystery"],
        "Comedy or Musical": ["comedy", "sitcom", "musical", "parody", "romantic comedy"]
    },
    "Film": {
        "Foreign Film": ["danish", "french"],
        "Animated Film": ["animated", "animation", "cartoon"],
        "Comedy or Musical": ["comedy", "comedy-drama", "romantic" , "musical", "parody", "romantic comedy"],
        "Drama": ["drama", "biography", "historical", "thriller", "revisionist"],
        
    }
}

def load_json(file_path):
    """Load JSON data from the file."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_wikipedia_summary(title, media_type, year):
    """Fetch Wikipedia summary with year and media type context."""
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
    """Classify subcategories based on keywords found in the summary."""
    if media_type in CATEGORIES:
        for subcategory, keywords in CATEGORIES[media_type].items():
            if any(keyword.lower() in summary_text.lower() for keyword in keywords):
                return subcategory
    return None

def classify_media_titles(media_entries):
    """Classify each title as TV or Movie, then further categorize using Wikipedia."""
    categorized_media = {
        "TV": {"Drama": [], "Comedy or Musical": []},
        "Film": {"Foreign Film": [], "Animated Film": [], "Comedy or Musical": [], "Drama": [], }
    }
    
    for media in media_entries:
        try:
            title, kind, year = media  # Unpack the media list
            media_type = "TV" if "tv" in kind else "Film"
            
            # Fetch Wikipedia summary for further classification
            summary = get_wikipedia_summary(title, media_type, year)
            
            # Determine subcategory based on summary keywords
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

def main():
    # Load the media titles from shouldHaves.json
    data = load_json('../resFiles/shouldHaves_media_only.json')
    media_entries = data.get("Media", [])
    
    # Classify each title
    categorized_media = classify_media_titles(media_entries)
    
    # Output results
    print("\nCategorized Media:")
    for main_category, subcategories in categorized_media.items():
        for subcategory, items in subcategories.items():
            print(f"{main_category} - {subcategory}: {items}")

    # Optionally, save results to a JSON file
    with open('../resFiles/categorized_media.json', 'w') as outfile:
        json.dump(categorized_media, outfile, indent=4)

# Execute the main function
if __name__ == "__main__":
    main()
