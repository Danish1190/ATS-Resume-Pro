from flask import Blueprint, render_template, request, make_response
from flask_login import login_required, current_user
from app.models import Job, Resume
from app import db
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json
import io
import csv

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/job/<int:job_id>/pdf")
@login_required
def export_pdf(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    resumes = Resume.query.filter_by(job_id=job_id).order_by(Resume.ats_score.desc()).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=0.75 * inch, leftMargin=0.75 * inch,
                            topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle("title", fontSize=20, alignment=TA_CENTER,
                                 textColor=colors.HexColor("#6C63FF"), spaceAfter=6,
                                 fontName="Helvetica-Bold")
    sub_style = ParagraphStyle("sub", fontSize=11, alignment=TA_CENTER,
                               textColor=colors.gray, spaceAfter=12)
    story.append(Paragraph("ATS PRO — Candidate Report", title_style))
    story.append(Paragraph(f"Job: {job.title} | Department: {job.department or 'N/A'}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#6C63FF")))
    story.append(Spacer(1, 12))

    # Summary Table
    story.append(Paragraph("Summary", styles["Heading2"]))
    summary_data = [
        ["Total Candidates", "Shortlisted", "Avg ATS Score", "Required Skills"],
        [
            str(len(resumes)),
            str(sum(1 for r in resumes if r.status == "shortlisted")),
            f"{sum(r.ats_score for r in resumes) / len(resumes):.1f}%" if resumes else "0%",
            ", ".join(job.skills_list[:5]) or "N/A",
        ],
    ]
    t = Table(summary_data, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch, 2.5 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6C63FF")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5FF")]),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    # Candidate Table
    story.append(Paragraph("Candidate Rankings", styles["Heading2"]))
    headers = ["#", "Candidate", "Email", "ATS Score", "Skill", "Experience", "Status"]
    data = [headers]
    for i, r in enumerate(resumes, 1):
        data.append([
            str(i),
            r.candidate_name or "Unknown",
            r.candidate_email or "N/A",
            f"{r.ats_score:.1f}%",
            f"{r.skill_score:.1f}%",
            f"{r.experience_score:.1f}%",
            (r.status or "pending").title(),
        ])
    col_widths = [0.3 * inch, 1.4 * inch, 1.6 * inch, 0.8 * inch, 0.7 * inch, 0.9 * inch, 0.8 * inch]
    candidate_table = Table(data, colWidths=col_widths)
    candidate_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2D2B55")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0EFFF")]),
    ]))
    story.append(candidate_table)
    doc.build(story)
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="ats_report_{job_id}.pdf"'
    return response


@reports_bp.route("/job/<int:job_id>/csv")
@login_required
def export_csv(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    resumes = Resume.query.filter_by(job_id=job_id).order_by(Resume.ats_score.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Name", "Email", "Phone", "ATS Score (%)",
        "Skill Score (%)", "Experience Score (%)", "Education Score (%)",
        "Keyword Score (%)", "Years Experience", "Education Level",
        "Status", "Matched Skills", "Missing Skills", "Uploaded At",
    ])
    for i, r in enumerate(resumes, 1):
        matched = ", ".join(json.loads(r.matched_skills or "[]"))
        missing = ", ".join(json.loads(r.missing_skills or "[]"))
        writer.writerow([
            i, r.candidate_name or "Unknown", r.candidate_email or "",
            r.candidate_phone or "", f"{r.ats_score:.1f}", f"{r.skill_score:.1f}",
            f"{r.experience_score:.1f}", f"{r.education_score:.1f}",
            f"{r.keyword_score:.1f}", r.years_experience or 0,
            r.education_level or "", r.status or "pending", matched, missing,
            r.uploaded_at.strftime("%Y-%m-%d %H:%M") if r.uploaded_at else "",
        ])
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = f'attachment; filename="candidates_{job_id}.csv"'
    return response
