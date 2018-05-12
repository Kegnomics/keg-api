import json
import os
import tempfile

from werkzeug.utils import redirect, secure_filename

from kegapi import app, db
from kegapi.models import JobRun
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
        result_json = {
            'results': pubmed_api.get_by_keywords(keywords, maxres=maxres)
        }
        return jsonify(result_json)
    else:
        return jsonify({'error': 'Invalid arguments. Required: keywords (comma separated list)'}), 400


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/upload', methods=['POST'])
def initial_upload():
    file = request.files['vcf']
    form = json.loads(request.form['keywords'])
    user_id = request.form['user_id']
    print('KW: {}'.format(form))
    print('user: {}'.format(user_id))

    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    job = JobRun(user_id=user_id, done=0)

    db.session.add(job)
    db.session.commit()
    return jsonify({'job_id': job.id})


@app.route('/api/jobs', methods=['GET'])
def jobs_index():
    job_id = request.args.get('job_id')
    user_id = request.args.get('user_id')
    if not user_id:
        return {'error': 'Must include user_id in params'}, 400
    if job_id:
        job_id = int(job_id)
        job = JobRun.query.filter_by(id=job_id, user_id=user_id)
        if not job.count():
            return jsonify({'error': 'Job with id not found'}), 404

        return jsonify({'job': JobRun.serialize_json(job.first())})
    else:
        all_res = [JobRun.serialize_json(obj) for obj in JobRun.query.filter_by(user_id=user_id)]
        print('All res: {}'.format(all_res))
        return jsonify({'results': all_res})
