from flask import Flask, jsonify

from db import db_session
from india_data import IndiaData


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/india/<state>')
def index(state):
    ind = IndiaData()
    return jsonify(ind.pincode_data(state))

if __name__ == '__main__':
    
    app.run()

