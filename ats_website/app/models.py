from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="recruiter")  # admin, recruiter
    company = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    jobs = db.relationship("Job", backref="creator", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100))
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(50), default="Full-time")  # Full-time, Part-time, Contract, Remote
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    required_skills = db.Column(db.Text)       # comma-separated skills
    experience_min = db.Column(db.Integer, default=0)
    experience_max = db.Column(db.Integer, default=10)
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    status = db.Column(db.String(50), default="active")  # active, closed, draft
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    resumes = db.relationship("Resume", backref="job", lazy=True, cascade="all, delete-orphan")

    @property
    def skills_list(self):
        if self.required_skills:
            return [s.strip() for s in self.required_skills.split(",") if s.strip()]
        return []

    @property
    def candidate_count(self):
        return len(self.resumes)

    @property
    def shortlisted_count(self):
        return sum(1 for r in self.resumes if r.status == "shortlisted")

    def __repr__(self):
        return f"<Job {self.title}>"


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    candidate_name = db.Column(db.String(200))
    candidate_email = db.Column(db.String(200))
    candidate_phone = db.Column(db.String(50))
    filename = db.Column(db.String(300), nullable=False)
    original_filename = db.Column(db.String(300))
    file_path = db.Column(db.String(500))
    file_type = db.Column(db.String(10))
    raw_text = db.Column(db.Text)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    status = db.Column(db.String(50), default="pending")  # pending, reviewed, shortlisted, rejected
    ats_score = db.Column(db.Float, default=0.0)
    skill_score = db.Column(db.Float, default=0.0)
    experience_score = db.Column(db.Float, default=0.0)
    education_score = db.Column(db.Float, default=0.0)
    keyword_score = db.Column(db.Float, default=0.0)
    matched_skills = db.Column(db.Text)          # JSON list
    missing_skills = db.Column(db.Text)         # JSON list
    extracted_skills = db.Column(db.Text)       # JSON list
    years_experience = db.Column(db.Float, default=0.0)
    education_level = db.Column(db.String(100))
    notes = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyzed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Resume {self.candidate_name} - {self.ats_score}>"


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(200))
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))

    user = db.relationship("User", backref="activities")

    def __repr__(self):
        return f"<ActivityLog {self.action}>"
