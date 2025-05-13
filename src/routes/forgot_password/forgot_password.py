from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from .schema import DataSchema
from ...database.MongoDB import MongoDB
import bcrypt

forgot_password_bp = Blueprint("forgot_password", __name__)

@forgot_password_bp.route('/forgot-password',methods =['POST'])
def forgot_password():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}),400
    
    try:
        data = DataSchema().load(data)
    except ValidationError as err:
        return jsonify({"error": "JSON body does not match schema", "messages":err.messages}), 400
    
    if data['new_password'] != data['confirm_password']:
        return jsonify({"error": "New password and confirm password do not match"}), 400
         
    try:
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('users')

        result = collection.find_one({'email': data['email']},{'_id':0,'password':0})
        if not result:
            return jsonify({"error": "Email not found"}), 404
        
        # Check if the security question and answer match
        if not bcrypt.checkpw(data['security_answer'].encode('utf-8'), result['security_answer']):
            return jsonify({"error": "Security answer is incorrect"}), 401
        
        # Hash the new password
        hashed_password = bcrypt.hashpw(data['new_password'].encode('utf-8'), bcrypt.gensalt())

        # Update the password in the database
        collection.update_one(
            {"email": data['email']},
            {"$set": {"password": hashed_password}}
        )

        # Returns success message
        return jsonify({"message": "Password changed successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500
        
