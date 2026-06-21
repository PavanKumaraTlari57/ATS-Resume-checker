import spacy

nlp = spacy.load("en_core_web_sm")

job_description = """
"Looking for a Java Developer with Spring Boot and Docker."
"""

doc = nlp(job_description)

keywords = []

for token in doc:
    if token.pos_ in ["NOUN", "PROPN"]:
        if not token.is_stop and token.is_alpha:
            keywords.append(token.text.lower())

print("Extracted Keywords:")
print(keywords)
