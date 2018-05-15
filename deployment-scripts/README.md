## Deployment scripts

In order to deploy the keg-api on a fresh machine, a few steps have to be taken:

1. Install virtualenv / virtualenvwrapper and then install the packages inside a newly created Python 3 venv. Run the server after that.

2. Install `redis-server` (`apt install redis-server`) and setup airflow.


## 1. Install all prerequisites

First install venv:

```
sudo apt install -y python3-pip

sudo python-3 -m pip install virtualenv virtualenvwrapper
```


Then, create your virtualenv folder (default ~/.venvs) and set the env variable:  `export WORKON_HOME=~/.venvs`

Use the `.kegrc` script here as a starting point and do `source .kegrc` to setup most of the things needed. Add the `kegapi.cfg` file in the right spot (where `KEGAPI_SETTINGS` points to in the .kegrc file).

Then, the first time, create the venv: `mkvirtualenv <NAME>` . After that just call `workon <NAME>`.

In the kegapi folder, install everything and run the app:

```
python -m pip install -r requirements.txt

python -m flask run --host 0.0.0.0
```

If all went well the following url should work:

```
http://localhost:5000/api/jobs?user_id=123
```

## 2. Setting up airflow

After installing everything from pip, use the following command:

```
airflow initdb
```

This will create a directory under `~/airflow`. The most important part of it is `airflow.cfg`. Open the file in the text editor and modify the following configs:

```
dags_folder = /location/to/keg-api/dags


broker_url = redis://localhost:6379/0

celery_result_backend = redis://localhost:6379/0

```


Then launch the webserver and scheduler with the following commands:

```
airflow webserver
airflow scheduler
```

You should be able to see the dags and the UI at localhost:8080


