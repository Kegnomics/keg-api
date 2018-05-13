"""
Code that goes along with the Airflow tutorial located at:
https://github.com/airbnb/airflow/blob/master/airflow/example_dags/annotation_job.py
"""
from __future__ import absolute_import

import logging
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from kegapi.classifiers import build_dataframes
from kegapi.pubmed import pubmed_api
from kegapi.vcf import VcfApi

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 5, 12),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}


def annotate_vcf(**context):
    logging.info('context: {}'.format(context))

    my_dag_run = context['dag_run']
    config = my_dag_run.conf

    logging.info('Config: {}'.format(config))

    # file_path = kwargs['file_path']
    vcf = VcfApi()
    results = vcf.upload_file(file_path=config['file_path'])
    context['ti'].xcom_push(key='vcf_results', value=results)
    logging.info('Successfully pushed')


def filter_vcf(**context):
    results = context['ti'].xcom_pull(key=None, task_ids='annotate_vcf')
    logging.info('Results in filter_vcf: {}'.format(results))

    filtered_results = VcfApi.filter(results)
    logging.info('Successfully pushed filtered results')
    return filtered_results


def pubmed_nlp_job(**context):
    results = context['ti'].xcom_pull(key=None, task_ids='filter_vcf')
    keywords = context['dag_run'].conf['keywords']

    if keywords:
        return pubmed_api.get_by_keywords(keywords)
    else:
        return []


def create_variant_barchart(**context):
    results = context['ti'].xcom_pull(key=None, task_ids='annotate_vcf')
    counts = {}
    for res in results['data']:
        gene = res.get('info').get('Gene.refGene')
        if gene in counts:
            counts[gene] += 1
        else:
            counts[gene] = 1
    return counts


def clustering_task(**context):
    my_dag_run = context['dag_run']
    config = my_dag_run.conf

    build_dataframes(
        [
            config['file_path'],
        ],
        out_path='/home/cristi/Documents/hacktm/pca_graph.png'
    )
    # TODO do the clustering and display here

    return 'done clustering'


def write_results_to_db(**context):
    # TODO actually write
    filtered_variants = context['ti'].xcom_pull(key=None, task_ids='filter_vcf')
    pubmed_results = context['ti'].xcom_pull(key=None, task_ids='pubmed_nlp_task')
    gene_counts = context['ti'].xcom_pull(key=None, task_ids='create_variant_barchart_task')

    # db_path = '/home/cristi/Documents/hacktm/'
    #
    # with open(db_path + 'filtered_vars.p', 'wb') as f:
    #     pickle.dump(filtered_variants, f)
    #
    # with open(db_path + 'pubmed_results.p', 'wb') as f:
    #     pickle.dump(pubmed_results, f)
    my_dag_run = context['dag_run']
    config = my_dag_run.conf
    request_data = {
        'job_id': config['job_id'],
        'user_id': config['user_id'],
        'variants': filtered_variants,
        'gene_counts': gene_counts,
        'pubmed': pubmed_results,
    }

    resp = requests.post(config['end_url'], json=request_data)
    if resp == 200:
        print('All ok writing the crap')
    return 'done writing'


# Job definition
dag = DAG('annotation_job', default_args=default_args)

# do the annotations now
annotate_task = PythonOperator(
    python_callable=annotate_vcf,
    task_id='annotate_vcf',
    provide_context=True,
    dag=dag)

# filter_task
filter_task = PythonOperator(
    python_callable=filter_vcf,
    task_id='filter_vcf',
    provide_context=True,
    dag=dag)

# The task to get pubmed
pubmed_nlp_task = PythonOperator(
    python_callable=pubmed_nlp_job,
    task_id='pubmed_nlp_task',
    provide_context=True,
    dag=dag
)

filtered_results_keyword_task = PythonOperator(
    python_callable=clustering_task,
    task_id='clustering_task',
    provide_context=True,
    dag=dag
)

create_variant_barchart_task = PythonOperator(
    python_callable=create_variant_barchart,
    task_id='create_variant_barchart_task',
    provide_context=True,
    dag=dag
)

db_write_task = PythonOperator(
    python_callable=write_results_to_db,
    task_id='db_write_task',
    provide_context=True,
    dag=dag
)

filter_task.set_upstream(annotate_task)

pubmed_nlp_task.set_upstream(filter_task)
filtered_results_keyword_task.set_upstream(filter_task)
create_variant_barchart_task.set_upstream(filter_task)
db_write_task.set_upstream([pubmed_nlp_task, filtered_results_keyword_task, create_variant_barchart_task])
