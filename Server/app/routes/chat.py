from flask import Blueprint, jsonify

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/', methods=['POST'])
def chat():
    return jsonify({"message": "Chat endpoint"})
