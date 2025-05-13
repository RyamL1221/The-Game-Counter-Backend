from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ...database.MongoDB import MongoDB
import numpy as np

data_analysis_bp = Blueprint("data_analysis", __name__)

@data_analysis_bp.route('/data-analysis',methods =['GET'])
def data_analysis():
    try:
        client = MongoDB.getMongoClient()
        db = client.get_database()
        collection = db.get_collection('count')

        all_counts = collection.find({}, {'_id': 0, 'count': 1})
        count_arr = [doc['count'] for doc in all_counts if 'count' in doc]

        if not count_arr:
            return jsonify({"error": "No data found"}), 404

        np_arr = np.array(count_arr, dtype=float)  

        stats = {
            "n": int(np_arr.size),
            "mean": np.mean(np_arr),
            "median": np.median(np_arr),
            "std_dev": np.std(np_arr),
            "variance": np.var(np_arr),
            "min": np.min(np_arr),
            "max": np.max(np_arr)
        }

        return jsonify(stats), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500
        
