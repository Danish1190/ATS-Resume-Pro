"""
ATS PRO — Database Seed Script
Populates demo jobs, candidates, and activity logs for realistic glassmorphism dashboard.
"""
from app import create_app, db
from app.models import User, Job, Resume, ActivityLog
from datetime import datetime, timedelta
import json

def seed():
    app = create_app()
    with app.app_context():
        # Ensure database tables exist
        db.create_all()

        # 1. Admin & Demo User
        admin = User.query.filter_by(email="admin@atspro.com").first()
        if not admin:
            admin = User(name="Admin User", email="admin@atspro.com", company="TechCorp Global")
            admin.set_password("Admin@1234")
            db.session.add(admin)
            db.session.commit()
            print("Created admin user: admin@atspro.com")
        else:
            admin.set_password("Admin@1234")
            db.session.commit()
            print("Verified admin user: admin@atspro.com")

        recruiter = User.query.filter_by(email="recruiter@atspro.com").first()
        if not recruiter:
            recruiter = User(name="Sarah Jenkins", email="recruiter@atspro.com", company="TechCorp Global")
            recruiter.set_password("Recruiter@1234")
            db.session.add(recruiter)
            db.session.commit()
            print("Created recruiter user: recruiter@atspro.com")

        # Check existing jobs for admin
        existing_jobs = Job.query.filter_by(user_id=admin.id).count()
        if existing_jobs > 0:
            print(f"Admin already has {existing_jobs} jobs.")
            return

        # 2. Sample Jobs
        job1 = Job(
            title="Senior Full-Stack Python Engineer",
            department="Engineering",
            location="San Francisco, CA (Remote)",
            job_type="Full-time",
            description="We are seeking an experienced Senior Full-Stack Python Engineer to design and scale enterprise web applications, REST APIs, and microservices.",
            requirements="5+ years of experience in Python (Flask or Django) and modern frontend (React/Vue). Strong database design with PostgreSQL/MySQL, Docker containerization, and AWS deployment.",
            required_skills="python, flask, react, postgresql, docker, aws, rest, git",
            experience_min=5,
            experience_max=10,
            salary_min=130000,
            salary_max=175000,
            deadline=datetime.utcnow() + timedelta(days=30),
            status="active",
            user_id=admin.id
        )

        job2 = Job(
            title="AI & NLP Machine Learning Specialist",
            department="Data Science & AI",
            location="New York, NY (Hybrid)",
            job_type="Full-time",
            description="Lead the design and fine-tuning of natural language processing models, generative AI pipelines, and ML inference microservices.",
            requirements="3+ years of experience in Python, PyTorch or TensorFlow, NLP, text classification, transformers, and vector databases.",
            required_skills="python, nlp, pytorch, tensorflow, scikit-learn, docker, sql, machine learning",
            experience_min=3,
            experience_max=8,
            salary_min=140000,
            salary_max=190000,
            deadline=datetime.utcnow() + timedelta(days=45),
            status="active",
            user_id=admin.id
        )

        job3 = Job(
            title="DevOps & Cloud Platform Engineer",
            department="Infrastructure",
            location="Austin, TX (Remote)",
            job_type="Full-time",
            description="Manage and scale our multi-region Kubernetes clusters, CI/CD automated pipelines, and cloud security posture.",
            requirements="Strong expertise in AWS/GCP, Kubernetes, Docker, Terraform, CI/CD GitHub Actions, Linux administration, and Python/Bash scripting.",
            required_skills="aws, kubernetes, docker, terraform, ci/cd, linux, python, git",
            experience_min=4,
            experience_max=9,
            salary_min=125000,
            salary_max=165000,
            deadline=datetime.utcnow() + timedelta(days=20),
            status="active",
            user_id=admin.id
        )

        db.session.add_all([job1, job2, job3])
        db.session.commit()
        print("Created 3 jobs.")

        # 3. Sample Candidates / Resumes for Job 1
        candidates_job1 = [
            {
                "name": "Alexander Vance",
                "email": "alex.vance@example.com",
                "phone": "+1 (555) 234-8901",
                "filename": "alexander_vance_resume.pdf",
                "ats_score": 94.5,
                "skill_score": 96.0,
                "experience_score": 92.0,
                "education_score": 90.0,
                "keyword_score": 95.0,
                "years_exp": 7.5,
                "edu": "Master of Computer Science",
                "matched": ["python", "flask", "react", "postgresql", "docker", "aws", "rest", "git"],
                "missing": [],
                "extracted": ["python", "flask", "django", "react", "postgresql", "docker", "aws", "rest", "git", "redis", "linux"],
                "status": "shortlisted",
                "notes": "Outstanding candidate with 7+ years building enterprise Flask and React architectures. Top choice for lead role.",
                "days_ago": 2
            },
            {
                "name": "Elena Rostova",
                "email": "elena.rostova@example.com",
                "phone": "+1 (555) 456-7812",
                "filename": "elena_rostova_resume.pdf",
                "ats_score": 87.2,
                "skill_score": 88.0,
                "experience_score": 85.0,
                "education_score": 90.0,
                "keyword_score": 86.0,
                "years_exp": 6.0,
                "edu": "Bachelor of Software Engineering",
                "matched": ["python", "flask", "react", "docker", "postgresql", "git", "rest"],
                "missing": ["aws"],
                "extracted": ["python", "flask", "react", "javascript", "docker", "postgresql", "git", "rest", "mongodb"],
                "status": "shortlisted",
                "notes": "Solid full stack developer. Great portfolio and code samples.",
                "days_ago": 4
            },
            {
                "name": "Marcus Chen",
                "email": "marcus.chen@example.com",
                "phone": "+1 (555) 789-0123",
                "filename": "marcus_chen_resume.docx",
                "ats_score": 78.4,
                "skill_score": 75.0,
                "experience_score": 80.0,
                "education_score": 85.0,
                "keyword_score": 78.0,
                "years_exp": 5.0,
                "edu": "Bachelor of Computer Science",
                "matched": ["python", "flask", "docker", "postgresql", "git"],
                "missing": ["react", "aws", "rest"],
                "extracted": ["python", "flask", "docker", "postgresql", "git", "django", "sql"],
                "status": "reviewed",
                "notes": "Strong backend Python skills, limited React frontend experience.",
                "days_ago": 7
            },
            {
                "name": "Sophia Martinez",
                "email": "sophia.m@example.com",
                "phone": "+1 (555) 321-6549",
                "filename": "sophia_martinez_resume.pdf",
                "ats_score": 64.0,
                "skill_score": 62.0,
                "experience_score": 65.0,
                "education_score": 70.0,
                "keyword_score": 60.0,
                "years_exp": 3.0,
                "edu": "Associate Degree in IT",
                "matched": ["python", "react", "git"],
                "missing": ["flask", "postgresql", "docker", "aws", "rest"],
                "extracted": ["python", "react", "javascript", "git", "html", "css"],
                "status": "pending",
                "notes": "Promising junior developer, might need mentorship.",
                "days_ago": 10
            },
            {
                "name": "David Kim",
                "email": "david.kim@example.com",
                "phone": "+1 (555) 987-1234",
                "filename": "david_kim_cv.pdf",
                "ats_score": 42.5,
                "skill_score": 38.0,
                "experience_score": 45.0,
                "education_score": 50.0,
                "keyword_score": 40.0,
                "years_exp": 1.5,
                "edu": "High School Diploma",
                "matched": ["python", "git"],
                "missing": ["flask", "react", "postgresql", "docker", "aws", "rest"],
                "extracted": ["python", "git", "c++"],
                "status": "rejected",
                "notes": "Insufficient experience for senior requirements.",
                "days_ago": 15
            }
        ]

        # Candidates for Job 2
        candidates_job2 = [
            {
                "name": "Dr. Priya Sharma",
                "email": "priya.sharma@example.com",
                "phone": "+1 (555) 888-9999",
                "filename": "priya_sharma_nlp.pdf",
                "ats_score": 96.0,
                "skill_score": 98.0,
                "experience_score": 95.0,
                "education_score": 100.0,
                "keyword_score": 94.0,
                "years_exp": 6.5,
                "edu": "Ph.D. in Artificial Intelligence",
                "matched": ["python", "nlp", "pytorch", "tensorflow", "scikit-learn", "docker", "sql", "machine learning"],
                "missing": [],
                "extracted": ["python", "nlp", "pytorch", "tensorflow", "scikit-learn", "docker", "sql", "machine learning", "transformers", "pandas", "numpy"],
                "status": "shortlisted",
                "notes": "Exceptional NLP research and production deployment background. Highly recommended.",
                "days_ago": 3
            },
            {
                "name": "Liam O'Connor",
                "email": "liam.oconnor@example.com",
                "phone": "+1 (555) 444-2233",
                "filename": "liam_oconnor_ai.pdf",
                "ats_score": 83.5,
                "skill_score": 85.0,
                "experience_score": 80.0,
                "education_score": 88.0,
                "keyword_score": 82.0,
                "years_exp": 4.0,
                "edu": "M.Sc. in Data Science",
                "matched": ["python", "pytorch", "scikit-learn", "sql", "machine learning", "docker"],
                "missing": ["nlp", "tensorflow"],
                "extracted": ["python", "pytorch", "scikit-learn", "sql", "machine learning", "docker", "pandas", "numpy"],
                "status": "reviewed",
                "notes": "Good ML foundations, some NLP experience mentioned in projects.",
                "days_ago": 8
            }
        ]

        # Candidates for Job 3
        candidates_job3 = [
            {
                "name": "Jordan Taylor",
                "email": "jordan.taylor@example.com",
                "phone": "+1 (555) 667-8899",
                "filename": "jordan_taylor_devops.pdf",
                "ats_score": 91.8,
                "skill_score": 92.0,
                "experience_score": 90.0,
                "education_score": 90.0,
                "keyword_score": 93.0,
                "years_exp": 7.0,
                "edu": "B.Sc. in Computer Science",
                "matched": ["aws", "kubernetes", "docker", "terraform", "ci/cd", "linux", "python", "git"],
                "missing": [],
                "extracted": ["aws", "kubernetes", "docker", "terraform", "ci/cd", "linux", "python", "git", "ansible", "bash"],
                "status": "shortlisted",
                "notes": "Senior DevOps engineer with multi-cloud Kubernetes experience. Strong candidate.",
                "days_ago": 5
            }
        ]

        for c in candidates_job1:
            r = Resume(
                candidate_name=c["name"],
                candidate_email=c["email"],
                candidate_phone=c["phone"],
                filename=c["filename"],
                original_filename=c["filename"],
                file_type="pdf",
                job_id=job1.id,
                ats_score=c["ats_score"],
                skill_score=c["skill_score"],
                experience_score=c["experience_score"],
                education_score=c["education_score"],
                keyword_score=c["keyword_score"],
                years_experience=c["years_exp"],
                education_level=c["edu"],
                matched_skills=json.dumps(c["matched"]),
                missing_skills=json.dumps(c["missing"]),
                extracted_skills=json.dumps(c["extracted"]),
                status=c["status"],
                notes=c["notes"],
                uploaded_at=datetime.utcnow() - timedelta(days=c["days_ago"]),
                analyzed_at=datetime.utcnow() - timedelta(days=c["days_ago"])
            )
            db.session.add(r)

        for c in candidates_job2:
            r = Resume(
                candidate_name=c["name"],
                candidate_email=c["email"],
                candidate_phone=c["phone"],
                filename=c["filename"],
                original_filename=c["filename"],
                file_type="pdf",
                job_id=job2.id,
                ats_score=c["ats_score"],
                skill_score=c["skill_score"],
                experience_score=c["experience_score"],
                education_score=c["education_score"],
                keyword_score=c["keyword_score"],
                years_experience=c["years_exp"],
                education_level=c["edu"],
                matched_skills=json.dumps(c["matched"]),
                missing_skills=json.dumps(c["missing"]),
                extracted_skills=json.dumps(c["extracted"]),
                status=c["status"],
                notes=c["notes"],
                uploaded_at=datetime.utcnow() - timedelta(days=c["days_ago"]),
                analyzed_at=datetime.utcnow() - timedelta(days=c["days_ago"])
            )
            db.session.add(r)

        for c in candidates_job3:
            r = Resume(
                candidate_name=c["name"],
                candidate_email=c["email"],
                candidate_phone=c["phone"],
                filename=c["filename"],
                original_filename=c["filename"],
                file_type="pdf",
                job_id=job3.id,
                ats_score=c["ats_score"],
                skill_score=c["skill_score"],
                experience_score=c["experience_score"],
                education_score=c["education_score"],
                keyword_score=c["keyword_score"],
                years_experience=c["years_exp"],
                education_level=c["edu"],
                matched_skills=json.dumps(c["matched"]),
                missing_skills=json.dumps(c["missing"]),
                extracted_skills=json.dumps(c["extracted"]),
                status=c["status"],
                notes=c["notes"],
                uploaded_at=datetime.utcnow() - timedelta(days=c["days_ago"]),
                analyzed_at=datetime.utcnow() - timedelta(days=c["days_ago"])
            )
            db.session.add(r)

        # 4. Activity Logs
        activities = [
            ("Upload Resumes", "Uploaded 5 resumes for Senior Full-Stack Python Engineer", 2),
            ("Candidate Shortlisted", "Shortlisted Alexander Vance (94.5% ATS score)", 2),
            ("Candidate Shortlisted", "Shortlisted Elena Rostova (87.2% ATS score)", 3),
            ("Create Job", "Created job: AI & NLP Machine Learning Specialist", 3),
            ("Upload Resumes", "Uploaded 2 resumes for AI & NLP Specialist", 3),
            ("Candidate Shortlisted", "Shortlisted Dr. Priya Sharma (96.0% ATS score)", 3),
            ("Create Job", "Created job: DevOps & Cloud Platform Engineer", 5),
            ("Candidate Shortlisted", "Shortlisted Jordan Taylor (91.8% ATS score)", 5),
        ]
        for action, details, days in activities:
            log = ActivityLog(
                user_id=admin.id,
                action=action,
                details=details,
                timestamp=datetime.utcnow() - timedelta(days=days),
                ip_address="127.0.0.1"
            )
            db.session.add(log)

        db.session.commit()
        print("Database seeded successfully with demo jobs, candidates, and activities!")

if __name__ == "__main__":
    seed()
