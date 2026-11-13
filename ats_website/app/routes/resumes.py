import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import Job, Resume, ActivityLog
from app import db
from app.services.resume_parser import parse_resume
from app.services.ats_analyzer import analyze_resume
import json

resumes_bp = Blueprint("resumes", __name__)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@resumes_bp.route("")
@resumes_bp.route("/")
@login_required
def list_resumes():
    status_filter = request.args.get("status", "all")
    job_filter = request.args.get("job_id", "all")
    search = request.args.get("search", "").strip()

    query = (
        Resume.query.join(Job, Resume.job_id == Job.id)
        .filter(Job.user_id == current_user.id)
    )

    if status_filter != "all":
        query = query.filter(Resume.status == status_filter)
    if job_filter != "all" and job_filter.isdigit():
        query = query.filter(Resume.job_id == int(job_filter))
    if search:
        query = query.filter(
            (Resume.candidate_name.ilike(f"%{search}%")) |
            (Resume.candidate_email.ilike(f"%{search}%")) |
            (Resume.extracted_skills.ilike(f"%{search}%"))
        )

    resumes = query.order_by(Resume.ats_score.desc()).all()
    user_jobs = Job.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "resumes/list.html",
        resumes=resumes,
        jobs=user_jobs,
        status_filter=status_filter,
        job_filter=job_filter,
        search=search,
    )


@resumes_bp.route("/upload/<int:job_id>", methods=["GET", "POST"])
@login_required
def upload(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        files = request.files.getlist("resumes")
        if not files or all(f.filename == "" for f in files):
            flash("Please select at least one resume file.", "danger")
            return redirect(request.url)

        upload_folder = os.path.join("uploads", str(job_id))
        os.makedirs(upload_folder, exist_ok=True)
        uploaded, failed = 0, 0

        for file in files:
            if file and allowed_file(file.filename):
                original_name = file.filename
                ext = original_name.rsplit(".", 1)[1].lower()
                unique_name = f"{uuid.uuid4().hex}.{ext}"
                save_path = os.path.join(upload_folder, unique_name)
                try:
                    file.save(save_path)
                    raw_text = parse_resume(save_path, ext)
                    resume = Resume(
                        filename=unique_name,
                        original_filename=original_name,
                        file_path=save_path,
                        file_type=ext,
                        raw_text=raw_text,
                        job_id=job_id,
                        status="pending",
                    )
                    db.session.add(resume)
                    db.session.flush()
                    result = analyze_resume(resume, job)
                    resume.candidate_name = result.get("name", "Unknown")
                    resume.candidate_email = result.get("email", "")
                    resume.candidate_phone = result.get("phone", "")
                    resume.ats_score = result.get("ats_score", 0)
                    resume.skill_score = result.get("skill_score", 0)
                    resume.experience_score = result.get("experience_score", 0)
                    resume.education_score = result.get("education_score", 0)
                    resume.keyword_score = result.get("keyword_score", 0)
                    resume.matched_skills = json.dumps(result.get("matched_skills", []))
                    resume.missing_skills = json.dumps(result.get("missing_skills", []))
                    resume.extracted_skills = json.dumps(result.get("extracted_skills", []))
                    resume.years_experience = result.get("years_experience", 0)
                    resume.education_level = result.get("education_level", "")
                    resume.analyzed_at = datetime.utcnow()
                    db.session.commit()
                    uploaded += 1
                except Exception as e:
                    db.session.rollback()
                    failed += 1
                    print(f"Error processing {original_name}: {e}")
            else:
                failed += 1

        log = ActivityLog(
            user_id=current_user.id, action="Upload Resumes",
            details=f"Uploaded {uploaded} resumes for job: {job.title}",
            ip_address=request.remote_addr,
        )
        db.session.add(log)
        db.session.commit()

        if uploaded:
            flash(f"✅ {uploaded} resume(s) uploaded and analyzed successfully!" +
                  (f" ({failed} skipped)" if failed else ""), "success")
        else:
            flash("No valid files uploaded. Accepted: PDF, DOC, DOCX, TXT", "danger")
        return redirect(url_for("jobs.job_detail", job_id=job_id))

    return render_template("resumes/upload.html", job=job)


@resumes_bp.route("/<int:resume_id>")
@login_required
def resume_detail(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    job = Job.query.filter_by(id=resume.job_id, user_id=current_user.id).first_or_404()
    matched = json.loads(resume.matched_skills or "[]")
    missing = json.loads(resume.missing_skills or "[]")
    extracted = json.loads(resume.extracted_skills or "[]")
    return render_template("resumes/detail.html",
                           resume=resume, job=job,
                           matched_skills=matched,
                           missing_skills=missing,
                           extracted_skills=extracted)


@resumes_bp.route("/<int:resume_id>/status", methods=["POST"])
@login_required
def update_status(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    job = Job.query.filter_by(id=resume.job_id, user_id=current_user.id).first_or_404()
    new_status = request.form.get("status", resume.status)
    valid = ["pending", "reviewed", "shortlisted", "rejected"]
    if new_status in valid:
        resume.status = new_status
        db.session.commit()
        flash(f"Candidate status updated to {new_status.title()}.", "success")
    return redirect(url_for("resumes.resume_detail", resume_id=resume_id))


@resumes_bp.route("/<int:resume_id>/notes", methods=["POST"])
@login_required
def update_notes(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    Job.query.filter_by(id=resume.job_id, user_id=current_user.id).first_or_404()
    resume.notes = request.form.get("notes", "")
    db.session.commit()
    return jsonify({"success": True})


@resumes_bp.route("/<int:resume_id>/delete", methods=["POST"])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    job = Job.query.filter_by(id=resume.job_id, user_id=current_user.id).first_or_404()
    job_id = resume.job_id
    if resume.file_path and os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    db.session.delete(resume)
    db.session.commit()
    flash("Resume deleted.", "info")
    return redirect(url_for("jobs.job_detail", job_id=job_id))


@resumes_bp.route("/<int:resume_id>/download")
@login_required
def download_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    Job.query.filter_by(id=resume.job_id, user_id=current_user.id).first_or_404()
    if resume.file_path and os.path.exists(resume.file_path):
        return send_file(resume.file_path, as_attachment=True,
                         download_name=resume.original_filename)
    flash("File not found.", "danger")
    return redirect(url_for("resumes.resume_detail", resume_id=resume_id))


@resumes_bp.route("/reanalyze/<int:resume_id>", methods=["POST"])
@login_required
def reanalyze(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    job = Job.query.filter_by(id=resume.job_id, user_id=current_user.id).first_or_404()
    try:
        result = analyze_resume(resume, job)
        resume.ats_score = result.get("ats_score", 0)
        resume.skill_score = result.get("skill_score", 0)
        resume.experience_score = result.get("experience_score", 0)
        resume.education_score = result.get("education_score", 0)
        resume.keyword_score = result.get("keyword_score", 0)
        resume.matched_skills = json.dumps(result.get("matched_skills", []))
        resume.missing_skills = json.dumps(result.get("missing_skills", []))
        resume.extracted_skills = json.dumps(result.get("extracted_skills", []))
        resume.years_experience = result.get("years_experience", 0)
        resume.education_level = result.get("education_level", "")
        resume.analyzed_at = datetime.utcnow()
        db.session.commit()
        flash("Resume re-analyzed successfully!", "success")
    except Exception as e:
        flash(f"Analysis error: {str(e)}", "danger")
    return redirect(url_for("resumes.resume_detail", resume_id=resume_id))
