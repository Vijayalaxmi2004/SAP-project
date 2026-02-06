import streamlit as st
import docx2txt  # type: ignore
import PyPDF2    # type: ignore
import re

st.set_page_config(page_title="Resume Parser", page_icon="📄")
st.title("📄 Resume Parser & Job Match Analyzer")

# ---------------- Helper Functions ---------------- #

def extract_text(file):
    if file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return docx2txt.process(file)

    return None


def clean_text(text):
    text = re.sub(r"\s+@", "@", text)
    text = re.sub(r"\s+\.", ".", text)
    return text


def extract_email(text):
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    matches = re.findall(pattern, text)
    return matches[0] if matches else "Not Found"


def extract_phone(text):
    pattern = r"\+?\d[\d -]{8,12}\d"
    matches = re.findall(pattern, text)
    return matches[0] if matches else "Not Found"


def extract_name(text):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        candidate = line.strip()
        if candidate and re.match(r"^[A-Za-z\s]+$", candidate):
            if not any(keyword in candidate.upper() for keyword in [
                "EDUCATION", "CERTIFICATIONS", "WORKSHOPS", "PROJECTS",
                "SKILLS", "RESPONSIBILITIES", "INTERNSHIPS"
            ]):
                return candidate

        if re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", line):
            for j in range(max(0, i - 2), i):
                candidate = lines[j].strip()
                if candidate and re.match(r"^[A-Za-z\s]+$", candidate):
                    return candidate

    return "Not Found"


SKILLS_LIST = [
    "Python", "Java", "C++", "SQL", "HTML", "CSS", "JavaScript",
    "Machine Learning", "Deep Learning", "Excel", "Power BI",
    "AWS", "React", "Django", "Flask", "TensorFlow", "PyTorch"
]


def extract_skills(text):
    return [skill for skill in SKILLS_LIST if re.search(rf"\b{skill}\b", text, re.I)]


def extract_education(text):
    edu_keywords = [
        "B.Tech", "M.Tech", "Bachelor", "Master", "Diploma", "PhD",
        "Intermediate", "High School", "SSC", "HSC"
    ]
    return [line.strip() for line in text.split("\n")
            if any(keyword in line for keyword in edu_keywords)] or ["Not Found"]


def calculate_match_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0, [], jd_skills

    matched = list(set(resume_skills) & set(jd_skills))
    missing = list(set(jd_skills) - set(resume_skills))

    score = (len(matched) / len(jd_skills)) * 100
    return round(score, 2), matched, missing


# ---------------- Streamlit UI ---------------- #

st.subheader("🧾 Job Description")
job_description = st.text_area(
    "Paste the job description or required skills here",
    height=200
)

uploaded_file = st.file_uploader(
    "Upload Resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

if uploaded_file:
    text = extract_text(uploaded_file)

    if not text:
        st.error("Unsupported file format!")
    else:
        text = clean_text(text)

        resume_skills = extract_skills(text)

        st.subheader("📑 Extracted Resume Information")
        st.write("**Name:**", extract_name(text))
        st.write("**Email:**", extract_email(text))
        st.write("**Phone:**", extract_phone(text))
        st.write("**Skills:**", ", ".join(resume_skills) if resume_skills else "Not Found")

        st.write("**Education:**")
        for edu in extract_education(text):
            st.write("-", edu)

        # -------- Job Match Analysis -------- #
        if job_description:
            jd_skills = extract_skills(job_description)

            score, matched, missing = calculate_match_score(
                resume_skills, jd_skills
            )

            st.subheader("📊 Resume Match Analysis")
            st.metric("Match Score", f"{score}%")

            st.write("✅ **Matched Skills:**")
            st.write(", ".join(matched) if matched else "None")

            st.write("❌ **Missing Skills:**")
            st.write(", ".join(missing) if missing else "None")
