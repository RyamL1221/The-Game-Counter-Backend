from flask import Blueprint, jsonify
from bson import ObjectId
from ...database.MongoDB import MongoDB

get_count_bp = Blueprint("get_count", __name__)

@get_count_bp.route('/get-count', methods=['GET'])
def get_count():
    try:
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('count')

        result = collection.find_one({"_id": ObjectId("670c36f98145364754b17703")})

        if result is None:
            return jsonify({"error": "Document not found"}), 404

        result['_id'] = str(result['_id'])
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
