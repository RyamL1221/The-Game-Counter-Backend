from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from bson import ObjectId
from .schema import DataSchema
from ...database.MongoDB import MongoDB
import jwt
from env import env

minus_one_bp = Blueprint("minus_one", __name__)

@minus_one_bp.route('/minus-one', methods=['POST'])
def minus_one():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    try:
        schema = DataSchema()
        schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "JSON body does not match schema", "messages": err.messages}), 400

    try:
        token = data['token']
        decodedToken = jwt.decode(token, env['JWT_SECRET'], algorithms=["H256"])
        
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500 
    
    try:  
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('count')
        
        collection.update_one(
            {"email": data['email']},
            {"$inc": {"count": -1}}
        )
        result = collection.find_one({"email": data['email']})
        
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
