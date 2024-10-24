import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp(     "Anne Hathaway wins if I dont win after I cut my hair Cindy Stele ",

)

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
            token.shape_, token.is_alpha, token.is_stop)
