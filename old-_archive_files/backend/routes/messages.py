# routes/messages.py
from flask import Blueprint, redirect, url_for

bp = Blueprint('messages', __name__)

@bp.route('/process', methods=['POST'])
def redirect_to_message():
    return redirect(url_for('message_handling.handle_message'), code=307)