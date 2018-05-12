from __future__ import absolute_import
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/cristi/Documents/hacktm/test.db'
if 'KEGAPI_SETTINGS' in os.environ:
    app.config.from_envvar('KEGAPI_SETTINGS')

db = SQLAlchemy(app)

import kegapi.models
import kegapi.views
