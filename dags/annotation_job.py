"""
Code that goes along with the Airflow tutorial located at:
https://github.com/airbnb/airflow/blob/master/airflow/example_dags/annotation_job.py
"""
from __future__ import absolute_import

import json, logging

from airflow import DAG
from airflow.api.common.experimental.trigger_dag import trigger_dag
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

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

    # TODO actually filter
    filtered_results = results
    logging.info('Successfully pushed filtered results')
    return filtered_results


def pubmed_nlp_job(**context):
    results = context['ti'].xcom_pull(key=None, task_ids='filter_vcf')
    keywords = context['dag_run'].conf['keywords']

    return pubmed_api.get_by_keywords(keywords)


def filtered_results_keyword_search(**context):
    results = context['ti'].xcom_pull(key=None, task_ids='filter_vcf')
    # TODO do the search here
    return 'end'


def write_results_to_db(**context):
    # TODO actually write
    return 'done writing'


### Job definition
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
    python_callable=filtered_results_keyword_search,
    task_id='filtered_results_keyword_search',
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
db_write_task.set_upstream([pubmed_nlp_task, filtered_results_keyword_task])
