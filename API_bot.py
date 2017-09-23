 #!/usr/bin/env python
# -*- coding: utf-8 -*- 
import pgdb
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import jsonify, request, Flask
from sklearn.externals import joblib
from sklearn.feature_extraction import DictVectorizer
import itertools
import nltk
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from sklearn.linear_model import LogisticRegression
from nltk.corpus import stopwords
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import SelectFromModel
import csv
import os
import rollbar
import rollbar.contrib.flask
from flask import Request
from flask import got_request_exception
from bs4 import BeautifulSoup 
import re
from rq import Queue
from worker import conn
import time
import datetime
from dateutil import parser

app = Flask(__name__) 
@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    rollbar.init(
        # access token for the demo app: https://rollbar.com/demo
        '0200a206c3934cc99fabbdad7ad20da3',
        # environment name
        '.env',
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

class CustomRequest(Request):
    @property
    def rollbar_person(self):
        # 'id' is required, 'username' and 'email' are indexed but optional.
        # all values are strings.
        return {'id': '123', 'username': 'admin', 'email': 'nabil.ratbienstb@gmail.com'}

app.request_class = CustomRequest

@app.route("/response/", methods=['GET'])
def response():
	m = request.get_json()
	return m



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)

