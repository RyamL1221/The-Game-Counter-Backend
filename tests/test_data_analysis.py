import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
import json
from src.routes.data_analysis import data_analysis_bp

class DataAnalysisTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(data_analysis_bp)
        self.client = self.app.test_client()

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_successful_data_analysis(self, mock_get_client):
        # Prepare mock MongoDB
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_coll = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value = mock_coll
        # Simulate documents with counts
        docs = [ {'count': 1}, {'count': 2}, {'count': 3} ]
        mock_coll.find.return_value = docs

        # Call endpoint
        resp = self.client.get('/data_analysis')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        # Expect n=3, mean=2.0, median=2.0, variance=0.666..., std_dev~0.8165, min=1.0, max=3.0
        self.assertEqual(data['n'], 3)
        self.assertAlmostEqual(data['mean'], 2.0)
        self.assertAlmostEqual(data['median'], 2.0)
        self.assertAlmostEqual(data['variance'], 0.6666666666666666, places=6)
        self.assertAlmostEqual(data['std_dev'], 0.816496580927726, places=6)
        self.assertAlmostEqual(data['min'], 1.0)
        self.assertAlmostEqual(data['max'], 3.0)

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_no_data_found(self, mock_get_client):
        # Mock an empty collection
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_coll = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value = mock_coll
        mock_coll.find.return_value = []

        resp = self.client.get('/data_analysis')
        self.assertEqual(resp.status_code, 404)
        data = resp.get_json()
        self.assertEqual(data['error'], 'No data found')

    @patch('src.database.MongoDB.MongoDB.getMongoClient')
    def test_internal_server_error(self, mock_get_client):
        # Simulate DB connection failure
        mock_get_client.side_effect = Exception("DB down")
        resp = self.client.get('/data_analysis')
        self.assertEqual(resp.status_code, 500)
        data = resp.get_json()
        self.assertEqual(data['error'], 'Internal server error')

if __name__ == '__main__':
    unittest.main()