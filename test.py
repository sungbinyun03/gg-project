import spacy
from imdb import Cinemagoer, IMDbDataAccessError
import wikipedia
from rapidfuzz import fuzz

summary = wikipedia.summary("Best performance by an actor in a drama", sentences=2)
print(summary)

# nlp = spacy.load("en_core_web_trf")
# doc = nlp(
# "Sherlock should have won that But congrats to Kevin for Hatfields and McCoys ")
# ia = Cinemagoer()

# show = ia.search_person("Les Miserables", results = 1)
# similarity_score = fuzz.ratio("les miserables", show[0]['name'].lower())

# print("show: ", similarity_score)
# for token in doc:
#     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
#             token.shape_, token.is_alpha, token.is_stop)
# # for ent in doc.ents:
# #     print(ent.text, ent.start_char, ent.end_char, ent.label_)