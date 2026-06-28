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
    section_status = {
    "skills": bool(sections["skills"]),
    "projects": bool(sections["projects"]),
    "experience": bool(sections["experience"]),
    "education": bool(sections["education"])
    }

    resume_text = text.lower()

    required_technical_skills = extract_technical_skills(job_description)
    required_soft_skills = extract_soft_skills(job_description) 
    
    score = 0
    found_technical_skills = []
    found_soft_skills = []
    missing_technical_skills = []
    missing_soft_skills = []

    resume_doc = nlp(resume_text)
    resume_words = set()

    for token in resume_doc:
        if token.is_alpha:
            resume_words.add(token.lemma_.lower())
            resume_words.add(token.text.lower())

    for word in required_technical_skills:
        keyword_parts = word.split()
        matched = True
        for keyword_part in keyword_parts:
         if keyword_part not in resume_words:
            matched = False

        if matched:
            score +=2
            found_technical_skills.append(word)
        else:
            missing_technical_skills.append(f"Consider adding {word}")

    for word in required_soft_skills:
        keyword_parts = word.split()
        matched = True
        for keyword_part in keyword_parts:
         if keyword_part not in resume_words:
            matched = False

        if matched:
            score +=1
            found_soft_skills.append(word)
        else:
            missing_soft_skills.append(f"Consider adding {word}")
                
    technical_count = len(required_technical_skills)
    soft_count = len(required_soft_skills)

    maximum_score = (technical_count * 2 + soft_count * 1)

    if maximum_score > 0 :
        percentage = int((score / maximum_score) * 100)
    else:
        percentage = 0

    print(section_status)
    return percentage, found_technical_skills, found_soft_skills, missing_technical_skills, missing_soft_skills, section_status

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files["resume"]
        job_description = request.form["job_description"]

        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            percentage,  found_technical_skills, found_soft_skills, missing_technical_skills, missing_soft_skills, section_status = analyze_resume(filepath, job_description)

            return render_template (
                "result.html",
                percentage=percentage,
                found_technical_skills = found_technical_skills,
                found_soft_skills = found_soft_skills,
                missing_technical_skills = missing_technical_skills,
                missing_soft_skills =missing_soft_skills,
                section_status = section_status
            )
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)