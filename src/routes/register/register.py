from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ...database.MongoDB import MongoDB
from .schema import DataSchema
import bcrypt


register_bp = Blueprint("register", __name__)

@register_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        register = DataSchema()
        register.load(data)
    except ValidationError as err:
        return jsonify({"error": "JSON body does not match schema", "messages": err.messages}), 400
    
    try:
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('users')

        email = data['email'].lower()

        # Check if the email already exists in the database
        if(collection.find_one({"email": email})):
            return jsonify({"error": "Email already exists"}), 409
        
        password = data['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_answer = bcrypt.hashpw(data['security_answer'].encode('utf-8'), bcrypt.gensalt())

        user_data = {
            "email": email,
            "password": hashed_password,
            "security_question": data['security_question'],
            "security_answer": hashed_answer,
            "count": 0,
        }

        collection.insert_one(user_data)

        return jsonify({"message": "User registered successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500