from flask import Flask, jsonify, request

import json

app = Flask(__name__)


@app.route('/dip')
def get_dip():
    record = request.get_json() 
    for el in record:
        print(el)
    return jsonify(record)