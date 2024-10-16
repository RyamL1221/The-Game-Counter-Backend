from certifi import where
from flask import jsonify
from pymongo import MongoClient
from env import env
from pymongo.server_api import ServerApi

class MongoDB:
    def getMongoClient():
        try:
            client = MongoClient(
                env['MONGO_URI'],
                server_api=ServerApi(version="1", strict=True, deprecation_errors=True),
                tlsCAFile=where()
            )
            return client
        except Exception as e:
            return jsonify({"error": "Failed to connect to MongoDB client", "message": str(e)}), 500