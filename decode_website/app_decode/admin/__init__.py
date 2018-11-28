from flask import Blueprint

bp = Blueprint('admin', __name__)

from app_decode.admin import views
