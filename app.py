from flask import Flask
from flask_cors import CORS
from routes import default_bp, get_count_bp, plus_one_bp, minus_one_bp, register_bp, login_bp

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

    # Register blueprints
    app.register_blueprint(default_bp)
    app.register_blueprint(get_count_bp)
    app.register_blueprint(plus_one_bp)
    app.register_blueprint(minus_one_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(login_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
