import unittest
from unittest.mock import patch, MagicMock
from marshmallow import ValidationError
from flask import Flask
import src.routes.get_security_question.schema as schema_module
from src.routes.get_security_question import get_security_question_bp

class GetSecurityQuestionTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(get_security_question_bp)
        self.client = self.app.test_client()
        self.email = "user@example.com"

    @patch.object(schema_module.DataSchema, 'load', side_effect=ValidationError({"email": ["Missing data"]}))
    def test_schema_validation_error(self, mock_load):
        resp = self.client.post(
            '/get-security-question',
            json={"email": self.email}
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data.get("error"), "JSON body does not match schema")
        self.assertIn("email", data.get("messages", {}))

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    @patch.object(schema_module.DataSchema, 'load', return_value=None)
    def test_email_not_found(self, mock_load, mock_get_client):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_coll = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value = mock_coll
        mock_coll.find_one.return_value = None

        resp = self.client.post(
            '/get-security-question',
            json={"email": self.email}
        )
        self.assertEqual(resp.status_code, 404)
        self.assertIn("Email not found", resp.get_data(as_text=True))

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    @patch.object(schema_module.DataSchema, 'load', return_value=None)
    def test_successful_security_question(self, mock_load, mock_get_client):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_coll = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value = mock_coll
        mock_coll.find_one.return_value = {"email": self.email, "security_question": "Favorite color?"}

        resp = self.client.post(
            '/get-security-question',
            json={"email": self.email}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"security_question": "Favorite color?"})

    @patch.object(schema_module.DataSchema, 'load', return_value=None)
    @patch('src.database.MongoDB.MongoDB.getMongoClient', side_effect=Exception("DB failure"))
    def test_internal_server_error(self, mock_get_client, mock_load):
        resp = self.client.post(
            '/get-security-question',
            json={"email": self.email}
        )
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.get_json().get("error"), "Internal server error")

if __name__ == '__main__':
    unittest.main()
