#!/opt/anaconda3/envs/gg337/bin/python
import spacy 
import warnings
import json
warnings.filterwarnings("ignore", category=FutureWarning)

spacy_model = spacy.load("en_core_web_trf")


# with open( "gg2013answers.json", 'r') as f:
#     data = json.load(f)

# awards = list(data['award_data'].keys())
# print(awards)

# for award in awards:
#     doc = nlp(award.lower())
#     for token in doc:
#         print(token.text, token.pos_)




# import pandas as pd

# # Sample data as a dictionary
# data = {
#     "strings": [
#         "supporting actress in a motion picture",
#         "director motion picture",
#         "actress in a supporting role in a motion picture",
#         "recovery from a",
#         "director at hey academy"
#     ],
#     "counts": [20, 14, 12, 4, 4]
# }

# # Create the DataFrame
# df = pd.DataFrame(data)

# # Display the DataFrame
# print(df[df['counts'] > 10])
      




text  = ['actress', 'motion', 'picture', 'comedy', 'or', 'musical', 'for', 'silver', 'linings']
text = ['actress', 'motion', 'picture', 'comedy', 'or', 'musical', 'for', 'silver', 'linings']
joined_text = " ".join(text)
doc = spacy_model("performance by an actor in a television series - drama")
for token in doc:
    print(token.text, token.pos_)
