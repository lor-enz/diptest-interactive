from flask import Flask, jsonify, request
import numpy as np
from diptest.diptest import dip
app = Flask(__name__)


# put this sippet ahead of all your bluprints
# blueprint can also be app~~
@app.after_request 
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Methods'] = 'CALC, GET, KIWI'
    header['Access-Control-Allow-Headers'] = 'content-type'
    # Other headers can be added here if required
    return response

@app.route('/dip', methods=['GET', 'CALC', 'KIWI']) # because javascript won't allow adding JSON to a GET
def get_dip():
    jsondata = request.get_json() 
    result = dip(np.array(jsondata))
    return jsonify(result)



if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)