from flask import Blueprint, request, jsonify
from models import Customer
from database import db

customer_bp = Blueprint('customer_routes', __name__)

@customer_bp.route('/', methods=['POST'])
def add_customer():
    data = request.get_json()

    if not data.get('name') or not data.get('email'):
        return jsonify({"error": "Name and email are required"}), 400

    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400

    new_customer = Customer(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone'),
        project_id=data.get('project_id')  # ✅ NEW FIELD
    )
    db.session.add(new_customer)
    db.session.commit()

    return jsonify(new_customer.to_dict()), 201