from flask import Flask

def create_app():
    app = Flask(__name__)

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

    @app.route("/")
    def home():
        return "News Engine API is running"

    return app
