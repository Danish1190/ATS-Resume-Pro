"""
ATS Analyzer — scores resumes against job requirements.
Scores: skill match, keyword density, experience, education → weighted ATS score.
"""
import re
import json
from datetime import datetime

# ─── SKILL TAXONOMY ───────────────────────────────────────────────────────────
TECH_SKILLS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
    # Web
    "html", "css", "react", "angular", "vue", "node.js", "nodejs", "next.js",
    "django", "flask", "fastapi", "spring", "express", "jquery", "bootstrap",
    "tailwind", "graphql", "rest", "api", "restful",
    # Data & ML
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
    "data analysis", "data science", "statistics", "tableau", "power bi",
    "excel", "sql", "nosql", "spark", "hadoop", "kafka",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
    "github actions", "terraform", "ansible", "linux", "bash", "git",
    "devops", "microservices", "serverless",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle",
    "sqlite", "cassandra", "dynamodb",
    # Other
    "agile", "scrum", "jira", "testing", "unit testing", "selenium",
    "cybersecurity", "networking", "blockchain", "iot",
]

SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "problem solving", "critical thinking",
    "time management", "adaptability", "creativity", "collaboration", "presentation",
    "project management", "analytical", "detail oriented", "self motivated",
]

EDUCATION_KEYWORDS = {
    "phd": 5, "ph.d": 5, "doctorate": 5,
    "master": 4, "msc": 4, "mba": 4, "m.tech": 4, "m.e": 4,
    "bachelor": 3, "bsc": 3, "b.tech": 3, "b.e": 3, "b.com": 3, "ba ": 3,
    "associate": 2, "diploma": 2,
    "high school": 1, "secondary": 1,
}

EXPERIENCE_PATTERNS = [
    r"(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)",
    r"(\d+)\+?\s*yrs?\s*(?:of\s*)?(?:experience|exp)",
    r"experience\s*(?:of\s*)?(\d+)\+?\s*years?",
    r"(?:worked|working)\s+for\s+(\d+)\+?\s*years?",
]

DATE_PATTERNS = [
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"\s+(\d{4})",
    r"(\d{4})\s*[-–—]\s*(?:present|current|now|\d{4})",
]


def analyze_resume(resume_obj, job_obj) -> dict:
    """
    Analyze a Resume against a Job and return a score dict.
    """
    text = (resume_obj.raw_text or "").lower()
    if not text.strip():
        return _empty_result()

    required_skills = job_obj.skills_list  # list of strings
    job_description = (job_obj.description or "").lower()
    job_requirements = (job_obj.requirements or "").lower()
    job_text = job_description + " " + job_requirements

    # ── 1. Extract candidate info ─────────────────────────────────────
    name = _extract_name(resume_obj.raw_text or "")
    email = _extract_email(resume_obj.raw_text or "")
    phone = _extract_phone(resume_obj.raw_text or "")

    # ── 2. Extract skills from resume ────────────────────────────────
    extracted_skills = _extract_skills(text)

    # ── 3. Skill matching ─────────────────────────────────────────────
    req_lower = [s.lower().strip() for s in required_skills if s.strip()]
    if req_lower:
        matched_skills = [s for s in req_lower if s in text or
                          any(s in skill for skill in extracted_skills)]
        missing_skills = [s for s in req_lower if s not in matched_skills]
        skill_score = (len(matched_skills) / len(req_lower)) * 100
    else:
        # No explicit skills required — score based on extracted vs all known skills
        matched_skills = extracted_skills
        missing_skills = []
        skill_score = min(len(extracted_skills) * 5, 100)

    # ── 4. Keyword / relevance score ─────────────────────────────────
    keyword_score = _keyword_score(text, job_text)

    # ── 5. Experience score ───────────────────────────────────────────
    years_exp = _extract_experience_years(resume_obj.raw_text or "")
    exp_min = job_obj.experience_min or 0
    exp_max = job_obj.experience_max or 10
    experience_score = _score_experience(years_exp, exp_min, exp_max)

    # ── 6. Education score ────────────────────────────────────────────
    edu_level, education_score = _score_education(text)

    # ── 7. Weighted ATS Score ─────────────────────────────────────────
    if req_lower:
        ats_score = (
            skill_score * 0.40 +
            keyword_score * 0.25 +
            experience_score * 0.20 +
            education_score * 0.15
        )
    else:
        ats_score = (
            skill_score * 0.20 +
            keyword_score * 0.40 +
            experience_score * 0.25 +
            education_score * 0.15
        )

    ats_score = round(min(max(ats_score, 0), 100), 2)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "ats_score": ats_score,
        "skill_score": round(skill_score, 2),
        "keyword_score": round(keyword_score, 2),
        "experience_score": round(experience_score, 2),
        "education_score": round(education_score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extracted_skills": extracted_skills[:30],
        "years_experience": years_exp,
        "education_level": edu_level,
    }


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _empty_result():
    return {
        "name": "Unknown", "email": "", "phone": "",
        "ats_score": 0, "skill_score": 0, "keyword_score": 0,
        "experience_score": 0, "education_score": 0,
        "matched_skills": [], "missing_skills": [], "extracted_skills": [],
        "years_experience": 0, "education_level": "",
    }


def _extract_name(text: str) -> str:
    """Heuristic: first non-empty line with 2-4 capitalized words."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:10]:
        # Skip lines with email/phone/url patterns
        if re.search(r"[@:/\d]", line):
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            return line
    return lines[0][:60] if lines else "Unknown"


def _extract_email(text: str) -> str:
    match = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def _extract_phone(text: str) -> str:
    patterns = [
        r"\+?[\d\s\-().]{10,15}",
        r"\b\d{10}\b",
        r"\(\d{3}\)\s*\d{3}[-.\s]\d{4}",
        r"\d{3}[-.\s]\d{3}[-.\s]\d{4}",
    ]
    for p in patterns:
        match = re.search(p, text)
        if match:
            candidate = re.sub(r"[^\d+]", "", match.group(0))
            if 10 <= len(candidate) <= 15:
                return match.group(0).strip()
    return ""


def _extract_skills(text: str) -> list:
    found = []
    all_skills = TECH_SKILLS + SOFT_SKILLS
    for skill in all_skills:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)
    return list(set(found))


def _keyword_score(resume_text: str, job_text: str) -> float:
    """TF-IDF inspired keyword overlap score."""
    if not job_text.strip():
        return 50.0
    # Extract meaningful words from job (length > 3, alpha)
    job_words = set(w for w in re.findall(r"\b[a-zA-Z]{4,}\b", job_text.lower())
                    if w not in _STOPWORDS)
    if not job_words:
        return 50.0
    matched = sum(1 for w in job_words if w in resume_text)
    return round((matched / len(job_words)) * 100, 2)


def _extract_experience_years(text: str) -> float:
    """Try explicit patterns first, then date counting."""
    text_lower = text.lower()
    for pattern in EXPERIENCE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return float(match.group(1))
    # Count year ranges
    year_pattern = r"(\d{4})\s*[-–—]\s*(present|current|now|(\d{4}))"
    matches = re.findall(year_pattern, text_lower)
    total = 0
    current_year = datetime.utcnow().year
    for m in matches:
        start = int(m[0])
        end_str = m[1]
        if end_str in ("present", "current", "now"):
            end = current_year
        else:
            try:
                end = int(m[2])
            except (ValueError, IndexError):
                end = current_year
        if 1970 <= start <= current_year and start <= end:
            total += end - start
    return min(float(total), 30)


def _score_experience(years: float, exp_min: int, exp_max: int) -> float:
    if years == 0:
        return 10.0
    if years >= exp_min:
        if years <= exp_max:
            return 100.0
        else:
            # Over-qualified — slight penalty
            over = years - exp_max
            return max(70.0, 100.0 - over * 3)
    else:
        ratio = years / max(exp_min, 1)
        return round(ratio * 80, 2)


def _score_education(text: str) -> tuple:
    best_level = ""
    best_score = 0
    for keyword, score in EDUCATION_KEYWORDS.items():
        if keyword in text:
            if score > best_score:
                best_score = score
                best_level = keyword.title()
    score_map = {5: 100, 4: 90, 3: 75, 2: 55, 1: 35, 0: 20}
    return best_level or "Not specified", score_map.get(best_score, 20)


_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "have", "will", "from",
    "your", "are", "our", "their", "you", "who", "which", "what", "when",
    "where", "able", "must", "should", "would", "could", "into", "about",
    "also", "more", "than", "well", "strong", "good", "excellent", "skills",
    "experience", "work", "team", "role", "candidate", "looking",
}
