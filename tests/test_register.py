import unittest
from unittest.mock import patch, MagicMock
import bcrypt
from flask import Flask
from src.routes.register import register_bp

class RegisterTestCase(unittest.TestCase):
    def setUp(self):
        # Create a Flask app and register the blueprint
        self.app = Flask(__name__)
        self.app.register_blueprint(register_bp)
        self.client = self.app.test_client()

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_successful_registration(self, mock_get_client):
        # Set up the mock MongoDB client and collection
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        # Configure the mock to mimic getting a database and collection
        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value = mock_collection
        # Simulate that the email does not exist in the collection
        mock_collection.find_one.return_value = None
        mock_get_client.return_value = mock_client

        # Prepare valid payload
        payload = {
            "email": "test@example.com",
            "password": "password123"
        }

        response = self.client.post('/register', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("User registered successfully", response.get_data(as_text=True))

        # Verify that insert_one was called with the correct data
        inserted_data = mock_collection.insert_one.call_args[0][0]
        self.assertEqual(inserted_data["email"], payload["email"])
        # Check that the password is hashed and matches the original
        self.assertTrue(bcrypt.checkpw(payload["password"].encode('utf-8'), inserted_data["password"]))

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_email_already_exists(self, mock_get_client):
        # Set up the mock MongoDB client to simulate an existing email
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value = mock_collection
        # Simulate that the email already exists in the collection
        mock_collection.find_one.return_value = {"email": "test@example.com"}
        mock_get_client.return_value = mock_client

        payload = {
            "email": "test@example.com",
            "password": "password123"
        }

        response = self.client.post('/register', json=payload)
        self.assertEqual(response.status_code, 409)
        self.assertIn("Email already exists", response.get_data(as_text=True))

    def test_invalid_json(self):
        # Provide a payload that doesn't match the expected schema (e.g., missing required fields)
        payload = {"username": "testuser"}
        response = self.client.post('/register', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("JSON body does not match schema", response.get_data(as_text=True))

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_internal_server_error(self, mock_get_client):
        # Simulate an exception during MongoDB connection or operations
        mock_get_client.side_effect = Exception("Database error")

        payload = {
            "email": "test@example.com",
            "password": "password123"
        }
        response = self.client.post('/register', json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Internal server error", response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
