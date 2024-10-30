#!/opt/anaconda3/envs/gg337/bin/python
import pandas as pd 
import json 
import re 
import spacy
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from collections import defaultdict, Counter

spacy_model = spacy.load("en_core_web_trf")

with open('matched_people.json', 'r') as f:
    entities = json.load(f)

with open('gg2013answers.json', 'r') as f:
    winner_data = json.load(f)

def get_proper_award_name(tweets): 
    df = pd.DataFrame(tweets, columns=['strings'])
    df['strings'] = df['strings'].str.strip()
    value_counts = df['strings'].value_counts()
    df = df.sort_values(by='strings', key=lambda x: x.map(value_counts), ascending=False)

    duplicates_removed = df['strings'].drop_duplicates().reset_index(drop=True)
    print("After dropping duplicates:\n", duplicates_removed)
    def hard_code(x):
        if 'actor' in x or 'actress' in x:
            x = "best performance by an " + x
            return x
        else:
            x = "best " + x
            return x

    polished = duplicates_removed.apply(hard_code)
    # pd.set_option('display.max_rows', None)
    polished.to_csv("polished_award_names.csv", index=False, header=["polished_award_name"])



def find_award_boundry(tweet):

    spacy_output = spacy_model(tweet.lower()) 
    spacy_output = spacy_output[1:] # removes best 
    index = 0 
    word_tracker = []

    skip_words = {
        'now', 'where', 'aka', 'the', 'who', 'did', 'not', 'then', 'also', 'just', 'with', 'amp', 'via'
        'that', 'this', 'these', 'those', 'what', 'when', 'at', 'why', 'how', 'and', 'but', 'yet', 'so', 'because', 'best'
    }

    while index < len(spacy_output):
        token = spacy_output[index]
        if token.text == 'performance':
            print(True)


        if token.text == "made" and index + 1 < len(spacy_output) and spacy_output[index + 1].text == "for":
            word_tracker.extend(["made", "for"])
            index += 2
            continue

        if (token.text == "for" or token.text in skip_words or                   # Explicit check for "for"
            (token.pos_ in ["PROPN", "VERB", "CCONJ", "PRON"] and 
             token.text not in ["or", "made"])):      # Except special cases
            # print(token.text)
            break

        if token.dep_ in ['compound', 'amod', 'pobj', 'prep']:
            word_tracker.append(token.text)
            index += 1
            continue


        if token.text == "or" and token.pos_ == "CCONJ":
            word_tracker.append(token.text)
            index += 1
            continue

        word_tracker.append(token.text)
        index +=1 

    return word_tracker



def extract_awards(dict):
    # Ideal format -> prior tweet Daniel DayLewis wins best actor in a motion picture drama for Lincoln 

    # phase 1: Finding tweets with a reliable head and root_verb 
   

    tweets = [tweet for actor in entities for tweet in entities[actor]]
    spacy_outputs = list(spacy_model.pipe(tweets))

    phase_one_filter = []

    for spacy_output, tweet in zip(spacy_outputs, tweets):
        for chunk in spacy_output.noun_chunks:
            root_head = chunk.root.head.text
            root = chunk.text
            if root.lower() != "i" and re.search(r"\b(win|wins|won)\b", root_head.lower()):
                phase_one_filter.append(tweet)
    
    # check if first word after wins is "best "
    phase_2_filter = []
    for tweet in phase_one_filter:
        rhs = ''
    # Use non-greedy match to catch up to first occurence prior to wins 
        match = re.search(r"(.+?)\s+wins\s+(.+)", tweet.lower())
        if match:
            rhs = match.group(2).strip()
            if re.match(r"^\s*best\b", rhs, re.IGNORECASE): ### may want to revisit thsi to pair with first occurence of best rather than word after wins 
                phase_2_filter.append(rhs)

    # working backwards on the rhs to remove any words not associated with the movie title 
    phase_3_filter = []
    
    for tweet in phase_2_filter:
        returned = find_award_boundry(tweet)
        if len(returned) >3:
            phase_3_filter.append(" ".join(returned))

    get_proper_award_name(phase_3_filter)


def main():

    extract_awards(entities)
    


main()








# #!/opt/anaconda3/envs/gg337/bin/python
# import pandas as pd 
# import json 
# import re 
# import spacy
# import warnings
# warnings.filterwarnings("ignore", category=FutureWarning)



# spacy_model = spacy.load("en_core_web_trf")


# with open('matched_people truncated.json', 'r') as f:
#     entities = json.load(f)


# def get_proper_award_name(tweet):
#     most_frequenct = []
#     front_sliced = tweet[0:3]




# def find_award_boundry(tweet):

#     spacy_output = spacy_model(tweet.lower()) 
#     spacy_output = spacy_output[1:] # removes best 
#     index = 0 
#     word_tracker = []

#     while index < len(spacy_output):
#         token = spacy_output[index]

#         if token.text == "made" and index + 1 < len(spacy_output) and spacy_output[index + 1].text == "for":
#             word_tracker.extend(["made", "for"])
#             index += 2
#             continue

#         if (token.text == "for" or                    # Explicit check for "for"
#             (token.pos_ in ["PROPN", "VERB", "CCONJ", "ADP"] and 
#              token.text not in ["or", "made"])):      # Except special cases
#             # print(token.text)
#             break

    
#         if token.dep_ in ['compound', 'amod', 'pobj', 'prep']:
#             word_tracker.append(token.text)
#             index += 1
#             continue



#         if token.text == "or" and token.pos_ == "CCONJ":
#             word_tracker.append(token.text)
#             index += 1
#             continue


#         word_tracker.append(token.text)
#         index +=1 

#     return word_tracker



# def extract_awards(dict):
#     # Ideal format -> prior tweet Daniel DayLewis wins best actor in a motion picture drama for Lincoln 

#     # phase 1: Finding tweets with a reliable head and root_verb 
#     tweets = [tweet for actor in entities for tweet in entities[actor]]
#     phase_2_filter = []
#     for tweet in tweets:
#         match = re.search(r"\b(win|wins|won)\b\s+best\b\s+(.*)", tweet.lower())
#         if match:
#             rhs = match.group(2).strip()
#             phase_2_filter.append(rhs)
#     print(phase_2_filter)

#     # working backwards on the rhs to remove any words not associated with the movie title 
#     phase_3_filter = []
    
#     for tweet in phase_2_filter:
#         returned = find_award_boundry(tweet)
#         if len(returned) >=3:
#             phase_3_filter.append(returned)
#     print(phase_3_filter)


# def main():

#     extract_awards(entities)
    


# main()

# ### add in adjectives 
# ### add in verbs 






