# ATS PRO — Intelligent Applicant Tracking System

<div align="center">

![ATS PRO](https://img.shields.io/badge/ATS-PRO-6C63FF?style=for-the-badge&logo=robot&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

**A full-featured, AI-powered Applicant Tracking System built with Python & Flask.**  
Screen hundreds of resumes in seconds with smart scoring and beautiful analytics.

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **AI Resume Scoring** | Weighted ATS score based on skills, keywords, experience & education |
| 📄 **Multi-Format Support** | Upload PDF, DOC, DOCX, and TXT resumes simultaneously |
| 📊 **Live Analytics Dashboard** | KPI cards, bar charts, line trends, doughnut charts (Chart.js) |
| 🏆 **Candidate Leaderboard** | Visual podium for top 3 with ranked tables |
| 🔍 **Side-by-Side Comparison** | Compare all candidates on a single chart |
| 📤 **Export Reports** | Download PDF & CSV reports with one click |
| 🎯 **Skill Gap Analysis** | Matched vs. missing skills shown clearly |
| 🗂️ **Job Management** | Create, edit, filter, and manage multiple job postings |
| 🔒 **Auth System** | Register / login / profile with password hashing |
| 📝 **Recruiter Notes** | Add and save notes per candidate |
| 🔄 **Re-analyze** | Re-run ATS scoring on any resume at any time |
| 📱 **Responsive Design** | Works beautifully on desktop, tablet, and mobile |

---

## 🚀 Quick Start

### 1. Clone or navigate to the project
```bash
cd ats_website
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment (optional)
```bash
copy .env.example .env
# Edit .env to set your SECRET_KEY
```

### 4. Seed demo data (Recommended for instant full showcase)
```bash
python seed.py
```

### 5. Run the server
```bash
python run.py
```

### 6. Open your browser
```
http://127.0.0.1:5000
```

#### 🔑 Demo Credentials (or use 1-click auto-fill on the login screen):
- **Admin**: `admin@atspro.com` / `Admin@1234`
- **Recruiter**: `recruiter@atspro.com` / `Recruiter@1234`

---

## 📁 Project Structure

```
ats_website/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models (User, Job, Resume, ActivityLog)
│   ├── routes/
│   │   ├── auth.py          # Login, register, logout, profile
│   │   ├── dashboard.py     # Analytics dashboard
│   │   ├── jobs.py          # CRUD for job postings
│   │   ├── resumes.py       # Resume upload, view, delete, reanalyze
│   │   ├── analysis.py      # Compare & leaderboard views
│   │   └── reports.py       # PDF & CSV export
│   └── services/
│       ├── resume_parser.py # PDF/DOCX/TXT text extraction
│       └── ats_analyzer.py  # AI scoring engine
├── templates/
│   ├── base.html            # Base layout (sidebar + topbar)
│   ├── auth/                # Login, register, profile
│   ├── dashboard/           # Main dashboard
│   ├── jobs/                # Job list, create/edit, detail
│   ├── resumes/             # Upload, detail
│   └── analysis/            # Compare, leaderboard
├── static/
│   ├── css/style.css        # Premium dark design system
│   └── js/main.js           # Sidebar, animations, interactions
├── uploads/                 # Resume file storage (auto-created)
├── instance/                # SQLite database (auto-created)
├── run.py                   # Application entry point
├── requirements.txt
└── README.md
```

---

## 🧠 How ATS Scoring Works

Each resume is scored across **4 dimensions**, then combined into a weighted ATS Score:

| Dimension | Weight | How It's Calculated |
|---|---|---|
| **Skill Match** | 40% | % of required skills found in resume text |
| **Keyword Density** | 25% | Overlap of job description keywords with resume |
| **Experience** | 20% | Detected years vs. required range |
| **Education** | 15% | Highest detected degree level |

> Score Range: 0–100%. Candidates ≥75% are considered **strong matches**.

### Skill Detection
The analyzer recognizes 80+ technical skills (Python, React, AWS, ML, SQL...) and 15+ soft skills automatically — even without a required skills list.

### Experience Extraction
Two strategies:
1. **Explicit patterns** — "5+ years experience", "3 years of Python"
2. **Date range parsing** — Detects `Jan 2020 – Present`, `2018 – 2022`, etc.

---

## 📊 Dashboard Analytics

- **4 KPI Cards** — Total jobs, resumes, shortlisted, avg ATS score
- **Score Distribution Bar Chart** — How candidates cluster by score range
- **Monthly Upload Trend** — 6-month line chart
- **Status Doughnut** — Pending / Reviewed / Shortlisted breakdown
- **Top Candidates List** — Circular score gauges
- **Recent Activity Feed** — Login, uploads, job creation log

---

## 📤 Bulk Resume Upload

1. Navigate to a Job → **Upload Resumes**
2. Drag & drop or browse — select **multiple files** at once
3. Each file is:
   - Saved securely with a UUID filename
   - Parsed for text content
   - Analyzed and scored automatically
4. All candidates appear ranked in the Job Detail view

**Supported formats:** `.pdf`, `.docx`, `.doc`, `.txt`  
**Max file size:** 16 MB per file

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask 3.1 |
| Database | SQLite (dev), PostgreSQL-ready via SQLAlchemy |
| Auth | Flask-Login + Werkzeug password hashing |
| PDF Parsing | pdfplumber + pdfminer.six (fallback) |
| DOCX Parsing | python-docx |
| ML / NLP | Regex-based + TF-IDF keyword scoring |
| Charts | Chart.js 4.x (CDN) |
| Icons | Font Awesome 6.5 |
| Fonts | Google Fonts (Inter, Space Grotesk) |
| PDF Export | ReportLab |
| CSV Export | Python csv module |

---

## 🔧 Configuration

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (random) | Flask session secret — **change in production** |
| `DATABASE_URL` | SQLite | Database connection string |
| `FLASK_ENV` | `development` | Set to `production` for deployment |
| `MAX_CONTENT_LENGTH` | 16 MB | Maximum upload file size |

---

## 🚧 Roadmap / Future Features

- [ ] Email notifications when candidates are shortlisted
- [ ] Resume duplicate detection
- [ ] Team/multi-user collaboration per job
- [ ] LinkedIn profile import
- [ ] Advanced NLP with spaCy/transformers
- [ ] Kanban board for candidate pipeline
- [ ] Interview scheduling integration

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

<div align="center">Built with ❤️ using Python & Flask | ATS PRO v1.0</div>
