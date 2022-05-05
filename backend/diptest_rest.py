from rafodi import goal_function_for
from posixpath import split
from flask import Flask, jsonify, request, render_template
import numpy as np
import diptest.diptest as dt
app = Flask(__name__)


# Copied from stackoverflow
# put this snippet ahead of all your blueprints
# blueprint can also be app (I did replace that)
@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Methods'] = 'CALC, GET, KIWI'
    header['Access-Control-Allow-Headers'] = 'content-type'
    # Other headers can be added here if required
    return response


# Main page / Homepage / index
@app.route('/')
@app.route('/index')
def index():
    logger.info("Serving explanation.html")
    return render_template('explanation.html', title='Home')


# allow CALC and KIWI methods, because javascript won't allow adding JSON to a GET
@app.route('/dip', methods=['GET', 'CALC', 'KIWI'])
def get_dip():
    jsondata = request.get_json()
    result = dt.dip(np.array(jsondata))
    return jsonify(result)


# allow CALC and KIWI methods, because javascript won't allow adding JSON to a GET
@app.route('/diptest', methods=['GET', 'CALC', 'KIWI'])
def get_diptest():
    jsondata = request.get_json()
    result = dt.dip_test(np.array(jsondata))
    return jsonify(result)


# allow CALC and KIWI methods, because javascript won't allow adding JSON to a GET
@app.route('/findsplit', methods=['GET', 'CALC', 'KIWI'])
def find_split():

    cdf_vector = np.array(request.get_json())
    score, index, dip_all, dip_left, dip_right = goal_function_for(cdf_vector)

    json_response = {"dip_everything": dip_all,
                     "split_index": index,
                     "dip_left": dip_left,
                     "dip_right": dip_right,
                     "score": score}
    return jsonify(json_response)


if __name__ == "__main__":
    from waitress import serve
    import logging
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(app, host="0.0.0.0", port=5000)
