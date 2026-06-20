from __future__ import annotations

import os
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

from backend.recommender import OpportunityRecommender, load_opportunities
from backend.resume_parser import extract_profile, extract_text_from_upload


load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
FEEDBACK_COLUMNS = ["submitted_at", "name", "role", "rating", "category", "would_recommend", "contact", "message"]
FEEDBACK_PATH = Path(__file__).resolve().parent / "data" / "feedback.csv"


st.set_page_config(page_title="AI Career Opportunity Matcher", page_icon=":briefcase:", layout="wide")


def main() -> None:
    if not st.session_state.get("authenticated"):
        render_login_page()
        return

    role = st.session_state.get("role", "Student")
    user_name = st.session_state.get("user_name", "User")

    st.title(f"{role} Portal")
    st.caption(f"Welcome, {user_name}.")

    with st.sidebar:
        st.write(f"Signed in as **{role}**")
        if st.button("Logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state.pop("role", None)
            st.session_state.pop("user_name", None)
            st.rerun()

        if role == "Student":
            page = option_menu(
                "Student Portal",
                ["Student Home", "Resume Match", "Skill Gaps", "Feedback"],
                icons=["house", "file-earmark-person", "graph-up-arrow", "chat-left-text"],
                default_index=0,
            )
        else:
            page = option_menu(
                "Recruiter Portal",
                [
                    "Recruiter Home",
                    "Candidate Search",
                    "Shortlist Board",
                    "Job Match",
                    "AI Summary",
                    "Post Opportunity",
                    "Hiring Analytics",
                    "Feedback",
                ],
                icons=[
                    "briefcase",
                    "people",
                    "kanban",
                    "bullseye",
                    "stars",
                    "plus-square",
                    "bar-chart",
                    "chat-left-text",
                ],
                default_index=0,
            )

    if role == "Student":
        if page == "Student Home":
            render_student_home()
        elif page == "Resume Match":
            render_resume_match()
        elif page == "Skill Gaps":
            render_student_skill_gaps()
        else:
            render_feedback_page(role, user_name)
    else:
        if page == "Recruiter Home":
            render_recruiter_home()
        elif page == "Candidate Search":
            render_recruiter_portal()
        elif page == "Shortlist Board":
            render_shortlist_board()
        elif page == "Job Match":
            render_job_candidate_matching()
        elif page == "AI Summary":
            render_ai_candidate_summary()
        elif page == "Post Opportunity":
            render_post_opportunity()
        elif page == "Hiring Analytics":
            render_analytics()
        else:
            render_feedback_page(role, user_name)


def render_login_page() -> None:
    st.title("AI Career Opportunity Matcher")
    st.caption("Login if you already have an account, or register as a new user.")

    if "users" not in st.session_state:
        st.session_state["users"] = {
            "student@example.com": {"name": "Demo Student", "password": "student123", "role": "Student"},
            "recruiter@example.com": {"name": "Demo Recruiter", "password": "recruiter123", "role": "Recruiter"},
        }

    left, right = st.columns([0.95, 1.05])
    with left:
        auth_mode = st.radio("Account action", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
        if auth_mode == "Login":
            render_login_form()
        else:
            render_register_form()

    with right:
        st.subheader("Demo Accounts")
        st.write("Student: student@example.com / student123")
        st.write("Recruiter: recruiter@example.com / recruiter123")
        st.info("New users can register as either Student or Recruiter from the register option.")


def render_login_form() -> None:
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

    if submitted:
        user = st.session_state["users"].get(email.strip().lower())
        if not user or user["password"] != password:
            st.error("Invalid email or password.")
            return
        complete_authentication(user)


def render_register_form() -> None:
    st.subheader("Register")
    role = st.radio("Register as", ["Student", "Recruiter"], horizontal=True)
    with st.form("register_form"):
        user_name = st.text_input("Full name")
        email = st.text_input("Email")
        password = st.text_input("Create password", type="password")
        confirm_password = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Register", type="primary", use_container_width=True)

    if submitted:
        email_key = email.strip().lower()
        if not user_name.strip() or not email_key or not password:
            st.warning("Enter name, email, and password to register.")
            return
        if password != confirm_password:
            st.error("Passwords do not match.")
            return
        if email_key in st.session_state["users"]:
            st.error("This email is already registered. Please login.")
            return

        user = {"name": user_name.strip(), "password": password, "role": role}
        st.session_state["users"][email_key] = user
        complete_authentication(user)


def complete_authentication(user: dict) -> None:
    st.session_state["authenticated"] = True
    st.session_state["role"] = user["role"]
    st.session_state["user_name"] = user["name"]
    st.rerun()


def render_student_home() -> None:
    opportunities = pd.DataFrame(load_opportunities())
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Open Opportunities", len(opportunities))
    col2.metric("Internships", int((opportunities["type"] == "Internship").sum()))
    col3.metric("Remote Options", int((opportunities["mode"] == "Remote").sum()))
    col4.metric("Scholarships", int((opportunities["type"] == "Scholarship").sum()))

    left, right = st.columns([1.15, 0.85])
    with left:
        st.subheader("Browse Opportunities")
        selected_type = st.multiselect(
            "Type",
            sorted(opportunities["type"].unique()),
            default=sorted(opportunities["type"].unique()),
        )
        filtered = opportunities[opportunities["type"].isin(selected_type)]
        st.dataframe(
            filtered[["title", "organization", "type", "location", "mode", "deadline"]],
            use_container_width=True,
            hide_index=True,
        )
    with right:
        st.subheader("Opportunity Mix")
        fig = px.pie(opportunities, names="type", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)


def render_resume_match() -> None:
    uploaded = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
    demo_text = st.text_area(
        "Or paste resume/profile text",
        height=180,
        placeholder="Example: Python, Streamlit, FastAPI, NLP, pandas, machine learning projects...",
    )

    if st.button("Analyze and Recommend", type="primary", use_container_width=True):
        profile = None
        if uploaded:
            profile = analyze_uploaded_resume(uploaded)
        elif demo_text.strip():
            profile = extract_profile(demo_text)

        if not profile:
            st.warning("Upload a resume or paste profile text first.")
            return

        st.session_state["profile"] = profile
        st.session_state["recommendations"] = recommend(profile)

    profile = st.session_state.get("profile")
    recommendations = st.session_state.get("recommendations")

    if profile and recommendations:
        show_profile(profile)
        show_recommendations(recommendations)


def analyze_uploaded_resume(uploaded) -> dict:
    try:
        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}
        response = requests.post(f"{API_BASE_URL}/analyze-resume", files=files, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception:
        return extract_profile_from_streamlit_upload(uploaded)


def extract_profile_from_streamlit_upload(uploaded) -> dict:
    buffer = BytesIO(uploaded.getvalue())
    return extract_profile(extract_text_from_upload(buffer, uploaded.name))


def recommend(profile: dict) -> dict:
    try:
        response = requests.post(f"{API_BASE_URL}/recommend", json=profile, params={"limit": 5}, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception:
        result = OpportunityRecommender().recommend(profile, limit=5)
        return {
            "opportunities": result.opportunities,
            "top_skills": result.top_skills,
            "missing_skills": result.missing_skills,
        }


def show_profile(profile: dict) -> None:
    st.subheader("Parsed Profile")
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.write(profile.get("summary", ""))
        st.info(profile.get("ai_guidance", "Add measurable project outcomes and align your resume with target role skills."))
    with col2:
        skills = profile.get("skills", [])
        if skills:
            st.write("Skills")
            st.write(", ".join(skills))
        st.metric("Resume Word Count", profile.get("word_count", 0))


def show_recommendations(recommendations: dict) -> None:
    st.subheader("Recommended Opportunities")
    for item in recommendations.get("opportunities", []):
        with st.container(border=True):
            col1, col2 = st.columns([0.76, 0.24])
            with col1:
                st.markdown(f"**{item['title']}**")
                st.caption(f"{item['organization']} - {item['type']} - {item['location']} - {item['mode']}")
                st.write(item["description"])
                st.caption(f"Skills: {item['skills']}")
            with col2:
                st.metric("Fit Score", f"{item['fit_score']}%")
                st.caption(f"Deadline: {item['deadline']}")

    missing = recommendations.get("missing_skills", [])
    if missing:
        st.subheader("Skill Gaps")
        st.write(", ".join(missing))


def render_student_skill_gaps() -> None:
    st.subheader("Student Skill Gaps")
    recommendations = st.session_state.get("recommendations")
    profile = st.session_state.get("profile")

    if not profile or not recommendations:
        st.info("Analyze your resume first to generate personalized skill gaps.")
        sample_profile = {
            "summary": "Student interested in AI internships with Python and data projects.",
            "skills": ["python", "pandas", "machine learning"],
        }
        recommendations = recommend(sample_profile)

    missing = recommendations.get("missing_skills", [])
    current = recommendations.get("top_skills", [])

    col1, col2 = st.columns(2)
    with col1:
        st.write("Current strengths")
        st.write(", ".join(current) if current else "No skills detected yet.")
    with col2:
        st.write("Recommended next skills")
        st.write(", ".join(missing) if missing else "No major gaps found.")

    if missing:
        roadmap = pd.DataFrame(
            {
                "skill": missing[:6],
                "priority": ["High", "High", "Medium", "Medium", "Medium", "Low"][: len(missing[:6])],
                "practice_task": [f"Build one mini project using {skill}" for skill in missing[:6]],
            }
        )
        st.dataframe(roadmap, use_container_width=True, hide_index=True)


def render_recruiter_home() -> None:
    candidates = get_recruiter_candidates()
    opportunities = pd.DataFrame(load_opportunities())
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Candidates", len(candidates))
    col2.metric("Avg. Fit Score", round(candidates["fit_score"].mean(), 1))
    col3.metric("Open Listings", len(opportunities))
    col4.metric("High Fit Candidates", int((candidates["fit_score"] >= 85).sum()))

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Top Candidates")
        st.dataframe(candidates.sort_values("fit_score", ascending=False), use_container_width=True, hide_index=True)
    with right:
        st.subheader("Candidate Fit Distribution")
        fig = px.histogram(candidates, x="fit_score", nbins=8, title="Fit Scores")
        st.plotly_chart(fig, use_container_width=True)


def render_recruiter_portal() -> None:
    st.subheader("Candidate Search")
    candidates = get_recruiter_candidates()
    col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
    with col1:
        keyword = st.text_input("Search skills or role", placeholder="python, fastapi, nlp...")
    with col2:
        min_score = st.slider("Minimum fit score", 0, 100, 75)
    with col3:
        status = st.selectbox("Status", ["All", "New", "Shortlisted", "Interview"])

    filtered = candidates[candidates["fit_score"] >= min_score]
    if keyword:
        query = keyword.lower()
        filtered = filtered[
            filtered["skills"].str.lower().str.contains(query)
            | filtered["target_role"].str.lower().str.contains(query)
        ]
    if status != "All":
        filtered = filtered[filtered["status"] == status]

    st.dataframe(filtered, use_container_width=True, hide_index=True)


def render_shortlist_board() -> None:
    st.subheader("Candidate Shortlist Board")
    st.caption("Move candidates through the hiring pipeline and track their current stage.")
    candidates = get_recruiter_candidates()
    stages = ["New", "Shortlisted", "Interview", "Selected", "Rejected"]

    candidate_name = st.selectbox("Candidate", candidates["name"].tolist())
    current_status = candidates.loc[candidates["name"] == candidate_name, "status"].iloc[0]
    new_status = st.selectbox("Move to stage", stages, index=stages.index(current_status))

    if st.button("Update Stage", type="primary"):
        update_candidate_status(candidate_name, new_status)
        st.success(f"{candidate_name} moved to {new_status}.")
        st.rerun()

    columns = st.columns(len(stages))
    for column, stage in zip(columns, stages):
        with column:
            stage_candidates = candidates[candidates["status"] == stage]
            st.markdown(f"**{stage}**")
            st.metric("Count", len(stage_candidates))
            for _, candidate in stage_candidates.iterrows():
                with st.container(border=True):
                    st.write(candidate["name"])
                    st.caption(candidate["target_role"])
                    st.progress(int(candidate["fit_score"]))
                    st.caption(f"Fit: {candidate['fit_score']}%")


def render_job_candidate_matching() -> None:
    st.subheader("Job-to-Candidate Matching")
    opportunities = pd.DataFrame(load_opportunities())
    candidates = get_recruiter_candidates()

    selected_title = st.selectbox("Select opportunity", opportunities["title"].tolist())
    selected_job = opportunities[opportunities["title"] == selected_title].iloc[0]
    required_skills = split_skills(selected_job["skills"])

    st.write(selected_job["description"])
    st.caption(f"Required skills: {', '.join(sorted(required_skills))}")

    ranked = candidates.copy()
    ranked["match_score"] = ranked["skills"].apply(lambda value: calculate_skill_match(split_skills(value), required_skills))
    ranked["matched_skills"] = ranked["skills"].apply(
        lambda value: ", ".join(sorted(split_skills(value) & required_skills)) or "No direct match"
    )
    ranked["missing_skills"] = ranked["skills"].apply(
        lambda value: ", ".join(sorted(required_skills - split_skills(value))) or "None"
    )
    ranked = ranked.sort_values(["match_score", "fit_score"], ascending=False)

    st.dataframe(
        ranked[["name", "target_role", "status", "fit_score", "match_score", "matched_skills", "missing_skills"]],
        use_container_width=True,
        hide_index=True,
    )


def render_ai_candidate_summary() -> None:
    st.subheader("AI Candidate Summary")
    candidates = get_recruiter_candidates()
    candidate_name = st.selectbox("Choose candidate", candidates["name"].tolist())
    candidate = candidates[candidates["name"] == candidate_name].iloc[0].to_dict()

    left, right = st.columns([0.58, 0.42])
    with left:
        st.write(f"**Target role:** {candidate['target_role']}")
        st.write(f"**Skills:** {candidate['skills']}")
        st.write(f"**Status:** {candidate['status']}")
        st.metric("Fit Score", f"{candidate['fit_score']}%")
    with right:
        st.info(generate_candidate_summary(candidate))

    st.subheader("Interview Focus")
    focus = build_interview_focus(candidate)
    st.dataframe(focus, use_container_width=True, hide_index=True)


def render_post_opportunity() -> None:
    st.subheader("Post Opportunity")
    with st.form("post_opportunity"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title")
            organization = st.text_input("Organization")
            opportunity_type = st.selectbox("Type", ["Internship", "Job", "Hackathon", "Scholarship", "Fellowship"])
        with col2:
            location = st.text_input("Location")
            mode = st.selectbox("Mode", ["Remote", "Hybrid", "Onsite"])
            deadline = st.date_input("Deadline")

        skills = st.text_area("Required skills", placeholder="python, fastapi, postgresql, analytics")
        description = st.text_area("Description")
        submitted = st.form_submit_button("Preview Listing", type="primary", use_container_width=True)

    if submitted:
        st.success("Opportunity preview created. Database saving can be connected next.")
        st.json(
            {
                "title": title,
                "organization": organization,
                "type": opportunity_type,
                "location": location,
                "mode": mode,
                "skills": skills,
                "description": description,
                "deadline": str(deadline),
            }
        )


def render_analytics() -> None:
    st.subheader("Hiring Analytics")
    opportunities = pd.DataFrame(load_opportunities())
    candidates = get_recruiter_candidates()
    skill_counts = (
        opportunities["skills"]
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .head(12)
        .reset_index()
    )
    skill_counts.columns = ["skill", "count"]

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(skill_counts, x="count", y="skill", orientation="h", title="Most Requested Skills")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(candidates, x="target_role", y="fit_score", color="status", title="Candidate Pipeline")
        st.plotly_chart(fig, use_container_width=True)


def render_feedback_page(role: str, user_name: str) -> None:
    st.subheader("Feedback")
    st.caption("Share what worked well, what felt confusing, or what you want improved.")

    with st.form("feedback_form", clear_on_submit=True):
        col1, col2 = st.columns([0.45, 0.55])
        with col1:
            rating = st.slider("Overall rating", 1, 5, 4)
            category = st.selectbox(
                "Feedback category",
                ["Overall experience", "Student portal", "Recruiter portal", "Recommendations", "Login/Register", "Other"],
            )
        with col2:
            would_recommend = st.radio("Would you recommend this app?", ["Yes", "Maybe", "No"], horizontal=True)
            contact = st.text_input("Email or contact info (optional)")

        message = st.text_area(
            "Your feedback",
            placeholder="Tell us what to improve or what you liked...",
            height=140,
        )
        submitted = st.form_submit_button("Submit Feedback", type="primary", use_container_width=True)

    if submitted:
        if not message.strip():
            st.warning("Please write a short feedback message before submitting.")
            return

        entry = {
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": user_name,
            "role": role,
            "rating": rating,
            "category": category,
            "would_recommend": would_recommend,
            "contact": contact.strip(),
            "message": message.strip(),
        }
        save_feedback_entry(entry)
        st.success("Thanks for your feedback. It has been saved.")

    feedback_df = load_feedback_entries()
    if not feedback_df.empty:
        st.subheader("Recent Feedback")
        col1, col2, col3 = st.columns(3)
        col1.metric("Responses", len(feedback_df))
        col2.metric("Average Rating", round(feedback_df["rating"].mean(), 1))
        col3.metric("Recommend Yes", int((feedback_df["would_recommend"] == "Yes").sum()))

        st.dataframe(feedback_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Feedback CSV",
            data=feedback_df.to_csv(index=False).encode("utf-8"),
            file_name="careerlens_feedback.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("No feedback submitted yet.")


def load_feedback_entries() -> pd.DataFrame:
    if not FEEDBACK_PATH.exists():
        return pd.DataFrame(columns=FEEDBACK_COLUMNS)
    try:
        return pd.read_csv(FEEDBACK_PATH)
    except Exception:
        return pd.DataFrame(columns=FEEDBACK_COLUMNS)


def save_feedback_entry(entry: dict) -> None:
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = load_feedback_entries()
    updated = pd.concat([existing, pd.DataFrame([entry], columns=FEEDBACK_COLUMNS)], ignore_index=True)
    updated.to_csv(FEEDBACK_PATH, index=False)


def get_recruiter_candidates() -> pd.DataFrame:
    if "recruiter_candidates" not in st.session_state:
        st.session_state["recruiter_candidates"] = sample_candidates().to_dict(orient="records")
    return pd.DataFrame(st.session_state["recruiter_candidates"])


def update_candidate_status(candidate_name: str, status: str) -> None:
    for candidate in st.session_state.get("recruiter_candidates", []):
        if candidate["name"] == candidate_name:
            candidate["status"] = status
            break


def sample_candidates() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "name": "Aarav Sharma",
                "target_role": "ML Intern",
                "fit_score": 91,
                "skills": "python, nlp, pandas",
                "status": "Shortlisted",
                "experience": "Built NLP classifiers and resume parsing projects using Python.",
            },
            {
                "name": "Mira Iyer",
                "target_role": "Streamlit Developer",
                "fit_score": 86,
                "skills": "streamlit, plotly, sql",
                "status": "Interview",
                "experience": "Created analytics dashboards with Streamlit, Plotly, and SQL data sources.",
            },
            {
                "name": "Kabir Khan",
                "target_role": "Backend API Intern",
                "fit_score": 82,
                "skills": "fastapi, postgresql, jwt",
                "status": "New",
                "experience": "Developed FastAPI endpoints, JWT auth flows, and PostgreSQL schemas.",
            },
            {
                "name": "Diya Mehta",
                "target_role": "Data Analyst Intern",
                "fit_score": 78,
                "skills": "pandas, plotly, statistics",
                "status": "New",
                "experience": "Analyzed datasets, built charts, and prepared business insight reports.",
            },
        ]
    )


def split_skills(value: str) -> set[str]:
    return {skill.strip().lower() for skill in str(value).split(",") if skill.strip()}


def calculate_skill_match(candidate_skills: set[str], required_skills: set[str]) -> int:
    if not required_skills:
        return 0
    return round(len(candidate_skills & required_skills) / len(required_skills) * 100)


def generate_candidate_summary(candidate: dict) -> str:
    skills = split_skills(candidate["skills"])
    strongest = ", ".join(sorted(skills)[:3])
    if candidate["fit_score"] >= 85:
        decision = "Strong candidate for immediate shortlist or interview."
    elif candidate["fit_score"] >= 75:
        decision = "Good candidate, but validate project depth before moving ahead."
    else:
        decision = "Needs closer screening before shortlisting."
    return (
        f"{candidate['name']} is targeting {candidate['target_role']} with strengths in {strongest}. "
        f"{candidate['experience']} {decision}"
    )


def build_interview_focus(candidate: dict) -> pd.DataFrame:
    skills = sorted(split_skills(candidate["skills"]))
    questions = [
        {
            "area": skill,
            "question": f"Describe one project where you used {skill} and what result it produced.",
        }
        for skill in skills[:4]
    ]
    questions.append(
        {
            "area": "Role fit",
            "question": f"Why are you a strong fit for the {candidate['target_role']} role?",
        }
    )
    return pd.DataFrame(questions)


if __name__ == "__main__":
    main()
