from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from .schema import DataSchema
from ...database.MongoDB import MongoDB

get_security_question_bp = Blueprint("get_security_question", __name__)

@get_security_question_bp.route('/get-security-question',methods =['POST'])
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
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('count')


        result = collection.find_one({'email': data['email']},{'_id':0,'password':0})
        if not result:
            return jsonify({"error": "Email not found"}), 404
        return jsonify({"security_question": result['security_question']}), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500