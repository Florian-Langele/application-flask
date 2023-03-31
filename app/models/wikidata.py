from ..app import app, db

classe_propriete = db.Table(
    "classe_propriete",
    db.Column('classe_id', db.Text, db.ForeignKey('classe.id'), primary_key=True),
    db.Column('propriete_id', db.Text, db.ForeignKey('propriete.id'), primary_key=True)
)

class Classe(db.Model):
    __tablename__ = "classe"

    id = db.Column(db.Text,primary_key=True)
    nom = db.Column(db.Text, nullable=False)

    proprietes = db.relationship("Propriete", secondary=classe_propriete, backref="proprietes")

    def __repr__(self):
        return '<Classe %r>' % (self.nom)

class Propriete(db.Model):
    __tablename__ = "propriete"

    id = db.Column(db.Text,primary_key=True)
    nom = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Propriete %r>' % (self.nom)