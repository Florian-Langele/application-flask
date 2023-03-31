from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, TextAreaField,PasswordField
from .wikidata import Classe

class Connexion(FlaskForm):
    nom = StringField("nom", validators=[])
    password = PasswordField("password", validators=[])

class Inscription(FlaskForm):
    nom = StringField("nom", validators=[])
    password = PasswordField("password", validators=[])
    confirmation_password = StringField("confirmation_password", validators=[])

class Recherche(FlaskForm):
    recherche = StringField("nom", validators=[])
    classe = SelectField("classe", validators=[])
    langue = SelectField("langue", choices = [("fr","Français"),("en","English")])
    nombre = SelectField("nombre",choices = [(str(a),str(a)) for a in range(1,11)])

class Proprietes(FlaskForm):
    proprietes = SelectMultipleField("proprietes")