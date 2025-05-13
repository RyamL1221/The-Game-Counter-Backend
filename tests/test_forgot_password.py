import unittest
from unittest.mock import patch, MagicMock
import bcrypt
from flask import Flask
from marshmallow import ValidationError
from src.routes.forgot_password import forgot_password_bp

import src.routes.forgot_password.schema as schema_module

class ForgotPasswordTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(forgot_password_bp)
        self.client = self.app.test_client()
        self.email = "user@example.com"
        self.new_password = "newpass123"
        self.confirm_password = "newpass123"
        self.security_answer = "blue"
        # Simulate hashed answer stored in DB
        self.hashed_answer = bcrypt.hashpw(self.security_answer.encode('utf-8'), bcrypt.gensalt())

    @patch.object(schema_module.DataSchema, 'load', side_effect=ValidationError({"email": ["Missing"]}))
    def test_schema_validation_error(self, mock_load):
        resp = self.client.post(
            '/read',
            json={"email": self.email}
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data.get("error"), "JSON body does not match schema")

    def test_password_mismatch(self):
        # Load passes, but new != confirm
        with patch.object(schema_module.DataSchema, 'load', return_value={
            "email": self.email,
            "security_answer": self.security_answer,
            "new_password": "one",
            "confirm_password": "two"
        }):
            resp = self.client.post(
                '/read',
                json={
                    "email": self.email,
                    "security_answer": self.security_answer,
                    "new_password": "one",
                    "confirm_password": "two"
                }
            )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("do not match", resp.get_data(as_text=True))

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_email_not_found(self, mock_get_client):
        # Schema load passes
        with patch.object(schema_module.DataSchema, 'load', return_value={
            "email": self.email,
            "security_answer": self.security_answer,
            "new_password": self.new_password,
            "confirm_password": self.confirm_password
        }):
            # Mock DB returns no user
            mock_client = MagicMock()
            mock_db = MagicMock()
            mock_coll = MagicMock()
            mock_get_client.return_value = mock_client
            mock_client.get_database.return_value = mock_db
            mock_db.get_collection.return_value = mock_coll
            mock_coll.find_one.return_value = None

            resp = self.client.post(
                '/read',
                json={
                    "email": self.email,
                    "security_answer": self.security_answer,
                    "new_password": self.new_password,
                    "confirm_password": self.confirm_password
                }
            )
        self.assertEqual(resp.status_code, 404)
        self.assertIn("Email not found", resp.get_data(as_text=True))

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_incorrect_security_answer(self, mock_get_client):
        with patch.object(schema_module.DataSchema, 'load', return_value={
            "email": self.email,
            "security_answer": self.security_answer,
            "new_password": self.new_password,
            "confirm_password": self.confirm_password
        }), patch('bcrypt.checkpw', return_value=False):
            mock_client = MagicMock()
            mock_db = MagicMock()
            mock_coll = MagicMock()
            mock_get_client.return_value = mock_client
            mock_client.get_database.return_value = mock_db
            mock_db.get_collection.return_value = mock_coll
            mock_coll.find_one.return_value = {"email": self.email, "security_answer": self.hashed_answer}

            resp = self.client.post(
                '/read',
                json={
                    "email": self.email,
                    "security_answer": self.security_answer,
                    "new_password": self.new_password,
                    "confirm_password": self.confirm_password
                }
            )
        self.assertEqual(resp.status_code, 401)
        self.assertIn("incorrect", resp.get_data(as_text=True))

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_successful_password_change(self, mock_get_client):
        with patch.object(schema_module.DataSchema, 'load', return_value={
            "email": self.email,
            "security_answer": self.security_answer,
            "new_password": self.new_password,
            "confirm_password": self.confirm_password
        }), patch('bcrypt.checkpw', return_value=True), patch('bcrypt.hashpw', return_value=b'hashedpw'):
            mock_client = MagicMock()
            mock_db = MagicMock()
            mock_coll = MagicMock()
            mock_get_client.return_value = mock_client
            mock_client.get_database.return_value = mock_db
            mock_db.get_collection.return_value = mock_coll
            mock_coll.find_one.return_value = {"email": self.email, "security_answer": self.hashed_answer}

            resp = self.client.post(
                '/read',
                json={
                    "email": self.email,
                    "security_answer": self.security_answer,
                    "new_password": self.new_password,
                    "confirm_password": self.confirm_password
                }
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("message"), "Password changed successfully")
        mock_coll.update_one.assert_called_once_with(
            {"email": self.email}, {"$set": {"password": b'hashedpw'}}
        )

    @patch('src.database.MongoDB.MongoDB.getMongoClient', side_effect=Exception("DB error"))
    def test_internal_server_error(self, mock_get_client):
        with patch.object(schema_module.DataSchema, 'load', return_value={
            "email": self.email,
            "security_answer": self.security_answer,
            "new_password": self.new_password,
            "confirm_password": self.confirm_password
        }), patch('bcrypt.checkpw', return_value=True):
            resp = self.client.post(
                '/read',
                json={
                    "email": self.email,
                    "security_answer": self.security_answer,
                    "new_password": self.new_password,
                    "confirm_password": self.confirm_password
                }
            )
        self.assertEqual(resp.status_code, 500)
        self.assertIn("Internal server error", resp.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
