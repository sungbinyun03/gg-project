import spacy 
import pandas as pd
import re 
from ftfy import fix_text 
from unidecode import unidecode 
import json 
import warnings
from .constants import NOMINEE_LIST
warnings.filterwarnings("ignore", category=FutureWarning)

spacy_model = spacy.load("en_core_web_trf")
nominee_seperated = [nominee for nominee in NOMINEE_LIST]
nominee_reex = r'\b(' + '|'.join(nominee_seperated) + r')\b'


def drunk_matcher(processed_tweets):
    drunk_list = []
    drunk_keyword_reex = r'\b(drunkk*)\b'  # modified regex for 'drunk' with multiple k's
    for tweet in processed_tweets:
        match = re.findall(drunk_keyword_reex, tweet, re.IGNORECASE)
        if match:
            loaded_tweet = spacy_model(tweet)
            for token in loaded_tweet:
                if token.pos_ == "PROPN":
                    drunk_list.append(tweet)
                    break
    return drunk_list


def drunk_finder(drunks):
    drunk_dict = {}
    for tweet in drunks:
        check = re.search(nominee_reex, tweet, re.IGNORECASE)
        if check: 
            value = check.group().lower()
            drunk_dict.setdefault(value, []).append(tweet)
    return drunk_dict


def get_most_drunk():
        
    with open("./resFiles/firstPass.json", 'r') as f:
        processed_tweets = json.load(f)

    drunk_tweets = drunk_matcher(processed_tweets)
    nominee_dictionary = drunk_finder(drunk_tweets)

    drunk_counts = {nominee: len(tweets) for nominee, tweets in nominee_dictionary.items()}
    top_3_drunk_nominees = sorted(drunk_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_3_drunk_list = [nominee for nominee, count in top_3_drunk_nominees]
    print("@@@@ HERE: ", top_3_drunk_list)
    return top_3_drunk_list  
