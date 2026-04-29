from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import bcrypt
import uuid
from datetime import datetime
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.models import TenantSchema, UserSchema

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_page():
    # If already logged in, redirect to home
    if 'user_id' in session or 'tenant_id' in session:
        return redirect(url_for('dashboard.index'))
    return render_template("login.html")

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    login_type = request.form.get('login_type', 'user')  # "user" or "agency"
    
    if not email or not password:
        flash("Please fill in all fields.", "error")
        return redirect(url_for('auth.login_page'))
    
    if login_type == 'agency':
        # Agency login
        tenant = Tenant.get_by_email(email)
        if not tenant:
            flash("No agency found with that email.", "error")
            return redirect(url_for('auth.login_page'))
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), tenant.password_hash.encode('utf-8')):
            flash("Invalid password.", "error")
            return redirect(url_for('auth.login_page'))
        
        # Set session
        session['tenant_id'] = tenant.tenant_id
        session['user_name'] = tenant.name
        session['user_email'] = tenant.email
        session['user_role'] = 'agency'
        return redirect(url_for('dashboard.index'))
    
    else:
        # User login
        user = User.get_by_email(email)
        if not user:
            flash("No user found with that email.", "error")
            return redirect(url_for('auth.login_page'))
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            flash("Invalid password.", "error")
            return redirect(url_for('auth.login_page'))
        
        # Set session
        session['user_id'] = user.user_id
        session['tenant_id'] = user.tenant_id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_role'] = 'user'
        return redirect(url_for('dashboard.index'))

@auth_bp.route('/register', methods=['GET'])
def register_page():
    if 'user_id' in session or 'tenant_id' in session:
        return redirect(url_for('dashboard.index'))
    
    # Fetch all tenants for user registration dropdown
    tenants = Tenant.list_all()
    return render_template("register.html", tenants=tenants)

@auth_bp.route('/register', methods=['POST'])
def register():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    register_type = request.form.get('register_type', 'agency')
    
    if not name or not email or not password:
        flash("Please fill in all fields.", "error")
        return redirect(url_for('auth.register_page'))
    
    if len(password) < 6:
        flash("Password must be at least 6 characters.", "error")
        return redirect(url_for('auth.register_page'))
    
    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    if register_type == 'agency':
        # Check if email already exists
        existing = Tenant.get_by_email(email)
        if existing:
            flash("An agency with this email already exists.", "error")
            return redirect(url_for('auth.register_page'))
        
        tenant_id = str(uuid.uuid4())
        tenant_data = TenantSchema(
            tenant_id=tenant_id,
            name=name,
            email=email,
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )
        
        if Tenant.create(tenant_data):
            # Auto-login after registration
            session['tenant_id'] = tenant_id
            session['user_name'] = name
            session['user_email'] = email
            session['user_role'] = 'agency'
            flash(f"Agency '{name}' created successfully!", "success")
            return redirect(url_for('dashboard.index'))
        else:
            flash("Failed to create agency. Please try again.", "error")
            return redirect(url_for('auth.register_page'))
    
    else:
        # User registration
        tenant_id = request.form.get('tenant_id', '').strip()
        if not tenant_id:
            flash("Please select an agency.", "error")
            return redirect(url_for('auth.register_page'))
        
        # Check if email already exists
        existing = User.get_by_email(email)
        if existing:
            flash("A user with this email already exists.", "error")
            return redirect(url_for('auth.register_page'))
        
        user_id = str(uuid.uuid4())
        user_data = UserSchema(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            name=name,
            password_hash=password_hash,
            role="user",
            created_at=datetime.utcnow()
        )
        
        if User.create(user_data):
            # Auto-login after registration
            session['user_id'] = user_id
            session['tenant_id'] = tenant_id
            session['user_name'] = name
            session['user_email'] = email
            session['user_role'] = 'user'
            flash(f"Welcome, {name}!", "success")
            return redirect(url_for('dashboard.index'))
        else:
            flash("Failed to create user. Please try again.", "error")
            return redirect(url_for('auth.register_page'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.login_page'))
