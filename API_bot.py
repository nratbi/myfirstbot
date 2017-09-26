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

#Fonction de calcul de l'éspérence d'utilité pour un ordinateur donné
def calculate_utility(weights, vector, mins_criteria, maxs_criteria, sign_utility):
    utility_vector = [0]*len(vector)
    for i in range(len(vector)):
        if sign_utility[i] == 1:
            utility_vector[i] = (weights[i]/sum(weights))*(vector[i]-mins_criteria[i])/(maxs_criteria[i]-mins_criteria[i])
        else : 
            utility_vector[i] = (weights[i]/sum(weights))*(maxs_criteria[i] - vector[i])/(maxs_criteria[i]-mins_criteria[i])
    utility = np.nansum(utility_vector)
    return utility

#Fonction permettant d'envoyer un message au user
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
#Verification lors de l'enregistrement webhook, retourne la valeur 'hub.challenge' reçue
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "ok", 200

@app.route('/', methods=['POST'])
#Traitement des messages arrivants
def webhook():
    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # quelqu'un a envoyé un message
                    sender_id = messaging_event["sender"]["id"]        # le facebook ID de l'émetteur
                    recipient_id = messaging_event["recipient"]["id"]  # l'ID du récépteur, en l'occurrence mon ID
                    message_text = messaging_event["message"]["text"]  # le contenu du message

                    #requête vers API.ai pour récupérer l'action et les paramètres nécessaires
                    headers = {
                    "Content-Type": "application/json",
                    "Authorization" : "Bearer 4c6588d427284768823a5520af36c901"
                    }
                    content = json.dumps({
                    "query": message_text,
                    "timezone": "Europe/Paris",
                    "lang": "fr",
                    "sessionId": "599fd47b-0f04-4e10-a488-cb9803ba538f"
                    })
                    params2 = {
                    "access_token": "EAAXFoXg4V2oBANtEWids8btXLLN3xMfu2xkZBoaQqwmkSZCheKJZCbZABG8Cmb1hamD0ZCZAK5DZCLYQmU2eXnsGB6pAJ3TZATvFjGczUeCwEsJvFXJujrw7DtF9CZBwPk9tixFUJ134Fj5HrgMtBOlw8KnHsst46IjTB5kv4XolZB9QZDZD"
                    }
                    headers2 = {
                    "Content-Type": "application/json"
                    }              
                    r = requests.post('https://api.api.ai/v1/query?v=20150910',headers=headers, data=content)
                    print(r.content)
                    if r:
                        send_json = r.json()
                        send_json['sender_id'] = sender_id #ajout de l'ID de l'émetteur pour lui envoyer la réponse après traitement
                        #requête pour récupérer le prénom et le nom de l'émetteur
                        a = requests.get('https://graph.facebook.com/v2.10/'+sender_id,params=params2,headers=headers2)
                        print(a.content)
                        if a:
                            send_json['first_name'] = a.json()['first_name'] # ajout du prénom
                            send_json['last_name'] = a.json()['last_name'] #ajout du nom
                        #requête pour la préparation et l'envoi de la réponse
                        r2 = requests.post('https://myfirstbot11.herokuapp.com/response/', json = send_json)

    return "ok", 200


@app.route('/response/', methods=['GET','POST'])
def response():

    #connexion à la base de données MongoDB
    client = MongoClient("mongodb://heroku_fkfhqw1w:mtkhac4bj08bu2qs02gm0i4s79@ds147964.mlab.com:47964/heroku_fkfhqw1w")
    computers = client["heroku_fkfhqw1w"].example_computers_table # accès à la table contenant les données sur les ordinateurs
    m = request.get_json() #récupération du contenu de la requête reçue
    if m:
        if 'sender_id' in m:
            sender_id = m['sender_id']
            speech = ''
            #si message de bienvenue
            if m['result']['action'] == 'input.welcome':
                speech = 'Bonjour '+m['first_name']+' '+m['last_name']+", je suis un bot créé par Nabil. J'ai été conçu pour vous aider à trouver votre ordinateur idéal. Quelle en sera votre utilisation ? Recherchez-vous un ordinateur fixe ou portable ?"
            
            #si Fallback
            elif m['result']['action'] == 'input.unknown':
                speech = "Je n'ai pas saisi ce que tu as dit."

            else :

                #accès aux paramètres du message (cf API.ai)
                indicators = m['result']['parameters'] 

                #initialisation neutre des poids à affecter aux caractéristiques des machines : par défaut choix de 2.5 car valeur moyenne (max à 5)
                weight_taille_ecran = 2.5
                weight_processeur = 2.5
                weight_RAM = 2.5
                weight_stockage = 2.5
                weight_carte_graphique = 2.5
                weight_prix = 2.5
                weight_poids = 2.5
                weight_autonomie = 2.5

                #Cas du développeur
                if 'developper' in indicators and indicators['developper'] != '':
                    weight_RAM = 5 #formulation explicite du besoin de beaucoup de RAM => poids max = 5
                    weight_stockage = 5 #de même, formulation explicite => poids max = 5
                    weight_processeur = 2.5 #aucune formulation, mais critère intéressant => poids moyen = 2.5
                    weight_carte_graphique = 1 #sans grand intérêt vu le profil => poids min = 1

                if 'prix' in indicators and indicators['prix'] != '':
                    weight_prix = 5 #si formulation du besoin d'un ordinateur pas cher => poids max = 5
                else : 
                    weight_prix = 2.5   
                #Il peut y avoir un troisième cas où l'individu est financièrement aisé (par exemple ici c'est le cas : ingénieur) 
                # auquel cas on aurait un poids négligeable mais par soucis de simplification on ne considérera pas ce cas ici

                #Cas du gamer
                if 'game' in indicators and indicators['game'] != '':
                    weight_processeur = 5 #formulation explicite + profil gamer => poids max = 5
                    weight_RAM = 3 #intéressant mais pas de formulation explicite 
                    weight_stockage = 3 #critère intéressant si l'individu doit installer des jeux volumineux mais pas de formulation explicite 
                    weight_carte_graphique = 5 #formulation explicite + profil gamer => poids max = 5
                    
                #Cas ordinateur de bureau
                if 'pc_fixe' in indicators and indicators['pc_fixe'] != '':
                    weight_poids = 0 #aucun intérêt car pc fixe => poids nul
                    weight_autonomie = 0 #aucun intérêt car pc fixe => poids nul
                    weight_taille_ecran = 4 #les ordinateurs de bureau sont généralement préférés avec de grands écrans  => poids  = 4
                    find_pc_gamer = pd.DataFrame(list(computers.find({'type':'fixe'}))) #filtrage présélectif en ne gardant que les ordinateurs fixes présents dans la base
                    d = find_pc_gamer[['ecran_taille (pouces)','processeur', 'RAM (Go)', 'stockage (To)', 'carte_graphique', 'poids (kg)','autonomie (h)', 'prix']]
                    sign_utility = [1,1,1,1,1,-1,1,-1] # liste permettant de distinguer les préférences croissantes et décroissantes
                
                #Cas ordinateur fixe
                if 'type' in indicators and indicators['type'] != '':
                    weight_poids = 4 #très intéressant pour les laptop => poids = 4
                    weight_autonomie = 4 #très intéressant pour les laptop => poids = 4
                    weight_taille_ecran = 4 #les ordinateurs portables sont généralement préférés avec de petits écrans  => poids  = 4
                    find_pc_gamer = pd.DataFrame(list(computers.find({'type':'portable'}))) #filtrage présélectif en ne gardant que les ordinateurs portables présents dans la base
                    d = find_pc_gamer[['ecran_taille (pouces)','processeur', 'RAM (Go)', 'stockage (To)', 'carte_graphique', 'poids (kg)','autonomie (h)', 'prix']]
                    sign_utility = [-1,1,1,1,1,-1,1,-1] #liste permettant de distinguer les préférences croissantes et décroissantes

                weights = [weight_taille_ecran,weight_processeur,weight_RAM,weight_stockage,weight_carte_graphique,weight_poids,weight_autonomie,weight_prix] #liste contenant les poids pour les différentes variables

                mins_criteria = [np.nansum(min(d[str(key)])) for key in d.keys()] #liste avec la plus petite valeur prise par chaque critère
                maxs_criteria = [np.nansum(max(d[str(key)])) for key in d.keys()] #liste avec la plus grande valeur prise par chaque critère
                utilities = d.apply(lambda x : calculate_utility(weights,list(x), mins_criteria, maxs_criteria, sign_utility), axis = 1) #calcul de l'espérance d'utilié pour toutes les machines retenues
                find_pc_gamer['global_utility'] = utilities #ajout d'une colonne avec les scores d'utilité globaux
                print(find_pc_gamer) 
                name_best = find_pc_gamer[find_pc_gamer['global_utility'] == max(utilities)]['nom'] #récupération des noms des machines avec l'espérance d'utilité la plus élevée
                name_best = list(name_best)
                list_names = name_best[0]
                for item in name_best[1:]:
                    list_names += ', '+item

                #si un seul ordinateur
                if len(name_best) == 1:
                    speech = "Humm..Je vois. J'ai l'ordinateur qu'il vous faut : "+list_names+" !"
                #si plusieurs ordinateurs
                else : 
                    speech = "Humm..Je vois. J'ai "+str(len(name_best))+" ordinateurs à vous proposer : "+list_names+" !" 

            #envoi réponse lorsqu'un test est effectué sur API.ai (aucun rapport avec messenger)
            response = {
            'speech': speech,
            'displayText' : speech,
            'data':None,
            'contextOut' : None,
            'source':'',
            'followupEvent' : None
            }

            #envoi du message de réponse
            send_message(sender_id, speech)

            return jsonify(response)
    return 'Empty request'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

