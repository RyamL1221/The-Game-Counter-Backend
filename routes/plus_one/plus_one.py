from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from bson import ObjectId
from schema import DataSchema
from database.MongoDB import MongoDB

plus_one_bp = Blueprint("plus_one", __name__)

@plus_one_bp.route('/plus-one', methods=['PUT'])
def plus_one():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    try:
        schema = DataSchema()
        schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "JSON body does not match schema", "messages": err.messages}), 400

    try:
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('count')

        collection.update_one(
            {"_id": ObjectId("670c36f98145364754b17703")},
            {"$inc": {"count": 1}}
        )
        result = collection.find_one({"_id": ObjectId("670c36f98145364754b17703")})

        if result is None:
            return jsonify({"error": "Document not found"}), 404

        result['_id'] = str(result['_id'])
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
