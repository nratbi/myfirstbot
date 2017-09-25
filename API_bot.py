 #!/usr/bin/env python
# -*- coding: utf-8 -*- 
from __future__ import division
from flask import jsonify, request, Flask
from flask import Request
import os
from pymongo import MongoClient
from bson.son import SON
from flask import Response
import sys
import json
import requests
import pandas as pd
import numpy as np
import numbers
import math

def calculate_utility(weights, vector, mins_criteria, maxs_criteria):
    utility_vector = [(weights[i]/sum(weights))*(vector[i]-mins_criteria[i])/(maxs_criteria[i]-mins_criteria[i]) for i in range(len(vector))]
    utility = np.nansum(utility_vector)
    return utility

def send_message(recipient_id, message_text):

    params = {
        "access_token": "EAAXFoXg4V2oBANtEWids8btXLLN3xMfu2xkZBoaQqwmkSZCheKJZCbZABG8Cmb1hamD0ZCZAK5DZCLYQmU2eXnsGB6pAJ3TZATvFjGczUeCwEsJvFXJujrw7DtF9CZBwPk9tixFUJ134Fj5HrgMtBOlw8KnHsst46IjTB5kv4XolZB9QZDZD"
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)


app = Flask(__name__) 
@app.route("/", methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "ok", 200

@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    headers = {
                    "Content-Type": "application/json",
                    "Authorization" : "Bearer 4c6588d427284768823a5520af36c901"
                    }
                    content = json.dumps({
                    "query": message_text,
                    "timezone": "Europe/Paris",
                    "lang": "fr",
                    "contexts" : [],
                    "sessionId": "c2f3eb24-8ed5-42c3-9ec1-ee51f0bb607c"
                    })
                    params2 = {
                    "access_token": "EAAXFoXg4V2oBANtEWids8btXLLN3xMfu2xkZBoaQqwmkSZCheKJZCbZABG8Cmb1hamD0ZCZAK5DZCLYQmU2eXnsGB6pAJ3TZATvFjGczUeCwEsJvFXJujrw7DtF9CZBwPk9tixFUJ134Fj5HrgMtBOlw8KnHsst46IjTB5kv4XolZB9QZDZD"
                    }
                    headers2 = {
                    "Content-Type": "application/json"
                    }              
                    r = requests.post('https://api.api.ai/v1/query?v=20150910',headers=headers, data=content)
                    if r:
                        send_json = r.json()
                        send_json['sender_id'] = sender_id
                        a = requests.get('https://graph.facebook.com/v2.10/'+sender_id,params=params2,headers=headers2)
                        if a:
                            send_json['first_name'] = a.json()['first_name']
                            send_json['last_name'] = a.json()['last_name']
                        r2 = requests.post('https://myfirstbot11.herokuapp.com/response/', json = send_json)

    return "ok", 200


@app.route('/response/', methods=['GET','POST'])
def response():

    client = MongoClient("mongodb://heroku_fkfhqw1w:mtkhac4bj08bu2qs02gm0i4s79@ds147964.mlab.com:47964/heroku_fkfhqw1w")
    computers = client["heroku_fkfhqw1w"].example_computers_table
    m = request.get_json()
    if m:
        if 'sender_id' in m:
            sender_id = m['sender_id']
            speech = ''

            if m['result']['action'] == 'input.welcome':
                speech = 'Bonjour '+m['first_name']+' '+m['last_name']+", je suis un bot créé par Nabil. J'ai été conçu pour vous aider à trouver votre ordinateur idéal. Quelle en sera votre utilisation ? Recherchez-vous un ordinateur fixe ou portable ?"
            
            indicators = m['result']['parameters']   
            weight_taille_ecran = 2.5
            weight_processeur = 2.5
            weight_RAM = 2.5
            weight_stockage = 2.5
            weight_carte_graphique = 2.5
            weight_prix = 2.5
            weight_poids = 2.5
            weight_autonomie = 2.5

            if 'developper' in indicators and indicators['developper'] != '':
                weight_RAM = 5
                weight_stockage = 5
                weight_processeur = 3
                weight_carte_graphique = 1

            if 'prix' in indicators and indicators['prix'] != '':
                weight_prix = 5
            else : 
                weight_prix = 2

            if 'game' in indicators and indicators['game'] != '':
                weight_processeur = 5
                weight_RAM = 3
                weight_stockage = 3
                weight_carte_graphique = 5
                
            if 'pc_fixe' in indicators and indicators['pc_fixe'] != '':
                weight_poids = 0
                weight_autonomie = 0
                weight_taille_ecran = 3
                find_pc_gamer = pd.DataFrame(list(computers.find({'type':'fixe'})))
                
            elif 'type' in indicators and indicators['type'] != '':
                weight_poids = 4
                weight_autonomie = 4
                weight_taille_ecran = 1
                find_pc_gamer = computers.find({'type':'portable'})
            else :
                find_pc_gamer = computers.find({})

            weights = [weight_taille_ecran,weight_processeur,weight_RAM,weight_stockage,weight_carte_graphique,weight_poids,weight_autonomie,weight_prix]

            d = find_pc_gamer[['ecran_taille (pouces)','processeur', 'RAM (Go)', 'stockage (To)', 'carte_graphique', 'poids (kg)','autonomie (h)', 'prix']]
            mins_criteria = [np.nansum(min(d[str(key)])) for key in d.keys()]
            maxs_criteria = [np.nansum(max(d[str(key)])) for key in d.keys()]
            utilities = d.apply(lambda x : calculate_utility(weights,list(x), mins_criteria, maxs_criteria), axis = 1)
            find_pc_gamer['global_utility'] = utilities
            name_best = find_pc_gamer[find_pc_gamer['global_utility'] == max(utilities)]['nom']
            name_best = list(name_best)
            list_names = name_best[0]
            for item in name_best[1:]:
                list_names += ', '+item
            if len(name_best) == 1:
                speech = "Humm..Je vois. J'ai l'ordinateur qu'il vous faut : "+list_names+" !"
            else : 
                speech = "Humm..Je vois. J'ai "+str(len(name_best))+" ordinateurs à vous proposer : "+list_names+" !" 

            response = {
            'speech': speech,
            'displayText' : speech,
            'data':None,
            'contextOut' : None,
            'source':'',
            'followupEvent' : None
            }
            send_message(sender_id, speech)

            return jsonify(response)
    return 'Empty request'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

