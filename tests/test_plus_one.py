import unittest
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta, timezone
from flask import Flask
from src.routes.plus_one import plus_one_bp

@patch.dict('env.env', {'JWT_SECRET_KEY': 'testsecret'}, clear=True)
class PlusOneTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(plus_one_bp)
        self.client = self.app.test_client()
        self.email = "test@example.com"
        self.valid_token = jwt.encode(
            {"email": self.email, "exp": datetime.now(timezone.utc) + timedelta(days=1)},
            'testsecret',
            algorithm="HS256"
        )

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_successful_plus_one(self, mock_get_client):
        mock_client = MagicMock()
        mock_db     = MagicMock()
        mock_coll   = MagicMock()
        mock_get_client.return_value        = mock_client
        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value  = mock_coll

        # first find_one → existence check, second → updated doc
        mock_coll.find_one.side_effect = [
            {"email": self.email, "count": 0},
            {"email": self.email, "count": 1}
        ]

        resp = self.client.post('/plus-one',
            json={"email": self.email, "auth_token": self.valid_token}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"email": self.email, "count": 1})
        mock_coll.update_one.assert_called_once_with(
            {"email": self.email}, {"$inc": {"count": 1}}
        )

    def test_invalid_json(self):
        resp = self.client.post('/plus-one', json={"email": self.email})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("JSON body does not match schema", resp.get_data(as_text=True))

    def test_token_expired(self):
        with patch('jwt.decode', side_effect=jwt.ExpiredSignatureError):
            resp = self.client.post('/plus-one',
                json={"email": self.email, "auth_token": "deadtoken"}
            )
            self.assertEqual(resp.status_code, 401)
            self.assertIn("Token has expired", resp.get_data(as_text=True))

    def test_invalid_token(self):
        with patch('jwt.decode', side_effect=jwt.InvalidTokenError):
            resp = self.client.post('/plus-one',
                json={"email": self.email, "auth_token": "badtoken"}
            )
            self.assertEqual(resp.status_code, 401)
            self.assertIn("Invalid token", resp.get_data(as_text=True))

    def test_decode_internal_error(self):
        with patch('jwt.decode', side_effect=Exception("decode oops")):
            resp = self.client.post('/plus-one',
                json={"email": self.email, "auth_token": "weirdtoken"}
            )
            self.assertEqual(resp.status_code, 500)
            self.assertIn("Internal server error", resp.get_data(as_text=True))

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_email_not_found(self, mock_get_client):
        mock_client = MagicMock()
        mock_db     = MagicMock()
        mock_coll   = MagicMock()
        mock_get_client.return_value        = mock_client
        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value   = mock_coll

        mock_coll.find_one.return_value = None

        resp = self.client.post('/plus-one',
            json={"email": self.email, "auth_token": self.valid_token}
        )
        self.assertEqual(resp.status_code, 404)
        self.assertIn("Email not found", resp.get_data(as_text=True))

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_mongo_internal_error(self, mock_get_client):
        mock_get_client.side_effect = Exception("DB down")
        resp = self.client.post('/plus-one',
            json={"email": self.email, "auth_token": self.valid_token}
        )
        self.assertEqual(resp.status_code, 500)
        self.assertIn("Internal server error", resp.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
