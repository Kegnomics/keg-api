import json


def trigger_airflow_job(conf, dag_name='annotation_job'):
    import subprocess
    json_conf = json.dumps(conf)
    subprocess.call(['airflow', 'trigger_dag', '-c', json_conf, dag_name], shell=True)
    return 'done'
