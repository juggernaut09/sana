from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import json
import os
import requests
from datetime import datetime

application = Flask(__name__)

application.config["MONGO_URI"] = "mongodb://localhost:27017/rasa"
mongo = PyMongo(application)
db = mongo.db
print(db)
@application.route('/')
def hello():
    return "Hello From  Client"

@application.route('/contactus', methods=["POST"])
def contact_us():
    try:
        payload = request.get_json()
        existing = db.contacts.find_one({
            'status': 'active',
            "$or": [ { 'email': payload["email"] }, { 'mobile': payload["mobile"] } ]
        })
        if existing:
            return jsonify({
                'message': "You have already submitted your details, You will be contacted by our HR team soon",
                "status_code": 401,
                'internal_data': None
            }), 401
        response = db.contacts.insert_one({
        'name': payload['name'],
        'email': payload['email'],
        'mobile': payload['mobile'],
        'status': 'active',
        'created_at': datetime.now(),
        'deleted_at': None,
        'updated_at': None
        })
        if response:
            return jsonify({
                'message': "Dear {}, Your details have been submitted successfully you will be contacted by our HR team soon.".format(payload['name']),
                'internal_data': None,
                'status_code': 200
            }), 200
        return jsonify({
        'message': "Something went wrong Please try again later",
        "status_code": 500,
        'internal_data': None
        }), 500

    except Exception as e:
        return jsonify({
        'message': "Something went wrong Please try again later",
        "status_code": 500,
        'internal_data': str(e)
        }), 500




if __name__ == "__main__":
    application.run(host = '0.0.0.0', debug=True, use_reloader=True)
