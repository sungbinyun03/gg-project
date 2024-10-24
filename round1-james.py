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



with open('gg2013answers.json', 'r') as f:
    answers = json.load(f)


### Replace any portion of the word with the full nominee name 
### Replace words with hope or wish or think 

## Pre-processing the data-set 
with open('firstpass.json', 'r') as f:
    raw_tweet_data = json.load(f)


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


# def create_nominee_regex(nominees_dict):
#     all_nominees = set()
#     for nominees in nominees_dict.values():
#         all_nominees.update(nominees)
    
#     # Sort nominees by length (longest first) to avoid partial matches
#     sorted_nominees = sorted(all_nominees, key=len, reverse=True)
    
#     # Escape special regex characters and create alternations
#     escaped_nominees = [re.escape(nominee) for nominee in sorted_nominees]
#     regex_pattern = '|'.join(escaped_nominees)
    
#     # Make it case insensitive and allow for partial word matches
#     return rf'\b(?:{regex_pattern})\b'

# Frames 
pos_keywords = ['win', 'won', 'winner', 'awarded', 'wins']
uncertin_keywords = ['hope', 'hoping', 'think', 'predict', 'prediction', 'maybe', 'could', 'should','dont', 'don''t']
pos_keyword_reex = r'\b(' + '|'.join(pos_keywords) + r')\b'
uncertain_keyword_reex = r'\b(' + '|'.join(uncertin_keywords) + r')\b'
# print(uncertain_keyword_reex)

# make nominee re keywords 
nominee_database  = {}
for category in answers['award_data'].keys(): 
        if answers['award_data'][category]['winner'] not in answers['award_data'][category]['nominees']:
            answers['award_data'][category]['nominees'].append(answers['award_data'][category]['winner'])
            # print(answers['award_data'][category]['nominees'])
            nominee_database[category] = answers['award_data'][category]['nominees']
        else:
            nominee_database[category] = answers['award_data'][category]['nominees']


nominee_lists= [nominee_list for nominee_list in nominee_database.values()]
nominee_seperated = [item for sublist in nominee_lists for item in sublist]
nominee_reex = r'\b(' + '|'.join(nominee_seperated) + r')\b'



def normalize_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()

def fufills_pattern(normal_tweet):
    weight = 0
    if re.findall(pos_keyword_reex, normal_tweet, re.IGNORECASE): 
        weight += 3 
    if re.findall(uncertain_keyword_reex, normal_tweet, re.IGNORECASE):
        weight -= 2.5
    return [normal_tweet, weight]


def nominee_matcher(filtered_tweets):
    counter_dict = {}
    count = 0
    weight = 0 
    for tweet in filtered_tweets:
        check = re.search(nominee_reex, tweet, re.IGNORECASE)
        if check:
            count +=1 
            # key is the award category
            # value is the list of nomineees 
            for k, v in nominee_database.items():
                if check.group() in v:
                    value = check.group() 
                    counter_dict[value] = [k, count]

    return(counter_dict)
   
    
# First need to find the name of the actor / title 
# Now, need to search for the number of occurences for this name in the filtered_tweet database 
# Store it in some new datatype 
# Once we have a list with the count, need to matchup the role of that indivudal with 

    
tweet_list = []

def export_to_csv(nominee_counts):
    # Create a list to store rows
    rows = []
    
    # Collect the rows from nominee_counts
    for name, award_info in nominee_counts.items():
        rows.append([award_info[0], name, award_info[1]])

    # Create a DataFrame from the list
    df = pd.DataFrame(rows, columns=["Award", "Nominee", "Mentions"])
    
    # Export the DataFrame to a CSV file
    df.to_csv('nominee_mentions1.csv', index=False)

    return df  # Return the DataFrame for further processing

def main(): 
    for tweet in processed_tweets:
        # print(tweet)
        normal_tweet = normalize_text(tweet)
        tweet_list.append(fufills_pattern(normal_tweet))
    filtered_tweets = [tweet[0] for tweet in tweet_list if tweet[1] > 2]
    mentions_unsorted = nominee_matcher(filtered_tweets)
    df = export_to_csv(mentions_unsorted)
    df_sorted = df.sort_values(by=["Award", "Mentions"], ascending=[True, False])
    df_sorted.to_csv('sorted_nominee_mentions.csv', index=False)
    print(df_sorted)



main()





# Look at indivudal tweet 
# if it matches one of the nominee regex 
# then create/add it to the dictionary with a count + 1 
# The key should be the actor / movie 









