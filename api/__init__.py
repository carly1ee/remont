from flask import Blueprint
from .users import users_bp

main_blueprint = Blueprint('main', __name__)

main_blueprint.register_blueprint(users_bp)