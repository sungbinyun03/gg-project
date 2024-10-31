#!/opt/anaconda3/envs/gg337/bin/python
import spacy 
import pandas as pd
import re 
from ftfy import fix_text 
from unidecode import unidecode 
import nltk 
from inflection import humanize, underscore
import json 
import csv 
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

with open('gg2013answers.json', 'r') as f:
    answers = json.load(f)

## Pre-processing the data-set 
with open('gg2013.json', 'r') as f:
    raw_tweet_data = json.load(f)


spacy_model = spacy.load("en_core_web_trf")



nominee_list = [
    "Kathryn Bigelow", "Ang Lee", "Steven Spielberg", "Quentin Tarantino", 
    "Zooey Deschanel", "Tina Fey", "Julia Louis-Dreyfus", "Amy Poehler", 
    "Hayden Panettiere", "Archie Panjabi", "Sarah Paulson", "Sofia Vergara", 
    "Alan Arkin", "Leonardo DiCaprio", "Philip Seymour Hoffman", "Tommy Lee Jones", 
    "Emily Blunt", "Judi Dench", "Maggie Smith", "Meryl Streep", 
    "Ben Affleck", "Benedict Cumberbatch", "Woody Harrelson", "Toby Jones", 
    "Clive Owen", "Nicole Kidman", "Jessica Lange", "Sienna Miller", 
    "Sigourney Weaver", "Jack Black", "Bradley Cooper", "Ewan McGregor",
    "Bill Murray", "Marion Cotillard", "Sally Field", "Helen Mirren", 
    "Naomi Watts", "Rachel Weisz", "Connie Britton", "Glenn Close", 
    "Michelle Dockery", "Julianna Margulies", "Richard Gere", "John Hawkes", 
    "Joaquin Phoenix", "Denzel Washington", "Steve Buscemi", "Bryan Cranston", 
    "Jeff Daniels", "Jon Hamm", "Alec Baldwin", "Louis C.K.", 
    "Matt LeBlanc", "Jim Parsons", "Max Greenfield", "Danny Huston", 
    "Mandy Patinkin", "Eric Stonestreet", "Amy Adams", "Sally Field", 
    "Helen Hunt", "Nicole Kidman"
]

processed_tweets = []
for tweet in raw_tweet_data:
    if isinstance(tweet, dict) and 'text' in tweet:
        tweet_text = tweet['text']
    elif isinstance(tweet, str):
        tweet_text = tweet
    else:
        continue  # Skip if the tweet is neither a dict with 'text' nor a string

    # Apply text processing
    cleaned_tweet = fix_text(tweet_text)
    cleaned_tweet = unidecode(cleaned_tweet)
    cleaned_tweet = " ".join(cleaned_tweet.split())
    processed_tweets.append(cleaned_tweet)

# Frames 
pos_keywords = ['drunk']
drunk_keyword_reex = r'\b(' + '|'.join(pos_keywords) + r'k*)\b' # will get drunk an drunkkkkkk 
# uncertain_keyword_reex = r'\b(' + '|'.join(uncertin_keywords) + r')\b'
# negative_keyword_reex = r'\b(' + '|'.join(negative_keywords) + r')\b'
# print(uncertain_keyword_reex)

def normalize_text(text):
    return re.sub(r'[^a-zA-Z0-9\s-]', '', text).lower()

nominee_seperated = [nominee for nominee in nominee_list]
nominee_reex = r'\b(' + '|'.join(nominee_seperated) + r')\b'



def drunk_matcher():
    drunk_list = []
    for tweet in processed_tweets:
        match = re.findall(drunk_keyword_reex, tweet, re.IGNORECASE)
        if match:
            loaded_tweet = spacy_model(tweet)
            for token in loaded_tweet:
                part_of_speech = token.pos_
                if part_of_speech == "PROPN":
                    drunk_list.append(tweet)
    return drunk_list


def drunk_finder(drunks):
    drunk_dict = {}
    for tweet in drunks:
        check = re.search(nominee_reex, tweet, re.IGNORECASE)
        if check: 
            value = check.group().lower()
            if value not in drunk_dict.keys():
                drunk_dict[value] = [tweet]
            else:
                drunk_dict[value].append(tweet)
    return drunk_dict

def export_to_csv(drunk_nominee):
    # Create a list to store rows
    rows = []
    # Collect the rows from nominee_counts
    print(drunk_nominee)
    for nominee in drunk_nominee:
        rows.append([nominee, len(drunk_nominee[nominee])])

    # Create a DataFrame from the list
    df = pd.DataFrame(rows, columns=["Nominee", "Drunk Count"])
    
    # Export the DataFrame to a CSV file
    # df.to_csv('Drunk.csv', index=False)

    return df  # Return the DataFrame for further processing

def main():
    drunk_tweets = drunk_matcher()
    nominee_dictionary = drunk_finder(drunk_tweets)
    df = export_to_csv(nominee_dictionary)
    df_sorted = df.sort_values(by='Drunk Count', ascending=(False))
    df_sorted.to_csv('drunk.csv', index=False)
    most_drunk_idx = df['Drunk Count'].idxmax()
    

main()
