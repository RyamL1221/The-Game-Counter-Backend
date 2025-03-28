from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from .schema import DataSchema
from ...database.MongoDB import MongoDB
from env import env
import jwt

plus_one_bp = Blueprint("plus_one", __name__)

@plus_one_bp.route('/plus-one', methods=['PUT'])
def plus_one():
    data = request.get_json() # Retrieve JSON data from request

    # Validate JSON data against schema
    try:
        schema = DataSchema()
        schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "JSON body does not match schema", "messages": err.messages}), 400
    
    # Validate JWT token
    try:
        token = data['token']
        decoded_token = jwt.decode(token, env['JWT_SECRET'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

    try:
        # Connect to MongoDB
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('count')

        # Check if email exists in database
        if not collection.find_one({"email": data['email']}):
            return jsonify({"error": "Email not found"}), 404
        
        # Increment count by 1
        collection.update_one(
            {"email": data['email']},
            {"$inc": {"count": 1}}
        )

        # Retrieve updated document
        result = collection.find_one({"email": data['email']})

        # Return the document as JSON
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500