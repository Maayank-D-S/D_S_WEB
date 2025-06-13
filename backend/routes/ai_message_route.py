from flask import Blueprint, request, jsonify
from models import AIMessage
from database import db
from OPENAI_CHATBOT.chatbot import fetch_response  
# from ai_agent.agent import get_ai_response  # Your custom logic

ai_bp = Blueprint('ai_routes', __name__)

@ai_bp.route('/new_query', methods=['POST'])
def new_query():
    data = request.get_json()

    user_id = data.get('user_id')
    session_id = data.get('session_id')
    user_message = data.get('message')

    if not user_id or not session_id or not user_message:
        return jsonify({"error": "user_id, session_id, and message are required"}), 400

    # Save user message
    user_msg = AIMessage(user_id=user_id, session_id=session_id, role='user', message=user_message)
    db.session.add(user_msg)

    # Get AI response
    ai_response = fetch_response(user_message)  # your LLM call

    # Save AI response
    ai_msg = AIMessage(user_id=user_id, session_id=session_id, role='ai', message=ai_response["text"])
    db.session.add(ai_msg)
    db.session.commit()

    return jsonify({
        "user": user_msg.to_dict(),
        "ai": ai_msg.to_dict()
    }), 200

@ai_bp.route('/get_messages/<int:user_id>/<string:session_id>', methods=['GET'])
def get_messages(user_id, session_id):
    messages = AIMessage.query.filter_by(user_id=user_id, session_id=session_id).order_by(AIMessage.timestamp).all()
    return jsonify([m.to_dict() for m in messages]), 200
