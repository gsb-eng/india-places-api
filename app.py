from flask import Flask

from db import db_session


app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/india')
def IndiaApi():
    
    return "Hello World!"

@app.route('/india/data')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__ == '__main__':
    app.run()

