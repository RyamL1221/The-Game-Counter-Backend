from certifi import where
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from env import env

class MongoDB:
    @staticmethod
    def getMongoClient():
        """
        Creates and returns a MongoDB client instance.
        
        Raises:
            Exception: If there is an issue connecting to MongoDB.
        
        Returns:
            MongoClient: An instance of the MongoDB client.
        """
        try:
            client = MongoClient(
                env['MONGO_URI'],
                server_api=ServerApi(version="1", strict=True, deprecation_errors=True),
                tlsCAFile=where()
            )
            # Check if the client can connect to the server
            client.admin.command('ping')
            return client
        except Exception as e:
            raise Exception(f"Failed to connect to MongoDB client: {str(e)}")
