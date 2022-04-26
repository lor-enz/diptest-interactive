from flask import Flask, jsonify, request
import numpy as np
from diptest.diptest import dip
app = Flask(__name__)


@app.route('/dip')
def get_dip():
    record = request.get_json() 
    result = dip_wrapper(record)
    return jsonify(result)


def dip_wrapper(oned_dataset, is_dataset_numpy=False, data_sorted=False):
    if not is_dataset_numpy:
        oned_dataset = np.array(oned_dataset)
    dip_value = dip(oned_dataset, just_dip=True, is_data_sorted=data_sorted, use_c=True, debug=False)
    return dip_value

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)