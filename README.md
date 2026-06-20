# CareerLens AI

### AI Opportunity Recommendation & Talent Matchmaking Platform

CareerLens AI helps students discover better career opportunities while enabling recruiters to screen and match talent faster using AI.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![AI](https://img.shields.io/badge/AI-Gemini%20%7C%20NLP-purple)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## Problem Statement

Students often struggle to find opportunities that genuinely match their skills, interests, eligibility, and career goals. Most platforms focus on listings, but do not clearly show which opportunities fit a student profile or which skills need improvement.

Recruiters also face large applicant pools, resume overload, manual screening, and weak candidate-job matching.

CareerLens AI bridges both sides through AI-powered opportunity discovery and recruiter-focused talent matchmaking.

---

## What is CareerLens AI?

CareerLens AI is a role-based AI career platform with two separate experiences:

### Student Portal

- Register or login as a student
- Upload resume in PDF, DOCX, or TXT format
- Extract skills, education, projects, and experience
- Get opportunity recommendations
- View skill-gap insights and career guidance

### Recruiter Portal

- Register or login as a recruiter
- Search candidates by role, skill, fit score, and status
- Move candidates through a shortlist pipeline
- Match posted jobs with the best candidates
- Generate AI-style candidate summaries and interview focus areas
- Post new opportunities
- View hiring analytics

---

## Latest Features

### Role-Based Authentication

- Separate login and register flow
- New users can register as Student or Recruiter
- Existing users can login with demo credentials
- Portal menu changes based on selected role

### User Feedback Form

- Students and recruiters can submit feedback from inside the app
- Captures rating, category, recommendation intent, optional contact, and comments
- Saves responses to `data/feedback.csv`
- Shows recent feedback responses with CSV download support for demo review

### Candidate Shortlist Board

Recruiters can move candidates through hiring stages:

```text
New -> Shortlisted -> Interview -> Selected -> Rejected
```

### Job-to-Candidate Matching

Recruiters can select an opportunity and rank candidates by skill match. The app shows:

- Match score
- Matched skills
- Missing skills
- Candidate status
- Existing fit score

### AI Candidate Summary

Recruiters can view a concise AI-style summary for each candidate, including:

- Candidate strengths
- Target role fit
- Screening recommendation
- Interview focus questions

---

## Core Features

### AI Resume Intelligence

Students can upload resumes in:

- PDF
- DOCX
- TXT

The system extracts:

- Skills
- Education
- Projects
- Experience
- Profile summary

### Opportunity Recommendation Engine

CareerLens AI recommends:

- Internships
- Jobs
- Hackathons
- Scholarships
- Fellowships

Powered by:

- Sentence Transformers
- Semantic similarity
- Cosine similarity
- TF-IDF fallback
- Hybrid recommendation logic

### Skill Gap Detection

The app identifies missing skills that can improve a student's match score.

Example:

```text
Current Match: 72%
Learn Docker + FastAPI -> Match could improve to 88%
```

### Recruiter Matchmaking

Recruiters can:

- Discover relevant candidates faster
- Filter candidates intelligently
- View fit scores
- Track hiring pipeline status
- Compare candidates against job requirements
- Generate interview focus areas

---

## Application Preview

### Login & Authentication

<p align="center">
<img src="assets/login-page.png" width="900">
</p>

### Student Portal

<p align="center">
<img src="assets/student-portal.png" width="900">
</p>

Student features:

- Opportunity browsing
- Resume matching
- Skill-gap analysis
- Personalized recommendations
- Career guidance

### Recruiter Dashboard

<p align="center">
<img src="assets/recruiter-dashboard.png" width="900">
</p>

Recruiter features:

- Candidate search
- Candidate shortlist board
- Job-to-candidate matching
- AI candidate summaries
- Opportunity posting
- Hiring analytics
- User feedback collection

---

## Tech Stack

### Frontend

- Streamlit
- streamlit-option-menu
- Plotly

### Backend

- Python
- FastAPI

### AI / NLP

- Google Gemini API
- Sentence Transformers
- spaCy
- scikit-learn

### Recommendation Engine

- FAISS
- Cosine Similarity
- TF-IDF fallback

### Resume Parsing

- PyMuPDF
- pdfplumber
- python-docx

### Database Ready

- PostgreSQL
- SQLAlchemy

The current version includes demo/session-based data for easy local testing. PostgreSQL can be connected for production storage.

Feedback submissions are stored in `data/feedback.csv` for a simple file-based backend.

---

## System Architecture

```text
Student Resume Upload
        |
Resume Parsing
        |
Skill Extraction
        |
Embedding / TF-IDF Matching
        |
Opportunity Dataset
        |
Fit Score + Recommendations
        |
Skill Gap Insights

Recruiter Login
        |
Candidate Search
        |
Shortlist Pipeline
        |
Job-to-Candidate Matching
        |
AI Candidate Summary
        |
Hiring Analytics
```

---

## Project Structure

```text
backend/
  main.py
  recommender.py
  resume_parser.py

data/
  opportunities.csv

assets/
  login-page.png
  student-portal.png
  recruiter-dashboard.png

streamlit_app.py
requirements.txt
README.md
```

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/AryaLolusare2712/CareerLens-AI.git
cd CareerLens-AI
```

### 2. Create Virtual Environment

Windows:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

Linux / Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running CareerLens AI

Start the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

Start the frontend in another terminal:

```bash
streamlit run streamlit_app.py
```

The Streamlit app also supports demo mode when the backend is unavailable.

---

## Gemini Setup

Create a `.env` file:

```text
GEMINI_API_KEY=your_api_key
API_BASE_URL=http://localhost:8000
```

Gemini is used for:

- Resume guidance
- Career suggestions
- AI candidate summaries
- Personalized profile insights

Do not upload `.env` to GitHub.

---

## Demo Accounts

Student:

```text
student@example.com
student123
```

Recruiter:

```text
recruiter@example.com
recruiter123
```

---

## Future Roadmap

- Persistent PostgreSQL authentication
- Saved recruiter job postings
- Resume builder
- Candidate comparison view
- AI interview question generator
- Persistent feedback storage with PostgreSQL
- Live opportunity scraping
- LinkedIn/GitHub profile integration
- Multi-agent recommendation workflow
- Deployment on Streamlit Cloud and Railway

---

## Resume Description

```text
CareerLens AI | Streamlit, FastAPI, Gemini, FAISS
- Built a role-based platform where students upload resumes and get AI-powered job/internship recommendations with skill-gap insights.
- Added recruiter portal with candidate search, shortlist board, job-to-candidate matching, AI summaries, opportunity posting, and analytics.
```

---

## Vision

CareerLens AI aims to become a career intelligence and AI-powered talent matchmaking ecosystem for students and recruiters.
