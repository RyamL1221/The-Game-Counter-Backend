from flask import Flask, request, jsonify
from marshmallow import Schema, fields, ValidationError
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from certifi import where
from env import env

app = Flask(__name__) 

class DataSchema(Schema):
    count = fields.Integer(required=True)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/get-count', methods=['GET'])
def getCount():
    # Connect to MongoDB
    try:
        client = getMongoClient()
        db = client.get_database('dev')
        collection = db.get_collection('count')

        # Find the document with the specified ObjectId
        result = collection.find_one({"_id": ObjectId("670c36f98145364754b17703")})

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
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": "JSON body does not match schema)"}), 400
    
    # Connect to MongoDB
    try:
        client = getMongoClient() 
        db = client.get_database('dev')
        collection = db.get_collection('count')

        # Insert the updated data into the MongoDB collection
        collection.update_one(
            {"_id": ObjectId("670c36f98145364754b17703")},
            {"$inc": {"count": 1}}  # Increment the count field by 1
        )

        result = collection.find_one({"_id": ObjectId("670c36f98145364754b17703")})
            
        result['_id'] = str(result['_id'])

        # Return updated JSON data
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

def getMongoClient():
    try:
        client = MongoClient(
            env['MONGO_URI'],
            server_api=ServerApi(version="1", strict=True, deprecation_errors=True),
            tlsCAFile=where()
        )
        return client
    except Exception as e:
        return jsonify({"error": "Failed to connect to MongoDB", "message": str(e)}), 500

def create_app():
   return app
