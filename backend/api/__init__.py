from flask import Blueprint
from .users import users_bp
from .request import requests_bp
from .request_history import history_bp
from .balance import balance_bp
from .balance_history import balance_history_bp

main_blueprint = Blueprint('main', __name__, url_prefix='/api')

main_blueprint.register_blueprint(users_bp)
main_blueprint.register_blueprint(requests_bp)
main_blueprint.register_blueprint(history_bp)
main_blueprint.register_blueprint(balance_bp)
main_blueprint.register_blueprint(balance_history_bp)
