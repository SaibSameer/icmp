from flask import jsonify, request, Blueprint
from icmplib import ping
import logging

log = logging.getLogger(__name__)
bp = Blueprint('ping', __name__, url_prefix='/ping')

@bp.route('/', methods=['GET', 'POST']) # Allow GET for easy browser testing
def ping():
    print("--- Inside /ping route handler --- ") # Add print
    return jsonify({"message": "pong"}), 200