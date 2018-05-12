import os

from werkzeug.utils import redirect, secure_filename

from kegapi import app
from kegapi.constants import ALLOWED_EXTENSIONS
from kegapi.pubmed import pubmed_api
from flask import request, jsonify, flash


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/api/pubmed')
def pubmed_keywords():
    k = request.args.get('keywords')
    maxres = request.args.get('maxres')
    if not maxres:
        maxres = 10
    maxres = int(maxres)
    if k:
        keywords = k.split(',')
        return jsonify(pubmed_api.get_by_keywords(keywords, maxres=maxres))
    else:
        return jsonify({'error': 'Invalid arguments. Required: keywords (comma separated list)'}), 400


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/upload', methods=['POST'])
def initial_upload():
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
