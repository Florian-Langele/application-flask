from ..app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin



class Users(UserMixin, db.Model):

    """
Une classe utilisée pour la gestion des utilisateurs.

Attributes 
---------
id : sqlalchemy.sql.schema.Column
        Identifiant de l'utilisateur. C'est la clé primaire. Cet attribut est une Column SQLALchemy.
nom : sqlalchemy.sql.schema.Column
        Nom de l'utilisateur
password : sqlalchemy.sql.schema.Column
        Mot de passé hashé de l'utilisateur

"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<User %r>" %(self.nom)
    
    def get_id(self):
        return self.id
    
    @login.user_loader
    def get_user_by_id(id):
        return Users.query.get(int(id))

    @staticmethod
    def connexion(nom, password):
        utilisateur = Users.query.filter(Users.nom == nom).first()
        if utilisateur and check_password_hash(utilisateur.password,password):
            return utilisateur
        return None

    @staticmethod
    def ajout(nom:str, password:str, confirmation_password:str):
        erreurs = []
        if password != confirmation_password:
            erreurs.append("Les deux mots de passes ne sont pas identiques.")
        if not nom:
            erreurs.append("Le nom d'utilisateur est vide.")
        if not password or len(password) < 6:
            erreurs.append("Le mot de passe est vide ou trop court. (6 caractères mini)")
        unique = Users.query.filter( Users.nom == nom).count()
        if unique > 0 :
            erreurs.append("Un compte est déjà associé à ce prénom.")
        if len(erreurs) > 0 :
            return False, erreurs
        utilisateur = Users(nom=nom, password = generate_password_hash(password))
        
        try:
            db.session.add(utilisateur)
            db.session.commit()
            return True, utilisateur
        except Exception as erreur:
            db.session.rollback()
            return False, [str(erreur)]