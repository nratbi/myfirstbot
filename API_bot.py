 #!/usr/bin/env python
# -*- coding: utf-8 -*- 
from flask import jsonify, request, Flask
from flask import Request
import os
from pymongo import MongoClient

app = Flask(__name__) 
@app.route("/response/", methods=['GET','POST'])
def response():
	client = MongoClient("mongodb://heroku_fkfhqw1w:mtkhac4bj08bu2qs02gm0i4s79@ds147964.mlab.com:47964/heroku_fkfhqw1w")
	computers = client["heroku_fkfhqw1w"].computers
	m = request.get_json()
	indicators = m['result']['parameters']
	if 'game' in indicators:
		find_pc_gamer = computers.aggregate([{'$project':{'total':{'$sum' : ['processeur_rate','carte_graphique_rate']}}}])
		for item in find_pc_gamer:
			print(item)
	return jsonify(m)



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)

