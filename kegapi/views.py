from kegapi import app
from flask import request

@app.route('/')
def index():

    request.args
    return 'Hello World!'