from kegapi import app
from kegapi.pubmed import pubmed_api
from flask import request, jsonify


@app.route('/')
def index():
    request.args
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
