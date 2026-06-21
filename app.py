from flask import Flask, render_template, request
import os
from PyPDF2 import PdfReader
import spacy
from docx import Document
from skills import TECHNICAL_SKILLS, SOFT_SKILLS

nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"   # upload chesey files store avvadani ki idi path
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER # upload chesina files ikkada store avuthayi 

def extract_keywords(job_description):  # job description nundi keywords ni extract chesey function
    doc = nlp(job_description)  # spacy library ni use chesi jd ni process chesthundhi
    keywords = set()    # unique keywords ni store cheyadaniki set ni use chesthunam

    generic_words = {
        "developer",
        "experience",
        "skill",
        "skills",
        "knowledge"
    }

    for chunk in doc.noun_chunks:
        #print(chunk.text)
        cleaned_words = []  

        for token in chunk: 
            word = token.lemma_.lower()

            if token.is_alpha and not token.is_stop:
                if word not in generic_words:
                    cleaned_words.append(word)
        
        if cleaned_words:
            phrase = " ".join(cleaned_words)
            keywords.add(phrase)

    return list(keywords)

def extract_technical_skills(job_description):
    
    jd = job_description.lower()
    jd_words = jd.split()

    found_skills = []

    for skill in TECHNICAL_SKILLS:
        if len(skill.split()) == 1:
            if skill.lower() in jd_words:
                found_skills.append(skill)
        else:
            if skill.lower() in jd:
                found_skills.append(skill)

    return found_skills

def extract_soft_skills(job_description):
    
    jd = job_description.lower()

    found_skills = []

    for skill in SOFT_SKILLS:
        if skill.lower() in jd:
            found_skills.append(skill)

    return found_skills

def extract_text(filepath):
    text = ""

    if filepath.endswith(".pdf"):
        reader = PdfReader(filepath)

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

    elif filepath.endswith(".docx"):
        doc = Document(filepath)

        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"

    return text

def extract_section(text):

    lines = text.split("\n")

    sections = {
        "skills": "",
        "projects": "",
        "experience": "",
        "education": ""
    }

    current_section = None

    section_keywords = {
        "skills": ["skills", "technical skills"],
        "projects": ["projects", "personal projects"],
        "experience": ["experience", "work experience"],
        "education": ["education", "academic background"]
    }

    for line in lines:

        clean_line = " ".join(line.split()).lower()
        clean_line = line.strip().lower()

        for section, keywords in section_keywords.items():
           if any(keyword in clean_line for keyword in keywords):
                current_section = section 
                break

        else:
            if current_section:
                sections[current_section] +=line + "\n"

    return sections


def analyze_resume(filepath, job_description):
    text = extract_text(filepath)

    sections = extract_section(text)
    technical_skills = extract_technical_skills(job_description)
    soft_skills = extract_soft_skills(job_description)

    resume_text = text.lower()

    keywords = extract_technical_skills(job_description)
    print("keywords:", extract_keywords(job_description))
    print("technical:", extract_technical_skills(job_description))
    print("soft:", extract_soft_skills(job_description))
    # print("Extracted Keywords:", keywords)
    
    score = 0
    found_skills = []
    suggestions = []

    resume_doc = nlp(resume_text)
    
    resume_words = set()


    for token in resume_doc:
        if token.is_alpha:
            resume_words.add(token.lemma_.lower())

    print("keywords:", keywords)
    print("total keywords:", len(keywords))
    for word in keywords:
        keyword_parts = word.split()
        Matched = True
        for keyword_part in keyword_parts:
        #print(word, word in resume_words)
         if keyword_part not in resume_words:
            Matched = False
            #print(f"resume_words:", resume_words)
            #print("checking:", word)
            #print("parts:", keyword_parts)

        if Matched:
            score +=1
            found_skills.append(word)
        else:
            suggestions.append(f"Consider adding {word}")
                
    total_keywords = len(keywords)

    if total_keywords > 0:
        percentage = int((score / total_keywords) * 100)
    else:
        percentage = 0
    
    # print("Keywords:", keywords)
    # print("Score:", score)
    # print("Total Keywords:", total_keywords)
    # print("Percentage:", percentage)

    return percentage, found_skills, suggestions

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files["resume"]
        job_description = request.form["job_description"]

        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            percentage, skills, suggestions = analyze_resume(filepath, job_description)

            print("Reached this point")
            print("Percentage:", percentage)
            #print("Skills:", skills)
            #print("Suggestions:", suggestions)
            #print(type(extract_keywords))
            #print(type(analyze_resume))

            return render_template (
                "result.html",
                percentage=percentage,
                skills=skills,
                suggestions=suggestions
            )
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
