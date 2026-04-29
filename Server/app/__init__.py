from flask import Flask, session, redirect, url_for, request, g
import os

def create_app():
    app = Flask(__name__)
    
    # Secret key for session management
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'news-engine-secret-key-change-in-production')

    # Import Blueprints
    from app.routes.alerts import alerts_bp
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.news import news_bp

    # Register Blueprints
    app.register_blueprint(alerts_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(news_bp)

    # Route protection: redirect to login if not authenticated
    @app.before_request
    def require_login():
        # Allow static files, login, and register without authentication
        allowed_endpoints = ['auth.login_page', 'auth.login', 'auth.register_page', 'auth.register', 'static']
        if request.endpoint in allowed_endpoints:
            return None
        
        # Check if user is logged in
        if 'user_name' not in session:
            return redirect(url_for('auth.login_page'))
    
    # Make session data available in all templates
    @app.context_processor
    def inject_user():
        return {
            'current_user_name': session.get('user_name', 'Guest'),
            'current_user_email': session.get('user_email', ''),
            'current_user_role': session.get('user_role', ''),
            'is_logged_in': 'user_name' in session
        }

    # Start the background scheduler
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        from app.ingestion.scheduler import start_scheduler
        start_scheduler()

    return app

