from flask import Blueprint, jsonify

news_bp = Blueprint('news', __name__, url_prefix='/api/news')

@news_bp.route('/', methods=['GET'])
def get_news():
    return jsonify({"message": "News endpoint"})
