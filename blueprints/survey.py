from flask import Blueprint

survey_bp = Blueprint('survey', __name__, url_prefix='/survey')
# survey logic in experiment_bp
