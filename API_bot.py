 #!/usr/bin/env python
# -*- coding: utf-8 -*- 
from flask import jsonify, request, Flask
from flask import Request
import os
from pymongo import MongoClient
from bson.son import SON
from flask import Response

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
# def facebook_verification():
# 	c = request.args.getlist('hub.challenge')
# 	if len(c) > 0:
# 		challenge_token = c[0]
# 		return Response(challenge_token, status=200)
# 	return Response('ok', status=200)

@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id, "roger that!")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
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
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()

# def response():
# 	client = MongoClient("mongodb://heroku_fkfhqw1w:mtkhac4bj08bu2qs02gm0i4s79@ds147964.mlab.com:47964/heroku_fkfhqw1w")
# 	computers = client["heroku_fkfhqw1w"].computers
# 	m = request.get_json()
# 	print(m)
# 	indicators = m['result']['parameters']
# 	if 'game' in indicators:
# 		find_pc_gamer = computers.aggregate([{"$addFields":{'gamer_rate':{'$add' :['$processeur_rate','$carte_graphique_rate']}}},{'$sort':SON([("gamer_rate", -1)])}])
# 		best_computers = {}
# 		i = 0
# 		find_pc_gamer = list(find_pc_gamer)
# 		while find_pc_gamer[i]['gamer_rate'] == find_pc_gamer[0]['gamer_rate']:
# 			best_computers[i] = {}
# 			best_computers[i]['nom'] = find_pc_gamer[i]['nom']
# 			best_computers[i]['prix'] = find_pc_gamer[i]['prix']
# 			i = i+1
# 		print(best_computers)
# 		best_cheap = min(best_computers[k]['prix'] for k in range(len(best_computers.keys())))
# 		name_cheap = [best_computers[k]['nom'] for k in range(len(best_computers.keys())) if best_computers[k]['prix'] == best_cheap]
# 		speech = "Hum..Je vois. J'ai l'ordinateur qu'il vous faut : "+name_cheap[0]
# 		for word in name_cheap[1:]:
# 			speech += "," + word
# 		speech += "!"
# 		response = {
# 		'speech': speech,
# 		'displayText' : speech,
# 		'data':None,
# 		'contextOut' : None,
# 		'source':'',
# 		'followupEvent' : None
# 		}
# 		print(response)

# 	return jsonify(response)



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)

