from ..app import app
from flask import render_template, request, redirect, url_for, session, flash
from flask_login import login_required
from ..models.wikidata import Classe,Propriete
from ..models.formulaires import Recherche,Proprietes
import requests


@app.route("/", methods=["GET","POST"])
@login_required
def recherche():
    form = Recherche()

    choix_classes = []
    for classe in Classe.query.all():
        choix_classes.append((classe.id,classe.nom))
    form.classe.choices = choix_classes
    session["recherche"] = {}
    #Récupération des informations de bases
    
    if form.validate_on_submit():
        session['recherche'] = {
            'champs' : request.form.get("recherche",None),
            'classe' : request.form.get("classe",None),
            'langue' : request.form.get("langue",None),
            'nombre' : request.form.get("nombre",None)
        }
    #Première requête pour identifier les entités recherchées
        requete_sparql = "https://query.wikidata.org/bigdata/namespace/wdq/sparql?format=json&query="
        query = f"""SELECT DISTINCT ?objet ?objetLabel WHERE {{
                    ?classe wdt:P279* wd:{session['recherche']['classe']}.
                    ?objet wdt:P31 ?classe;
                    wdt:P625 ?coordonne;
                    rdfs:label ?objetLabel.
                    FILTER(lang(?objetLabel) = "{session['recherche']['langue']}").
                    FILTER regex(?objetLabel,".*{session['recherche']['champs']}.*", "i").
                }} LIMIT {session['recherche']['nombre']}"""
        resultat_requete = requests.get(requete_sparql+query).json()
        
    #Création de la liste qui récupère les informations et indique les noms et les identifiants, puis ajout dans la session
        resultat_final = []
        for entite in resultat_requete["results"]["bindings"]:
            resultat_final.append({
                    "id" : entite["objet"]["value"].split("/")[-1],
                    "label" : entite["objetLabel"]["value"]
            })
        session['recherche']['liste_entite'] = resultat_final

        #Prévention pour éviter les erreurs on ne peut pas aller plus loin si il n'y a pas de résultat
        if session['recherche']['liste_entite'] == []:
            flash("Votre recherche n'a rien trouvé")
            
            return redirect(url_for('recherche'))

        return redirect(url_for('resultat')) 

    session["recherche"].clear()

    return render_template("pages/recherche.html",form=form)

@app.route("/resultat", methods=["GET","POST"])
@login_required
def resultat():

    #Récupération des propriétés associés à la classe choisie pour le prochain formulaire
    form = Proprietes()
    choix_proprietes = []
    for propriete in Classe.query.filter(Classe.id==session['recherche']['classe']).first().proprietes:
        choix_proprietes.append((propriete.id,propriete.nom))
    form.proprietes.choices = choix_proprietes

    if form.validate_on_submit():
        #Récupération dans la session des propriétés choisies par l'utilisateur
        session["recherche"]["proprietes"] = request.form.getlist("proprietes",None)
        
        if len(session['recherche']['proprietes']) == 0:
            flash("Merci de sélectionner au moins une propriété dans la liste")
            return render_template('pages/resultat.html',resultat=session['recherche']['liste_entite'],form = form)

        session["recherche"]["proprietes"].append("P625")
        #Création de la requête pour aller chercher les valeurs attachées à ces propriétés pour chaque entité
        entites = '|'.join(entite['id'] for entite in session['recherche']['liste_entite'])
        requete = "https://www.wikidata.org/w/api.php?action=wbgetentities&languages=%s&languagefallback=%s&ids=%s&props=claims&format=json" % (session['recherche']['langue'], session['recherche']['langue'],entites)
        resultat = requests.get(requete).json()
        if resultat['success'] != 1 :
                return "Problème du serveur wikidata"
        resultat = resultat['entities']

        #On garde ici uniquement les propriétés qui avaient été choisies sous forme de tuple avec premier élément la propriété, deuxième élément son datatype et troisième la valeur associée
        proprietes = {}
        for entite in resultat:
            proprietes[entite] = []
            for chaque_propriete in resultat[entite]['claims']:
                if chaque_propriete in session['recherche']['proprietes']:
                    for value in resultat[entite]['claims'][chaque_propriete]:
                        proprietes[entite].append((chaque_propriete,value['mainsnak']['datatype'],value['mainsnak']['datavalue']))

        
        #On range dans session
        for entite in session['recherche']['liste_entite']:
            entite['propriete'] = proprietes[entite['id']]

        label_propriete = {}
        
        #Ajout des labels des différentes propriétés contenues dans la BDD
        for propriete in session['recherche']['proprietes']:
            if propriete == "P625":
                label_propriete[propriete] = "coordonnées"
            else:
                label_propriete[propriete] = Propriete.query.filter(Propriete.id == propriete).first().nom
        session['recherche']['proprietes'] = label_propriete

        
        #es fois les valeurs associés aux propriétés sont d'autres entités, on les récupère
        entites=[]
        for entite in proprietes:
            for propriete in proprietes[entite]:
                if propriete[1] == 'wikibase-item':
                    entites.append(propriete[2]['value']['id'])
        
        #Je supprime les doublons
        entites = '|'.join(list(set(entites)))

        #Requête pour récupérer les labels associés aux entités juste au dessus
        requete = "https://www.wikidata.org/w/api.php?action=wbgetentities&languages=%s&languagefallback=%s&ids=%s&props=labels&format=json" % (session['recherche']['langue'], session['recherche']['langue'],entites)    
        resultat = requests.get(requete).json()
        if resultat['success'] != 1 :
                return "Problème du serveur wikidata"
        resultat = resultat['entities']

        #On modifie la valeur associé aux propriétés qui était des identifiants par les labels de ceux ci, on en profite pour faire remonter l'info des coordonnées et normalisé les autres types de données
        for entite in session['recherche']['liste_entite']:
            for propriete in entite['propriete']:
                if propriete[1] == 'wikibase-item' and propriete[2]['value']['id'] in resultat.keys():
                    propriete[2]['value'] = resultat[propriete[2]['value']['id']]['labels'][session['recherche']['langue']]['value']
                elif propriete[1] == 'globe-coordinate':
                    entite['coordonnees'] = [propriete[2]['value']['latitude'],propriete[2]['value']['longitude']]
                elif propriete[1] == 'time':
                    temps = propriete[2]['value']['time'][1:10]
                    propriete[2]['value'] = ' '.join(str(int(date)) if int(date) != 0 else '' for date in reversed(temps.split('-')))


        session["recherche"]['proprietes'].pop('P625')
        return render_template('pages/recap.html',donnees = session['recherche'])

    return render_template('pages/resultat.html',resultat=session['recherche']['liste_entite'],form = form)