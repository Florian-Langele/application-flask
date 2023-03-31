from ..app import app
from flask_login import login_user, current_user, logout_user
from flask import render_template,request,flash, redirect, url_for
from ..models.formulaires import Connexion, Inscription
from ..models.users import Users

@app.route("/inscription", methods=["GET","POST"])
def inscription():
    form = Inscription()

    if current_user.is_authenticated:
        return redirect(url_for('recherche'))

    if form.validate_on_submit():
        statut,donnees = Users.ajout(request.form.get("nom",None),request.form.get("password",None),request.form.get("confirmation_password",None))
        if statut:
            login_user(donnees)
            return redirect(url_for("recherche"))
        else:
            flash(",".join(donnees), "error")
            print("Raté",donnees)
            return render_template("pages/inscription.html", form=form)
      
    return render_template("pages/inscription.html", form=form)

@app.route("/connexion", methods=["GET","POST"])
def connexion():
    form = Connexion()

    if current_user.is_authenticated:
        return redirect(url_for('recherche'))

    if form.validate_on_submit():
        utilisateur = Users.connexion(nom = request.form.get("nom", None), password = request.form.get("password", None))

        if utilisateur:
            flash("Connexion effectuée")
            login_user(utilisateur)
            return redirect(url_for('recherche'))
        else: 
            flash("Les identifiants n'ont pas été reconnus")
            return render_template("pages/connexion.html", form=form)
    else:
        return render_template("pages/connexion.html", form= form)

@app.route("/deconnexion", methods=["POST","GET"])
def deconnexion():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('recherche'))