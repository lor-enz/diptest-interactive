from dip_goal import all_dip_calculations
from posixpath import split
from flask import Flask, jsonify, request, render_template, send_from_directory
import os
import numpy as np
import diptest.diptest as dt
import data_prep as data_prep

# The built Vue frontend (frontend/dist) is served as static files from the root path.
# The docker image copies it there; locally it only exists after running 'yarn build'.
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")
app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path='')

# Input limits. The frontend canvas is 800x500 px and sends one value per drawn
# column, so real requests stay well below these limits.
MAX_HISTO_LENGTH = 1000
MAX_HISTO_VALUE = 600
# The drawing is a density, not a sample. The dip test runs on an ideal sample of
# n points placed at the drawing's quantiles; n only matters for the p-value.
# The p-value table ends at n = 72000, and the dip calculation is O(n) in Python.
DEFAULT_SAMPLE_SIZE = 200
MIN_SAMPLE_SIZE = 10
MAX_SAMPLE_SIZE = 5000
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024  # bytes; Flask answers larger bodies with 413



# Copied from stackoverflow
# put this snippet ahead of all your @blueprint / @app 
@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Methods'] = 'CALC, GET, KIWI'
    header['Access-Control-Allow-Headers'] = 'content-type'
    # Other headers can be added here if required
    try: # try except, because sometimes Content-Length is missing.
        # print out size of response in KiB
        print(f"📏 Content-Length of response: {round(int(header['Content-Length']) /1024,2)} KibiByte")
    except:
        pass
    return response


# Frontend
@app.route('/')
def frontend():
    return send_from_directory(FRONTEND_DIST, 'index.html')


# API explanation page
@app.route('/api/')
def index():
    logger.info("Serving explanation.html")
    return render_template('explanation.html', title='Home')



def validate_histo(histo):
    """Returns an error message if histo is not a list of reasonably sized numbers, else None."""
    if not isinstance(histo, list):
        return "Expected a JSON array of numbers"
    if len(histo) > MAX_HISTO_LENGTH:
        return f"Array too long (max {MAX_HISTO_LENGTH} values)"
    for value in histo:
        # bool is a subclass of int, but true/false are not valid histogram values
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "Expected a JSON array of numbers"
        if not 0 <= value <= MAX_HISTO_VALUE:
            return f"Values must be between 0 and {MAX_HISTO_VALUE}"
    return None


# allow CALC and KIWI methods, because javascript won't allow adding JSON to a GET
@app.route('/api/dip-from-histo', methods=['GET', 'CALC', 'KIWI'])
def dip_from_histo():
    histo = request.get_json(silent=True)
    error = validate_histo(histo)
    if error:
        return jsonify({"message": error}), 400
    if sum(histo) <= 0:
        return jsonify({"message": "Histogram is empty"}), 400
    n = request.args.get('n', DEFAULT_SAMPLE_SIZE, type=int)
    if not MIN_SAMPLE_SIZE <= n <= MAX_SAMPLE_SIZE:
        return jsonify({"message": f"n must be between {MIN_SAMPLE_SIZE} and {MAX_SAMPLE_SIZE}"}), 400
    samples = data_prep.quantile_samples_from_histo(histo, n)

    dip_value, pval, modal_triangle, low_high = all_dip_calculations(data=samples, is_data_sorted=True)

    # bar i covers [i, i+1), so a sample's bar is its integer part
    bar_of = lambda index: int(samples[index]) if index is not None else None
    mod_tri = [bar_of(index) for index in modal_triangle] if modal_triangle else None
    lo_hi = [bar_of(index) for index in low_high]

    json_response = {"dip": dip_value,
                     "pval": pval,
                     "n": n,
                     "low_high": lo_hi,
                     "modal_triangle": mod_tri,
                     }
    return jsonify(json_response)


if __name__ == "__main__":
    from waitress import serve
    import logging
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(app, host="0.0.0.0", port=5000)
