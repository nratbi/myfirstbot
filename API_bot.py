 #!/usr/bin/env python
# -*- coding: utf-8 -*- 
from flask import jsonify, request, Flask
from flask import Request
import os
from pymongo import MongoClient
from bson.son import SON
from flask import Response
import sys
import json
import requests

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
                    r = requests.post('https://api.api.ai/v1/query?v=20150910',headers=headers, data=content)
                    if r:
                        r2 = requests.post('https://myfirstbot11.herokuapp.com/response/', json = r.json())
                        print(r2.content)
                    send_message(sender_id, "roger that!")

    return "ok", 200


@app.route('/response', methods=['GET,POST'])
def response():
    client = MongoClient("mongodb://heroku_fkfhqw1w:mtkhac4bj08bu2qs02gm0i4s79@ds147964.mlab.com:47964/heroku_fkfhqw1w")
    computers = client["heroku_fkfhqw1w"].computers
    m = request.get_json()
    print('**************')
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
        # send_message(recipient_id, speech)

    return jsonify(response)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

