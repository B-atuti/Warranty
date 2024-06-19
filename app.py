from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User  # Ensure db and User are imported from models.py
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
CORS(app)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    firstName = data.get('firstName')
    secondName = data.get('secondName')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 409

    new_user = User(firstName=firstName, secondName=secondName, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [user.to_dict() for user in users]
    return jsonify({'users': user_list}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.password == password:
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': new_access_token}), 200

@app.route('/reset_password/request', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Generate a 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    user.otp = otp
    db.session.commit()

    return jsonify({'message': 'OTP sent to email', 'otp': otp}), 200

@app.route('/reset_password/verify', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    user = User.query.filter_by(email=email, otp=otp).first()
    if not user:
        return jsonify({'message': 'Invalid OTP or email'}), 400

    return jsonify({'message': 'OTP verified'}), 200

@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')

    user = User.query.filter_by(email=email, otp=otp).first()
    if not user:
        return jsonify({'message': 'Invalid OTP or email'}), 400

    user.password = new_password
    user.otp = None  # Clear the OTP after successful reset
    db.session.commit()

    return jsonify({'message': 'Password reset successful'}), 200

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({'logged_in_as': user.to_dict()}), 200

if __name__ == '__main__':
    app.run(debug=True)
