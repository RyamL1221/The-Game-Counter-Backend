import unittest
from unittest.mock import patch, MagicMock, ANY
from certifi import where
from pymongo.server_api import ServerApi

from src.database.MongoDB import MongoDB

class MongoDBHelperTestCase(unittest.TestCase):

    @patch.dict('env.env', {'MONGO_URI': 'mongodb://test-uri'}, clear=True)
    @patch('src.database.MongoDB.MongoClient')
    def test_getMongoClient_success(self, mock_mongo_client):
        # Arrange: MongoClient(...) returns a mock client whose ping succeeds
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.admin.command.return_value = {'ok': 1.0}

        # Act
        client = MongoDB.getMongoClient()

        # Assert
        self.assertIs(client, mock_client)
        mock_mongo_client.assert_called_once_with(
            'mongodb://test-uri',
            server_api=ANY,        # we don't need the exact ServerApi instance
            tlsCAFile=where()      # ensure it's using certifi.where()
        )
        mock_client.admin.command.assert_called_once_with('ping')

    @patch.dict('env.env', {'MONGO_URI': 'mongodb://test-uri'}, clear=True)
    @patch('src.database.MongoDB.MongoClient')
    def test_getMongoClient_ping_failure(self, mock_mongo_client):
        # Arrange: ping raises ⇒ getMongoClient should wrap & re-raise
        mock_client = MagicMock()
        mock_client.admin.command.side_effect = Exception("ping failed")
        mock_mongo_client.return_value = mock_client

        # Act & Assert
        with self.assertRaises(Exception) as ctx:
            MongoDB.getMongoClient()
        self.assertIn("Failed to connect to MongoDB client", str(ctx.exception))

    @patch.dict('env.env', {'MONGO_URI': 'mongodb://test-uri'}, clear=True)
    @patch('src.database.MongoDB.MongoClient', side_effect=Exception("constructor failure"))
    def test_getMongoClient_constructor_failure(self, mock_mongo_client):
        # Arrange: MongoClient(...) itself raises
        # Act & Assert
        with self.assertRaises(Exception) as ctx:
            MongoDB.getMongoClient()
        msg = str(ctx.exception)
        self.assertIn("Failed to connect to MongoDB client", msg)
        self.assertIn("constructor failure", msg)


if __name__ == '__main__':
    unittest.main()
