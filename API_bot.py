 #!/usr/bin/env python
# -*- coding: utf-8 -*- 
from flask import jsonify, request, Flask
import rollbar
import rollbar.contrib.flask
from flask import Request
from flask import got_request_exception
import os

app = Flask(__name__) 
@app.route("/response/", methods=['GET','POST'])
def response():
	m = request.get_json()
	print(m['parameters'])
	return jsonify(m)



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)

