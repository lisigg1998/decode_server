from flask import Blueprint

bp = Blueprint('email', __name__)

from app_decode.email import views
