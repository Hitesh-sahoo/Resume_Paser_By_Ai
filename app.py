from fastapi import FastAPI, UploadFile, File
import pdfplumber
import docx
import google.generativeai as genai
import json
import re

# CONFIGURE GEMINI API
genai.configure(api_key="Your_gemini_Api_key")
model = genai.GenerativeModel("gemini-1.5-flash")

# Extract text from PDF

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# from docx
def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def chunk_text(text, chunk_size=3000):
    """Split text into smaller chunks for Gemini"""
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

# Gemini Ai 
def parse_resume_with_gemini(resume_text):
    prompt = f"""
    Behave like a resume parser. Extract details from the given resume text
    and return JSON in this format:

    {{
      "name": "",
      "title": "",
      "location": "",
      "email": "",
      "linkedin": "",
      "summary": "",
      "key_skills": [],
      "technical_skills": {{
        "Data Engineering": [],
        "Programming": [],
        "Databases": [],
        "Cloud": [],
        "DevOps": [],
        "Data Science & Visualization": [],
        "Other Tools": [],
        "Business Domains": []
      }},
      "education": [
        {{
          "degree": "",
          "institution": "",
          "year": ""
        }}
      ],
      "certifications": [],
      "experience": [
        {{
          "company": "",
          "title": "",
          "location": "",
          "duration": "",
          "responsibilities": [],
          "tools": []
        }}
      ]
    }}

    Resume Text:
    {resume_text}
    """
    response = model.generate_content(prompt)

    try:
        resume_json = json.loads(response.text)
    except:
        cleaned_text = re.sub(r"```json|```", "", response.text).strip()
        resume_json = json.loads(cleaned_text)

    return resume_json

def merge_json(results):
    """Merge multiple chunked outputs into one JSON"""
    final = {
        "name": "",
        "title": "",
        "location": "",
        "email": "",
        "linkedin": "",
        "summary": "",
        "key_skills": [],
        "technical_skills": {
            "Data Engineering": [],
            "Programming": [],
            "Databases": [],
            "Cloud": [],
            "DevOps": [],
            "Data Science & Visualization": [],
            "Other Tools": [],
            "Business Domains": []
        },
        "education": [],
        "certifications": [],
        "experience": []
    }

    for res in results:
        for key in ["name", "title", "location", "email", "linkedin", "summary"]:
            if res.get(key) and not final[key]:
                final[key] = res[key]

        final["key_skills"].extend(res.get("key_skills", []))

        if "technical_skills" in res:
            for cat in final["technical_skills"].keys():
                final["technical_skills"][cat].extend(res["technical_skills"].get(cat, []))

        final["education"].extend(res.get("education", []))
        final["certifications"].extend(res.get("certifications", []))
        final["experience"].extend(res.get("experience", []))

    # remove duplicates
    final["key_skills"] = list(set(final["key_skills"]))
    for cat in final["technical_skills"].keys():
        final["technical_skills"][cat] = list(set(final["technical_skills"][cat]))

    return final

# FASTAPI APP

app = FastAPI(title="Resume Parser By AI")

@app.post("/parse_resume/")
async def parse_resume(file: UploadFile = File(...)):
    # Extract text
    if file.filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(file.file)
    elif file.filename.endswith(".docx"):
        resume_text = extract_text_from_docx(file.file)
    else:
        return {"error": "Unsupported file format. Please upload PDF or DOCX."}

    # Process with Gemini
    try:
        results = []
        for chunk in chunk_text(resume_text, chunk_size=3000):
            part = parse_resume_with_gemini(chunk)
            results.append(part)

        final_json = merge_json(results)

        return {"parsed_resume": final_json}

    except Exception as e:
        return {"error": str(e)}
