
'''from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, IntegerField, TextAreaField, SubmitField, DecimalField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class AddProductForm(FlaskForm):
    nom = StringField('Nom du produit', validators=[DataRequired(), Length(max=50)])
    prix = DecimalField('Prix', validators=[DataRequired(), NumberRange(min=0)], places=2)
    description = TextAreaField('Description', validators=[Length(max=200)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    type_produit = SelectField('Type de produit', choices=[
        ('Fruits et légumes', 'Fruits et légumes'),
        ('Produits laitiers', 'Produits laitiers'),
        ('Viandes et protéines', 'Viandes et protéines'),
        ('Produits de boulangerie', 'Produits de boulangerie'),
        ('Céréales et grains', 'Céréales et grains'),
        ('Conserves et produits secs', 'Conserves et produits secs'),
        ('Condiments et épices', 'Condiments et épices'),
        ('Boissons', 'Boissons'),
        ('Produits surgelés', 'Produits surgelés'),
        ('Snacks et confiseries', 'Snacks et confiseries'),
        ('Produits non alimentaires', 'Produits non alimentaires')
    ], validators=[DataRequired()])
    submit = SubmitField('Ajouter')

class AddClientForm(FlaskForm):
    nom = StringField('Nom du client', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    adresse = StringField('Adresse')
    submit = SubmitField('Effectuer')'''

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, IntegerField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired, Length, NumberRange, Email

#-------------class add form produit------------
class AddProductForm(FlaskForm):
    nom = StringField('Nom du produit', validators=[DataRequired(), Length(max=50)])
    prix = DecimalField('Prix', validators=[DataRequired(), NumberRange(min=0)], places=2)
    description = TextAreaField('Description', validators=[Length(max=200)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    type_produit = SelectField('Type de produit', choices=[
        ('Fruits et légumes', 'Fruits et légumes'),
        ('Produits laitiers', 'Produits laitiers'),
        ('Viandes et protéines', 'Viandes et protéines'),
        ('Produits de boulangerie', 'Produits de boulangerie'),
        ('Céréales et grains', 'Céréales et grains'),
        ('Conserves et produits secs', 'Conserves et produits secs'),
        ('Condiments et épices', 'Condiments et épices'),
        ('Boissons', 'Boissons'),
        ('Produits surgelés', 'Produits surgelés'),
        ('Snacks et confiseries', 'Snacks et confiseries'),
        ('Produits non alimentaires', 'Produits non alimentaires')
    ], validators=[DataRequired()])
    submit = SubmitField('Effectuer')

#-------------class add form client------------

class AddClientForm(FlaskForm):
    nom = StringField('Nom du client', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    adresse = StringField('Adresse', validators=[DataRequired()])
    submit = SubmitField('Ajouter')

#-------------Edit Client------------

class EditClientForm(FlaskForm):
    nom = StringField('Nom du client', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    adresse = StringField('Adresse', validators=[DataRequired()])
    submit = SubmitField('Modifier')


#-------------class add form commande------------

class AddOrderForm(FlaskForm):
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    produit_id = SelectField('Produit', coerce=int, validators=[DataRequired()])
    quantite = IntegerField('Quantité', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Effectuer')




