from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from bson import ObjectId
from .schema import DataSchema
from ...database.MongoDB import MongoDB
import jwt
from env import env

read_bp = Blueprint("read", __name__)

@read_bp.route('/read',methods =['POST'])
def read():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}),400
    
    try:
        schema = DataSchema()
        schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "JSON body does not match schema", "messages":err.messages}), 400
    
    
    try:
        token = data['auth_token']
        decoded_token = jwt.decode(token, env['JWT_SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
            return jsonify({"error":"Token has expired"}), 401
    except jwt.InvalidTokenError:
            return jsonify({"error":"Invalid token"}), 401
    except Exception as e:
            return jsonify({"error":"Internal server error","message":str(e)}), 500
         
    try:
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('count')


        result = collection.find_one({'email': data['email']},{'_id':0,'password':0})
        if not result:
            return jsonify({"error": "Email not found"}), 404
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
        
