from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, ActivityLog
from app import db
import re

auth_bp = Blueprint("auth", __name__)


def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(pattern, email) is not None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember", False)
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=bool(remember))
            log = ActivityLog(user_id=user.id, action="Login",
                              details="User logged in", ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(next_page or url_for("dashboard.index"))
        flash("Invalid email or password. Please try again.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        company = request.form.get("company", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        errors = []
        if not name or len(name) < 2:
            errors.append("Name must be at least 2 characters.")
        if not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered. Please log in.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("auth/register.html", name=name, email=email, company=company)
        user = User(name=name, email=email, company=company)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log = ActivityLog(user_id=user.id, action="Register",
                          details="New user registered", ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        login_user(user)
        flash(f"Account created successfully! Welcome to ATS PRO, {user.name}!", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    log = ActivityLog(user_id=current_user.id, action="Logout",
                      details="User logged out", ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        company = request.form.get("company", "").strip()
        new_password = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        if name and len(name) >= 2:
            current_user.name = name
        current_user.company = company
        if new_password:
            if len(new_password) < 8:
                flash("New password must be at least 8 characters.", "danger")
                return render_template("auth/profile.html")
            if new_password != confirm:
                flash("Passwords do not match.", "danger")
                return render_template("auth/profile.html")
            current_user.set_password(new_password)
        db.session.commit()
        flash("Profile updated successfully!", "success")
    return render_template("auth/profile.html")
