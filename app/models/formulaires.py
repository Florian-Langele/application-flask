from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, TextAreaField,PasswordField
from .wikidata import Classe



class Connexion(FlaskForm):

    """
Une classe utilisée pour les données du formulaire de connexion de l'utilisateur

Attributes 
---------
nom : c'est l'identifiant de connexion de l'utilisateur, c'est une chaine de caractères.

password : c'est le mot de passe que doit rentrer l'utilisateur, il n'est pas visualisable dans le formulaire.

"""

    nom = StringField("nom", validators=[])
    password = PasswordField("password", validators=[])



class Inscription(FlaskForm):

    """
Une classe utilisée pour les données du formulaire de l'inscription de l'utilisateur

Attributes 
---------
nom : c'est l'identifiant de connexion de l'utilisateur, c'est une chaine de caractères.

password : c'est le mot de passe que doit rentrer l'utilisateur, il n'est pas visualisable dans le formulaire.

confirmation_password : l'utilisateur doit confirmer son mot de passe, il n'est pas visualisable dans le formualire.

"""

    nom = StringField("nom", validators=[])
    password = PasswordField("password", validators=[])
    confirmation_password = PasswordField("confirmation_password", validators=[])



class Recherche(FlaskForm):

    """
Une classe utilisée pour les données du formulaire de recherche.

Attributes 
---------
recherche : le texte recherché.

classe : le type de classe que doit chercher la requete SPARQL.

langue : choix à faire entre français et anglais.

nommbre : nombre de résultats maximum.

"""

    recherche = StringField("nom", validators=[])
    classe = SelectField("classe", validators=[])
    langue = SelectField("langue", choices = [("fr","Français"),("en","English")])
    nombre = SelectField("nombre",choices = [(str(a),str(a)) for a in range(1,10)])



class Proprietes(FlaskForm):

    """
Une classe utilisée pour les données du formulaire des proprietes associées aux entités.

Attributes 
---------
proprietes : on peut choisir entre les différentes propriétés. Elles sont dans la base de données.

"""
    proprietes = SelectMultipleField("proprietes")