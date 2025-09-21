# Resume_Paser_By_Ai
n AI-powered Resume Parser built with FastAPI and Google Gemini. It extracts structured JSON data from PDF/DOCX resumes.


# Features

> Upload PDF or DOCX resumes.
> Parse resumes into structured JSON format.
> Uses Google Gemini AI for accurate parsing.
> Handles large resumes by splitting into chunks.

# Requirements

> Python 3.13+
> FastAPI
> uvicorn
> pdfplumber
> python-docx
> google-generativeai
> python-multipart

# Setup & Installation

# 1.Create and activate a virtual environment

  # > Windows:
 python -m venv venv
  # > Mac/Linux
 python3 -m venv venv

# 2.Install dependencies
pip install fastapi uvicorn pdfplumber python-docx google-generativeai python-multipart

# 3 Configure your Gemini AI API Key
Open app.py and replace:

# Run the App
uvicorn app:app --reload

Open your browser at: http://127.0.0.1:8000/docs

Use the POST /parse_resume/ endpoint to upload PDF/DOCX resumes and get JSON output.




  


