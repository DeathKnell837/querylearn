import os
import datetime
from flask import Flask, render_template, session
from config import Config


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, 'static'),
        template_folder=os.path.join(base_dir, 'templates'),
        static_url_path='/static'
    )
    app.config.from_object(Config)

    # --- Initialize databases if they don't exist ---
    from database.init_research_db import init_research_db
    from database.init_experiment_db import init_experiment_db

    if not os.path.exists(app.config['RESEARCH_DB']):
        init_research_db(app.config['RESEARCH_DB'])
    if not os.path.exists(app.config['EXPERIMENT_A_DB']):
        init_experiment_db(app.config['EXPERIMENT_A_DB'], 'A')
    if not os.path.exists(app.config['EXPERIMENT_B_DB']):
        init_experiment_db(app.config['EXPERIMENT_B_DB'], 'B')

    # --- Register blueprints ---
    from blueprints.auth import auth_bp
    from blueprints.experiment import experiment_bp
    from blueprints.tasks import tasks_bp
    from blueprints.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(experiment_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(dashboard_bp)

    # Try to register survey blueprint if it has routes
    try:
        from blueprints.survey import survey_bp
        app.register_blueprint(survey_bp)
    except (ImportError, AttributeError):
        pass

    # --- Context processor ---
    @app.context_processor
    def inject_context():
        return {
            'current_year': datetime.datetime.now().year,
            'study_id': session.get('study_id')
        }

    # --- Error handlers ---
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # --- Landing page ---
    @app.route('/')
    def index():
        return render_template('index.html')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
