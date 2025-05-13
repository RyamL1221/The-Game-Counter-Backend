import unittest
from unittest.mock import patch, MagicMock
import bcrypt
from flask import Flask
from src.routes.login import login_bp

@patch.dict('env.env', {'JWT_SECRET_KEY': 'testsecret'}, clear=True)
class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(login_bp)
        self.client = self.app.test_client()

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_successful_login(self, mock_get_client):
        # Arrange
        password = "password123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_coll = MagicMock()
        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value = mock_coll
        mock_coll.find_one.return_value = {
            "_id": "abc123",
            "email": "user@example.com",
            "password": hashed
        }
        mock_get_client.return_value = mock_client

        # Act
        resp = self.client.post('/login',
                                json={"email": "user@example.com",
                                      "password": password})

        # Assert
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("token", data)
        self.assertEqual(data["message"], "Login successful")

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_invalid_credentials(self, mock_get_client):
        wrong_hashed = bcrypt.hashpw(b"wrong", bcrypt.gensalt())
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_coll = MagicMock()
        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value = mock_coll
        mock_coll.find_one.return_value = {
            "_id": "abc123",
            "email": "user@example.com",
            "password": wrong_hashed
        }
        mock_get_client.return_value = mock_client

        resp = self.client.post('/login',
                                json={"email": "user@example.com",
                                      "password": "password123"})
        self.assertEqual(resp.status_code, 401)
        self.assertIn("Invalid credentials", resp.get_data(as_text=True))

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_user_not_found(self, mock_get_client):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_coll = MagicMock()
        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value = mock_coll
        mock_coll.find_one.return_value = None
        mock_get_client.return_value = mock_client

        resp = self.client.post('/login',
                                json={"email": "nouser@example.com",
                                      "password": "whatever"})
        self.assertEqual(resp.status_code, 404)
        self.assertIn("User not found", resp.get_data(as_text=True))

    def test_invalid_json(self):
        resp = self.client.post('/login', json={"username": "nope"})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("JSON body does not match schema", resp.get_data(as_text=True))

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_internal_server_error(self, mock_get_client):
        mock_get_client.side_effect = Exception("DB down")
        resp = self.client.post('/login',
                                json={"email": "user@example.com",
                                      "password": "password123"})
        self.assertEqual(resp.status_code, 500)
        self.assertIn("Internal server error", resp.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()