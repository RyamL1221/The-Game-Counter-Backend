from flask import Flask, request, jsonify
from marshmallow import Schema, fields, ValidationError
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from certifi import where
from flask_cors import CORS
from env import env
from MongoDB import MongoDB

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allows all origins access to all endpoints

class DataSchema(Schema):
    count = fields.Integer(required=True)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/get-count', methods=['GET'])
def getCount():
    # Connect to MongoDB
    try:
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('count')

        # Find the document with the specified ObjectId
        result = collection.find_one({"_id": ObjectId("670c36f98145364754b17703")})

        if result is None:
            return jsonify({"error": "Document not found"}), 404

        result['_id'] = str(result['_id'])

        # Return JSON data
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/plus-one', methods=['PUT'])
def plusOne():
    # Get JSON data from request body
    data = request.get_json()

    # Check if JSON data is provided
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    try:
        # Validate and deserialize incoming JSON
        schema = DataSchema()
        data = schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "JSON body does not match schema", "messages": err.messages}), 400

    # Connect to MongoDB
    try:
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('count')

        # Increment the count field by 1
        collection.update_one(
            {"_id": ObjectId("670c36f98145364754b17703")},
            {"$inc": {"count": 1}}
        )

        # Find the updated document
        result = collection.find_one({"_id": ObjectId("670c36f98145364754b17703")})

        if result is None:
            return jsonify({"error": "Document not found"}), 404

        result['_id'] = str(result['_id'])

        # Return updated JSON data
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/minus-one', methods=['PUT'])
def minusOne():
    # Get JSON data from request body
    data = request.get_json()

    # Check if JSON data is provided
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    try:
        # Validate and deserialize incoming JSON
        schema = DataSchema()
        data = schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "JSON body does not match schema", "messages": err.messages}), 400

    # Connect to MongoDB
    try:
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('count')

        # Decrement the count field by 1
        collection.update_one(
            {"_id": ObjectId("670c36f98145364754b17703")},
            {"$inc": {"count": -1}}
        )

        # Find the updated document
        result = collection.find_one({"_id": ObjectId("670c36f98145364754b17703")})

        if result is None:
            return jsonify({"error": "Document not found"}), 404

        result['_id'] = str(result['_id'])

        # Return updated JSON data
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500



def create_app():
    return app