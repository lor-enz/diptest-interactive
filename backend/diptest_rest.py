from posixpath import split
from flask import Flask, jsonify, request, render_template
import numpy as np
import diptest.diptest as dt
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

# Main page / Homepage / index
@app.route('/')
@app.route('/index')
def index():
    return render_template('explanation.html', title='Home')

# because javascript won't allow adding JSON to a GET
@app.route('/dip', methods=['GET', 'CALC', 'KIWI'])
def get_dip():
    jsondata = request.get_json()
    result = dt.dip(np.array(jsondata))
    return jsonify(result)


# because javascript won't allow adding JSON to a GET
@app.route('/diptest', methods=['GET', 'CALC', 'KIWI'])
def get_diptest():
    jsondata = request.get_json()
    result = dt.dip_test(np.array(jsondata))
    return jsonify(result)


# because javascript won't allow adding JSON to a GET
@app.route('/findsplit', methods=['GET', 'CALC', 'KIWI'])
def find_split():
    
    cdf_vector = np.array(request.get_json())
    score, index, dip_all, dip_left, dip_right = goal_function_for(cdf_vector)

    json_response = {"dip_everything": dip_all,
                     "split_index": index,
                     "dip_left": dip_left,
                     "dip_right": dip_right,
                     "score": score }
    return jsonify(json_response)


# copied from rafodi.py
def split_at(index, column):
    left = column[:index]  # From Beginning to (excluding) index
    right = column[index:]  # From (including) index to End
    return left, right

# copied from rafodi.py, but improved!
def goal_function_for(sorted_numpy_column):
    print(f"Goal function...")
    b_score = -999  # we want: max
    b_dip_all = -999  # we want: max
    b_dip_left = 999  # we want: min
    b_dip_right = 999  # we want: min
    b_index = -1
    length = len(sorted_numpy_column)
    for i in range(2, len(sorted_numpy_column)-1):
        left, right = split_at(i, sorted_numpy_column)
        dip_left = dt.dip(left)
        dip_right = dt.dip(right)
        dip_all = dt.dip(sorted_numpy_column)
        score = dip_all - dip_left - dip_right
        # print(f"Calcuated score at split {i} is {score}. Current best score is {b_score} at split {b_index} ")
        if score > b_score:
            b_score = score
            b_dip_all = dip_all
            b_dip_left = dip_left
            b_dip_right = dip_right
            b_index = i
        assert length == len(sorted_numpy_column)
    return b_score, b_index, b_dip_all, b_dip_left, b_dip_right


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
