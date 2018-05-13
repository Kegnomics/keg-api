import json
import operator
import os
import tempfile

from nltk.corpus import stopwords
from werkzeug.utils import redirect, secure_filename

from kegapi.app import app, db
from kegapi.models import JobRun, populate_pubmed_data, populate_variant_data, populate_gene_count, GeneCounts
from kegapi.constants import ALLOWED_EXTENSIONS
from kegapi.pubmed import pubmed_api
from flask import request, jsonify, flash, send_file
from kegapi.pipeline_operations import trigger_airflow_job
import nltk
import collections


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


@app.route('/api/upload', methods=['POST'])
def initial_upload():
    file = request.files['vcf']
    keywords = json.loads(request.form['keywords'])
    user_id = request.form['user_id']
    runname = request.form['runName']
    print('KW: {}'.format(keywords))
    print('user: {}'.format(user_id))

    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if file:
        file.save(file_path)
    else:
        return jsonify({'error': 'Invalid file!'}), 400

    job = JobRun(user_id=user_id, runname=runname, done=0)

    db.session.add(job)
    db.session.commit()

    # Start the airflow job
    config = {
        'job_id': job.id,
        'user_id': job.user_id,
        'file_path': file_path,
        'keywords': keywords,
        'end_url': 'http://localhost:5000/api/end_job_run'
    }
    trigger_airflow_job(config)

    return jsonify({'job_id': job.id})


@app.route('/api/jobs', methods=['GET'])
def jobs_index():
    job_id = request.args.get('job_id')
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Must include user_id in params'}), 400
    if job_id:
        job_id = int(job_id)
        job = JobRun.query.filter_by(id=job_id, user_id=user_id)
        if not job.count():
            return jsonify({'error': 'Job with id not found'}), 404

        return jsonify({'job': JobRun.serialize_json(job.first())})
    else:
        all_res = [JobRun.serialize_json(obj) for obj in JobRun.query.filter_by(user_id=user_id)]
        return jsonify({'results': all_res})


@app.route('/api/test-trigger', methods=['GET'])
def trigger_dag_test():
    config = {
        'job_id': 1,
        'user_id': 123,
        'file_path': '/home/cristi/Documents/hacktm/J2_S2.vcf',
        'keywords': ['breast', 'cancer'],
        'end_url': 'http://localhost:5000/api/end_job_run'
    }

    print(trigger_airflow_job(config))

    return jsonify({'job_result': 'started'})


@app.route('/api/stats/commonWords', methods=['GET'])
def get_most_common_words_in_run():
    job_id = request.args.get('job_id')
    user_id = request.args.get('user_id')
    if job_id is None or user_id is None:
        return jsonify({'error': 'JobId or user_id are none'}), 400

    english_stopwords = stopwords.words('english')
    job = JobRun.query.filter_by(id=job_id, user_id=user_id).first()
    most_common = {}
    for article in job.pubmedarticles:
        words = nltk.word_tokenize(article.abstract)
        words = [word.lower() for word in words if word.isalpha() and word not in english_stopwords]
        for k in words:
            if k in most_common:
                most_common[k] += 1
            else:
                most_common[k] = 1

    sorted_stuff = sorted(most_common.items(), key=operator.itemgetter(1), reverse=True)

    return jsonify({'results': sorted_stuff[:10]})


@app.route('/api/end_job_run', methods=['POST'])
def end_job_run():
    """
    End the job and create all instances in the db
    :return:
    """

    request_data = json.loads(request.data)
    job_id = request_data.get('job_id')
    user_id = request_data.get('user_id')
    pubmed_data = request_data.get('pubmed')
    filtered_variants = request_data.get('variants')
    gene_counts = request_data.get('gene_counts')

    job = JobRun.query.filter_by(id=job_id, user_id=user_id).first()

    populate_variant_data(job, filtered_variants)
    populate_pubmed_data(job, pubmed_data)
    populate_gene_count(job, gene_counts)
    job.done = 1
    db.session.commit()

    return jsonify({'status': 'ok'})


@app.route('/api/getLastCluster', methods=['GET'])
def get_clustering_img():
    filename = '/home/cristi/Documents/hacktm/pca_graph.png'
    return send_file(filename, mimetype='image/png')


@app.route('/api/stats/barChart', methods=['GET'])
def get_bar_chart():
    job_id = request.args.get('job_id')
    user_id = request.args.get('user_id')
    if job_id is None or user_id is None:
        return jsonify({'error': 'JobId or user_id are none'}), 400

    job = JobRun.query.filter_by(id=job_id, user_id=user_id).first()

    return jsonify({'results': [GeneCounts.serialize_json(obj) for obj in job.genecounts]})
