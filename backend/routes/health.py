from flask import Blueprint, request, jsonify, current_app
import logging

log = logging.getLogger(__name__)

bp = Blueprint('health', __name__, url_prefix='/health')

@bp.route('/', methods=['GET'])
def health_check():
    print("--- Inside /health route handler ---")
    return jsonify({"status": "healthy"}), 200