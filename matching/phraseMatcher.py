import pandas as pd 
import re 
import spacy
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from collections import defaultdict, Counter
from collections import defaultdict, Counter
from nltk import ngrams
from rapidfuzz import fuzz


def get_final_awards(tweets):
    tweet_dataframe = pd.DataFrame(tweets, columns=['strings'])
    tweet_dataframe['strings'] = tweet_dataframe['strings'].str.strip()


    def replace(x):
        x = " ".join(x.split())
        if 'actress' in x:
            x = x.replace('actress', 'actor')
        return x 

    tweet_dataframe['strings'] = tweet_dataframe['strings'].apply(replace)


    phrase_counts = tweet_dataframe['strings'].value_counts()
    df_unique_sorted = phrase_counts.reset_index()
    df_unique_sorted.columns = ['phrase', 'count']
    df_unique_sorted = df_unique_sorted[df_unique_sorted['count'] > 2]
    condensed_list_of_awards = df_unique_sorted['phrase'].to_list() 


    def actor(tweets):
        result = []
        for phrase in tweets:
            threshold = 67
            if all(fuzz.ratio(phrase, existing) < threshold for existing in result):
                    result.append(phrase)
        results2 = []
        for award in result:
            if "performance" not in award:
                award1 = ("best performance by an " + award)
                duplicated_award = ("best performance by an " + award.replace('actor', 'actress'))
                results2.append(duplicated_award)
                results2.append(award1)
            else:
                award1 = ("best by an " + award)
                duplicated_award = ("best " + award.replace('actor', 'actress'))
                results2.append(duplicated_award)
                results2.append(award1)
        return results2

    def movie(tweets):
        result = []
        for phrase in tweets:
            threshold = 67
            if all(fuzz.ratio(phrase, existing) < threshold for existing in result):
                    result.append(phrase)

        filtered_phrases = [phrase for phrase in result if "picture" not in phrase or re.search(r'\bmotion picture\b', phrase)]
        result_2 = []
        for award in filtered_phrases:
            award = ("best " + award)
            result_2.append(award)
        return result_2



    def tv(tweets):
        result = []
        for phrase in tweets:
            threshold = 50
            if all(fuzz.ratio(phrase, existing) < threshold for existing in result):
                result.append(phrase)
        result_2 = []
        for award in result:
            award = ("best " + award)
            result_2.append(award)

        return result_2

        finallly = [("best " + award) for award in result]


    actor_list = []
    tv_show_list = []
    movie_list = [] 
    for tweet in condensed_list_of_awards:
        if "actor" in tweet or "supporting" in tweet:
            actor_list.append(tweet)
        elif 'tv' in tweet or 'television' in tweet:
            tv_show_list.append(tweet)
        else:
            movie_list.append(tweet)
    awards_list = []
    for award in actor_list:
        awards_list.append(award)
    for award in movie_list:
        awards_list.append(award)
    for award in tv_show_list:
        awards_list.append(award)


    return awards_list 


    call_actors = actor(actor_list)
    call_movies = movie(movie_list)
    call_tweets = tv(tv_show_list)