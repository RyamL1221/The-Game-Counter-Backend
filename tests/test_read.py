import unittest
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta, timezone
from flask import Flask
from src.routes.read import read_bp

@patch.dict('env.env', {'JWT_SECRET_KEY': 'testsecret'}, clear=True)
class ReadTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(read_bp)
        self.client = self.app.test_client()
        self.email = "user@example.com"
        self.valid_token = jwt.encode(
            {"email": self.email, "exp": datetime.now(timezone.utc) + timedelta(days=1)},
            'testsecret',
            algorithm="HS256"
        )

    def test_no_json_data(self):
        # No JSON leads to a 415 Unsupported Media Type
        resp = self.client.post('/read')
        self.assertEqual(resp.status_code, 415)
        self.assertIn("Unsupported Media Type", resp.get_data(as_text=True))

    def test_successful_read(self):
        with patch('jwt.decode', return_value={"email": self.email}) as mock_decode, \
             patch('src.database.MongoDB.MongoDB.getMongoClient') as mock_get_client:
            # Mock DB client and collection
            mock_client = MagicMock()
            mock_db = MagicMock()
            mock_coll = MagicMock()
            mock_client.get_database.return_value = mock_db
            mock_db.get_collection.return_value = mock_coll
            expected = {"email": self.email, "count": 5}
            mock_coll.find_one.return_value = expected
            mock_get_client.return_value = mock_client

            resp = self.client.post(
                '/read',
                json={"email": self.email, "auth_token": self.valid_token}
            )
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.get_json(), expected)

    def test_invalid_json(self):
        resp = self.client.post('/read', json={"email": self.email})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("JSON body does not match schema", resp.get_data(as_text=True))

    def test_token_expired(self):
        with patch('jwt.decode', side_effect=jwt.ExpiredSignatureError):
            resp = self.client.post(
                '/read',
                json={"email": self.email, "auth_token": "token"}
            )
            self.assertEqual(resp.status_code, 401)
            self.assertIn("Token has expired", resp.get_data(as_text=True))

    def test_invalid_token(self):
        with patch('jwt.decode', side_effect=jwt.InvalidTokenError):
            resp = self.client.post(
                '/read',
                json={"email": self.email, "auth_token": "token"}
            )
            self.assertEqual(resp.status_code, 401)
            self.assertIn("Invalid token", resp.get_data(as_text=True))

    def test_decode_internal_error(self):
        with patch('jwt.decode', side_effect=Exception("Decode error")):
            resp = self.client.post(
                '/read',
                json={"email": self.email, "auth_token": "token"}
            )
            self.assertEqual(resp.status_code, 500)
            self.assertIn("Internal server error", resp.get_data(as_text=True))
            self.assertIn("Decode error", resp.get_data(as_text=True))

    def test_email_not_found(self):
        with patch('jwt.decode', return_value={"email": self.email}), \
             patch('src.database.MongoDB.MongoDB.getMongoClient') as mock_get_client:
            mock_client = MagicMock()
            mock_db = MagicMock()
            mock_coll = MagicMock()
            mock_client.get_database.return_value = mock_db
            mock_db.get_collection.return_value = mock_coll
            mock_coll.find_one.return_value = None
            mock_get_client.return_value = mock_client

            resp = self.client.post(
                '/read',
                json={"email": self.email, "auth_token": self.valid_token}
            )
            self.assertEqual(resp.status_code, 404)
            self.assertIn("Email not found", resp.get_data(as_text=True))

    def test_db_internal_error(self):
        with patch('jwt.decode', return_value={"email": self.email}), \
             patch('src.database.MongoDB.MongoDB.getMongoClient', side_effect=Exception("DB error")):
            resp = self.client.post(
                '/read',
                json={"email": self.email, "auth_token": self.valid_token}
            )
            self.assertEqual(resp.status_code, 500)
            self.assertIn("Internal server error", resp.get_data(as_text=True))
            self.assertIn("DB error", resp.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
