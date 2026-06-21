import spacy

nlp = spacy.load("en_core_web_sm")

text = "Python and Flask are important skills for AI Resume Analyzer."

doc = nlp(text)

for token in doc:
    print(token.text, "->", token.pos_)