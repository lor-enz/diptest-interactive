from dip_goal import goal_function_for, all_dip_calculations, create_ecdf_from_samples
from posixpath import split
from flask import Flask, jsonify, request, render_template
import numpy as np
import diptest.diptest as dt
import data_prep as data_prep
app = Flask(__name__)



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
        # print out size of reponse in KiB
        print(f"📏 Content-Length of response: {round(int(header['Content-Length']) /1024,2)} KibiByte")
    except:
        pass
    return response


# Main page / Homepage / index
@app.route('/')
@app.route('/index')
def index():
    logger.info("Serving explanation.html")
    return render_template('explanation.html', title='Home')



# Musst nur noch bei den Indices vom modal intervall und triangle aufpassen, 
# weil in der x-Koordinate mehrere Werte drinstecken. Weiß nicht wie du das umrechnest


# allow CALC and KIWI methods, because javascript won't allow adding JSON to a GET
@app.route('/dip-from-histo', methods=['GET', 'CALC', 'KIWI'])
def dip_from_histo():
    histo = request.get_json()
    chosen_deviation = 0.2
    randomized_samples = np.array(data_prep.infer_samples_from_histo(histo, standard_deviation=chosen_deviation))
    actual_samples = np.array(data_prep.infer_samples_from_histo(histo, randomize=False))
    print(f"🧮 Got request with {len(actual_samples)} samples. Randomized them by standard_deviation={chosen_deviation}")
    if len(randomized_samples) < 8:
        return jsonify({"message": "Array too short"})
    
    #score, index, dip_all, dip_left, dip_right = goal_function_for(samples)
    dip_value, pval, modal_triangle, low_high = all_dip_calculations(data=randomized_samples, is_data_sorted=True)
    
    a = int(actual_samples[modal_triangle[0]])
    b = int(actual_samples[modal_triangle[1]])
    c = int(actual_samples[modal_triangle[2]])
    mod_tri = [a, b, c]
    g = int(actual_samples[low_high[0]])
    h = int(actual_samples[low_high[1]])
    lo_hi = [g,h]

    ecdf = create_ecdf_from_samples(randomized_samples)

    json_response = {"dip": dip_value,
                     "pval": pval,
                     "low_high": lo_hi,
                     "modal_triangle": mod_tri,
                     "ecdf": ecdf # can be up to 400KiB of data each time.
                     }
    return jsonify(json_response)


if __name__ == "__main__":
    from waitress import serve
    import logging
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(app, host="0.0.0.0", port=5000)
