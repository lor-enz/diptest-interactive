from dip_goal import goal_function_for, all_dip_calculations
from posixpath import split
from flask import Flask, jsonify, request, render_template
import numpy as np
import diptest.diptest as dt
app = Flask(__name__)


# Copied from stackoverflow
# put this snippet ahead of all your @blueprint 
# @blueprint can also be @app (Lorenz: I did replace that)
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
    cdf_vector = np.array(request.get_json())
    dip_value, low_high, modal_triangle = dt.dip(
        np.sort(cdf_vector), just_dip=False, is_data_sorted=True)
    json_response = {"dip": dip_value,
                     "low_high": low_high,
                     "modal_triangle": modal_triangle
                     }
    return jsonify(json_response)


# allow CALC and KIWI methods, because javascript won't allow adding JSON to a GET
@app.route('/diptest', methods=['GET', 'CALC', 'KIWI'])
def get_diptest():
    cdf_vector = np.array(request.get_json())
    data_dip, pval = dt.dip_test(cdf_vector)
    json_response = {"dip": data_dip,
                     "pval": pval}
    return jsonify(json_response)


# allow CALC and KIWI methods, because javascript won't allow adding JSON to a GET
@app.route('/dipsplit', methods=['GET', 'CALC', 'KIWI'])
def find_split():
    
    cdf_vector = np.array(request.get_json())
    print(f"Got request with cdf: {cdf_vector[:3]} ... ]")
    if len(cdf_vector) < 8:
        return jsonify({"message": "Array too short"})
    score, index, dip_all, dip_left, dip_right = goal_function_for(cdf_vector)

    dip_value, pval, modal_triangle, low_high = all_dip_calculations(data=np.sort(cdf_vector), is_data_sorted=True)

    json_response = {"dip": dip_value,
                     "low_high": low_high,
                     "modal_triangle": modal_triangle,
                     # - - - - - - -
                     "split_index": index,
                     "dip_left": dip_left,
                     "dip_right": dip_right,
                     "score": score,
                     # - - - - - - -
                     "pval": pval
                     }
    return jsonify(json_response)


if __name__ == "__main__":
    from waitress import serve
    import logging
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(app, host="0.0.0.0", port=5000)
