 #!/usr/bin/env python
# -*- coding: utf-8 -*- 
from flask import jsonify, request, Flask
from flask import Request
import os

app = Flask(__name__) 
@app.route("/response/", methods=['GET','POST'])
def response():
	m = request.get_json()
	indicators = m['result']['parameters']
	if 'game' in indicators:
		print('Le user est un gamer')
	return jsonify(m)



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)

