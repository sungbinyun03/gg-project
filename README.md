### Golden Globes 2013 Winners, Award Categories, Nominees, and our added touch...Most Drunk
#### Natural Language Processsing Fall 2024 
**Group 6** - Sungbin Yun and James Carlin

### To run
python install -r requirements.txt

The entire processing flow was integrated into the main function of gg_api.

The results are also saved as json files in the folder resFiles

### About the Project 
This project involves analyzing tweets about the Golden Globe Awards to automatically extract and structure information about the ceremony. The core challenge is building a robust information extraction system that can understand and categorize unstructured social media text.

#### Techniques Used
**1. Entity recognition** 
- Use SpaCy for named entity recognition
- Identify people, works (movies/shows), organizations
- Build custom entity recognition for award names

**2. Syntactic Parsing**
- Use dependency parsing to understand sentence structure
- Identify relationships between entities
- Extract subject-verb-object patterns

**3. Text Similarity**
- Applied RapidFuzz library to gauge semantic similarity of tweets 

**3. Regular Expressions**
- Employed the re library to identifiy word and phrase similaries, and build pattern matchers. 

**4. Type Checking and Entity Checking**
- Utilized the IMDB API in conjunction with fuzz to categorize various structures of Actor/Actress/Media names into their official spelling.
  
### Preprocessing Phase (runtime ~ 8 minutes)

Tweet preparation and entity extraction to streamline award identification.

#### **1. firstpass.py: Initial Tweet Filtering**

- **Purpose**: Preprocesses raw tweets by removing extraneous elements and isolating award-related tweets.
- **Steps**:
  - **Text Cleaning**: Removes URLs, mentions (keeping usernames), and non-alphanumeric characters. Adds ")" after usernames following "RT".
  - **Filtering**: Only keeps tweets containing specific winning phrases from `WINNING_PHRASES`.
  - **Output**: Creates a list of unique preprocessed tweets and saves them to `firstpass.json` for use.

#### **2. entities.py: Entity Extraction with SpaCy**

- **Purpose**: Extracts named entities, particularly people, from the preprocessed tweets.
- **Steps**:
  - **Entity Identification**: Uses SpaCy’s `en_core_web_trf` model to identify "PERSON" entities in tweets.
  - **Categorization**: Organizes tweets into `people_tweets` for individuals and `other_entities_tweets` for non-person entities.
  - **Output**: Stores sorted people entities by tweet frequency in `people.json`, focusing on potential award nominees.

#### **3. media_classify.py: Media Mention Classification**

- **Purpose**: Identifies media entities (like movies and shows) and matches them to IMDb entries.
- **Steps**:
  - **Keyword Filtering**: Filters tweets mentioning awards with phrases like "should have won" or "was nominated".
  - **IMDb Matching**: Uses IMDb’s API to match entity names to IMDb entries, ensuring high similarity scores (≥90) using `fuzz.ratio`.
  - **Output**: Saves matched media entities in `mediaShouldHave.json` and caches IMDb results in `imdb_cache.json`.

#### **4. mediaMatcher.py: Media Categorization Using Wikipedia**

- **Purpose**: Further categorizes media entities into subcategories by fetching summaries from Wikipedia.
- **Steps**:
  - **Wikipedia Summarization**: Queries Wikipedia for a brief summary of each media title.
  - **Categorization**: Uses predefined keywords in `CATEGORIES` to classify each media entry into specific award categories.
  - **Output**: Outputs categorized media in `categorized_media.json` for use in award matching.
### Retreiving Award Data (runtime ~2 min)
**Description:** This was one of the more challenging undertakings of the project. At first, we emplyoed basic script theory to isolate somewhat relevant tweets. This invovled using Spacy to determine the root of a sentence—eliminating cases of first person POV or misleading phrases which include personal pronouns like -I-. From here, we isolated the RHS of the tweet which contains information about the award. So in the best case we could have a protoypical phrase (...best Performance by an Actor/Actress in a Television Series - Comedy or Musical) or a highly miselading and informal tweet (....best wahoo award for sexiest actor). 

Upon parsing through the firstpass_json file (our pre-processed version of gg2013) we realized entity identification would involve more than identifying the root. This led us to experiment with the find_award_boundry function. FABF helped us see through two main aims. First it allowed us to remove any content that was unrelated to the grammatical structure of a tweet. Upon running the correct award names through the spacy trf model, we found some key patterns. Namely, the parts of speech did not contain ["PROPN", "VERB", "PRON"]. This proved to be an easily filtration method for the first iteration of the tweets. This substantially reduced our new list of tweets size, but there remained too many incongruent phrases to identify any meaninful patterns. Consequently, we incorperated a hard-coded list of red-flag words (also, then, which ) that would remove converational tone fron the rhs. Next we applied a syntacic dependence label ['compound', 'amod', 'pobj', 'prep'] which we also derived from tests on the gganswers file.

Upon a few more minor tweak (e.x. any instance of the word made must be followed by for otherwise the ADP for) we had a library of high quality phrases covering the gamut of possible award names. 

The trickiest part of the Award function came down to figuring out the lingusitc similarity between awards. First however, we needed to cut down our ~800 item list down by grouping identical tweets and then ranking them using pandas dataframes (both for computational efficency and built-in methods). This gave us a condensed list which we subdivided into three distinct groups: actors, tv, and everything else (which ended up being films). 
)
We then used the rapidfuzz fuzz ratio with a threshold set at 67%—which we arrived at through trial and error. 

**Functions** 

**find_award_boundry(tweet):**
This function uses SpaCy to analyze the grammatical structure of a tweet and extracts just the award name portion by filtering out irrelevant words and stopping at certain boundary conditions.

**extract_awards():**
This function implements a three-phase filtering system to extract award names from tweets. First it finds tweets containing win-related verbs, then filters for those starting with "best", and finally applies the boundary detection to clean up the award names. 

**get_final_awards(tweets):**
This is the main function (in a seperate file) that processes the raw award names into standardized categories.

**actor(tweets):**
It uses fuzzy string matching to group similar actor awards, then creates standardized versions by adding "best performance by an" prefix. 

**movie(tweets): & tv(tweets):**
same approach here as above 

**main():**
This function serves as the entry point and orchestrator, calling extract_awards() to get the initial list of awards and then passing them to get_final_awards() (imported from phraseMatcher) for final processing. 

### Extracting Nominees (runtime ~5 minutes)

#### **winProb.py: Nominee Probability Scoring**

- **Purpose**: Scores potential nominees based on tweet sentiment and context.
- **Steps**:
  - **Award Categorization**: Uses `OFFICIAL_AWARDS` and `AWARD_SYNONYMS` to categorize nominees by award type.
  - **Sentiment Scoring**: Assigns scores to tweets based on `POSITIVE_PHRASES` and `NEGATIVE_PHRASES`.
  - **Gender Correction**: Adjusts award categories based on gender (e.g., actor/actress).
  - **Output**: Organizes scores in `likely_nominees.json` and stores IMDb-verified actors.

#### **nominee.py: Nominee Identification**

- **Purpose**: Consolidates nominees for each award by verifying against known people and media.
- **Steps**:
  - **Linked Nominee Identification**: Associates linked persons with nominees based on tweet context and mentions.
  - **Category Assignment**: Maps nominees to the correct awards using similarity matching.
  - **Output**: Saves finalized nominees and winners for each award in `people_nominees.json`.

#### **mediaNom.py: Top Media Nominees Identification**

- **Purpose**: Extracts top media mentions for each award category.
- **Steps**:
  - **Top Mentions Identification**: Counts mentions of each media title in tweets and selects the top candidates.
  - **Output**: Saves media nominees in `media_nominees.json` for final award processing.


The highlight was that the winners were successfully extracted for all people awards, without any prior data 

Accuracy (Precision): ≈0.3214
Total True Positives (TP): 18
Total False Positives (FP): 38


Although low, we want to highlight the successful cases in which we extracted the majority of nominees, such as:

"best performance by an actress in a television series - comedy or musical": [
        "Lena Dunham",
        "Tommy Lee Jones",
        "Amy Poehler",
        "Zooey Deschanel",
        "Tina Fey"
    ],


### get_winners (runtime ~1 min)

This script processes tweets to identify likely award winners based on nominee mentions and predefined winner patterns.

#### 1. count_nominee_mentions 

- **Purpose**: Counts mentions of each nominee for a given award based on tweets containing "winner" patterns.
- **Steps**:
  - **Winner Pattern Matching**: Uses `WINNER_PATTERNS` to identify tweets that imply an award win.
  - **Fuzzy Matching**: Compares each nominee's name to the tweet text using `fuzz.partial_ratio` with an 80% threshold to accommodate minor textual variations.
  - **Mention Counting**: Increments the count for nominees matched in tweets for each award.
  - **Output**: Prints nominee mention counts for each award.

- **Winner Selection**: For each award, selects the nominee with the highest mention count (if any), adding them to the `winners` dictionary.
- **Export**: Calls `export_to_csv` to save the mention counts.


#### 2. get_winners Function

- **Steps**:
  - **Winner Determination**: Calls `count_nominee_mentions` to generate mention counts and determine winners for each award.
  - **Output**: Returns and prints the final dictionary of award winners based on mention counts.

Great Accuracy here!
### Most drunk category (runtime ~30 seconds) 

**Description:** This was our bonus section of the assignment, and we used it to find the nominees that were argued by the twitter fans to be the most drunk. This script implement regular expressions and spacy to find the unsober nominee. First, we used regualr expression matching to identify any tweet with the word drunk, and then filtered down those tweets to one's with PROPN—with the help of spacy. Next, we take the list of PROPN/drunk occurences and use re.search to between the regular expression nominee list and an invidual tweet. IF ther eis a match, that tweet is added to a the nominees name in a dictionary. Last, we converted the dictionary to the a DF and sorted values by "Drunk Count" or the len of the items fora single key. 

With more time in the future, we would like to make this version more advanced by plotting the frequency of twitter observers drunk tweet mentions using a line graph or identfying the number of tweets about drunkness corresponding to the phase of the award ceremony.

**Functions** 
drunk_matcher():
This function scans through processed tweets looking for the word "drunk" (including variations like "drunkkkk"). It only keeps tweets that contain both the drunk keyword and a proper noun (PROPN), using SpaCy for part-of-speech tagging.

drunk_finder(drunks):
Takes tweets containing "drunk" and matches them against a predefined list of nominees using regex. Creates a dictionary where each nominee is a key and their associated "drunk" tweets are the values.




