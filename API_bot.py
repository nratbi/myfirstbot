 #!/usr/bin/env python
# -*- coding: utf-8 -*- 
from flask import jsonify, request, Flask
from flask import Request
import os
from pymongo import MongoClient
from bson.son import SON
from flask import Response

app = Flask(__name__) 
@app.route("/", methods=['GET','POST'])
def facebook_verification():
	print(request.args[1])
	return Response("ok", status=200, mimetype='application/json')

@app.route("/response/", methods=['GET','POST'])
def response():
	client = MongoClient("mongodb://heroku_fkfhqw1w:mtkhac4bj08bu2qs02gm0i4s79@ds147964.mlab.com:47964/heroku_fkfhqw1w")
	computers = client["heroku_fkfhqw1w"].computers
	m = request.get_json()
	indicators = m['result']['parameters']
	if 'game' in indicators:
		find_pc_gamer = computers.aggregate([{"$addFields":{'gamer_rate':{'$add' :['$processeur_rate','$carte_graphique_rate']}}},{'$sort':SON([("gamer_rate", -1)])}])
		best_computers = {}
		i = 0
		find_pc_gamer = list(find_pc_gamer)
		while find_pc_gamer[i]['gamer_rate'] == find_pc_gamer[0]['gamer_rate']:
			best_computers[i] = {}
			best_computers[i]['nom'] = find_pc_gamer[i]['nom']
			best_computers[i]['prix'] = find_pc_gamer[i]['prix']
			i = i+1
		print(best_computers)
		best_cheap = min(best_computers[k]['prix'] for k in range(len(best_computers.keys())))
		name_cheap = [best_computers[k]['nom'] for k in range(len(best_computers.keys())) if best_computers[k]['prix'] == best_cheap]
		speech = "Hum..Je vois. J'ai l'ordinateur qu'il vous faut : "+name_cheap[0]
		for word in name_cheap[1:]:
			speech += "," + word
		speech += "!"
		response = {
		'speech': speech,
		'displayText' : speech,
		'data':None,
		'contextOut' : None,
		'source':'',
		'followupEvent' : None
		}
		print(response)

	return jsonify(response)



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)

