from flask import Flask
from flask_cors import CORS
from database import db
from routes.customer_routes import customer_bp

from routes.ai_message_route import ai_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


CORS(app, resources={r"/ai/*": {"origins": "http://localhost:3000"}})


db.init_app(app)

# Register Blueprints
app.register_blueprint(customer_bp, url_prefix='/customers')
app.register_blueprint(ai_bp, url_prefix='/ai')
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
