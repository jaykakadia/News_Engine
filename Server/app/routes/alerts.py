from flask import Blueprint, jsonify

alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')

@alerts_bp.route('/', methods=['GET'])
def get_alerts():
    return jsonify({"message": "Alerts endpoint"})
