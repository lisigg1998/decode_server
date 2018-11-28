from flask import Blueprint

bp = Blueprint('api', __name__)

from app_decode.api import tokens
from app_decode.api import email_alert
