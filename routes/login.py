from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from database.MongoDB import MongoDB
from models.login import DataSchema
import bcrypt
import jwt
from datetime import datetime, timedelta
from env import env


login_bp = Blueprint("login", __name__)

@login_bp.route('/login', methods=['PUT'])
def login():
    data = request.get_json()
    try:
        login = DataSchema()
        login.load(data)
    except ValidationError as err:
        return jsonify({"error": "JSON body does not match schema", "messages": err.messages}), 400
    
    try:
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('count')

        email = data['email']
        user = collection.find_one({"email": email})
        if(user):
            if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
                return jsonify({"error": "Invalid credentials"}), 401
            token = jwt.encode(
                {
                    "email": email,
                    "id": str(user['_id']),
                    "exp": datetime.utcnow() + timedelta(days=3)  # Set token to expire in 3 days
                },
                env['JWT_SECRET_KEY'],
                algorithm="HS256"
            )
            return jsonify({"token": token, "message": "Login successful" }), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500