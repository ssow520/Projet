import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from datetime import datetime
from gestion_produit import Produit, Commande, Client


app = Flask(__name__)

# Define the base directory and set up the database URI
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_database.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
    return render_template('register.html', form=form)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different one")
        

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

# Route pour afficher les produits
@app.route('/products')
def products():
    """
    Affiche la liste des produits. Accessible uniquement pour les utilisateurs connectés.
    """
    products_list = Produit.get_all()  # Récupère tous les produits de la base de données
    return render_template('products.html', products=products_list)  # Affiche la page des produits

# Route pour ajouter un produit
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """
    Permet à un utilisateur connecté d'ajouter un nouveau produit.
    """
    if request.method == 'POST':
        nom = request.form['nom']
        prix = float(request.form['prix'])
        description = request.form['description']
        stock = int(request.form['stock'])
        type_produit = request.form['type']
        Produit.create(nom, prix, description, stock, type_produit)  # Création du produit dans la base de données
        flash('Produit ajouté avec succès!', 'success')
        return redirect(url_for('products'))  # Redirige vers la liste des produits après l'ajout
    
    return render_template('add_product.html')  # Affiche le formulaire d'ajout de produit

# Route pour modifier un produit
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """
    Permet de modifier un produit existant.
    """
    product = Produit.get_by_id(product_id)  # Récupère les détails du produit à modifier
    if request.method == 'POST':
        nom = request.form['nom']
        prix = float(request.form['prix'])
        description = request.form['description']
        stock = int(request.form['stock'])
        type_produit = request.form['type']
        Produit.update(product_id, nom, prix, description, stock, type_produit)  # Mise à jour du produit
        flash('Produit mis à jour avec succès!', 'success')
        return redirect(url_for('products'))  # Redirige vers la liste des produits
    
    return render_template('edit_product.html', product=product)  # Affiche le formulaire d'édition du produit

# Route pour supprimer un produit
@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    """
    Permet de supprimer un produit existant.
    """
    Produit.delete(product_id)  # Suppression du produit
    flash('Produit supprimé avec succès!', 'success')
    return redirect(url_for('products'))  # Redirige vers la liste des produits

# Route pour supprimer tous les produits
@app.route('/delete_all_products')
def delete_all_products():
    """
    Permet de supprimer tous les produits existants.
    """
    Produit.delete_all()  # Suppression de tous les produits
    flash('Tous les produits supprimés avec succès!', 'success')
    return redirect(url_for('products'))  # Redirige vers la liste des produits

# Route pour afficher les clients
@app.route('/clients')
def clients():
    """
    Affiche la liste des clients. Accessible uniquement pour les utilisateurs connectés.
    """
    clients_list = Client.get_all()  # Récupère tous les clients de la base de données
    return render_template('clients.html', clients=clients_list)  # Affiche la page des clients

# Route pour ajouter un client
@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        adresse = request.form['adresse']
        Client.create(nom, email, adresse)
        flash('Client ajouté avec succès!', 'success')
        return redirect(url_for('clients'))
    return render_template('add_client.html')

# Route pour modifier un client
@app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    client = Client.get_by_id(client_id)
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        adresse = request.form['adresse']
        Client.update(client_id, nom, email, adresse)
        flash('Client mis à jour avec succès!', 'success')
        return redirect(url_for('clients'))
    return render_template('edit_client.html', client=client)

# Route pour supprimer un client
@app.route('/delete_client/<int:client_id>')
def delete_client(client_id):
    Client.delete(client_id)
    flash('Client supprimé avec succès!', 'success')
    return redirect(url_for('clients'))

# Route pour supprimer tous les clients
@app.route('/delete_all_clients')
def delete_all_clients():
    """
    Permet de supprimer tous les clients existants.
    """
    Client.delete_all()  # Suppression de tous les clients
    flash('Tous les clients supprimés avec succès!', 'success')
    return redirect(url_for('clients'))  # Redirige vers la liste des clients

# Route pour afficher les commandes
@app.route('/orders')
def orders():
    orders_list = Commande.get_all()
    return render_template('orders.html', orders=orders_list)

# Route pour ajouter une commande
@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        client_id = int(request.form['client_id'])
        produit_id = int(request.form['produit_id'])
        quantite = int(request.form['quantite'])
        Commande.create(client_id, produit_id, quantite)
        flash('Commande ajoutée avec succès!', 'success')
        return redirect(url_for('orders'))
    clients_list = Client.get_all()
    products_list = Produit.get_all()
    return render_template('add_order.html', products=products_list, clients=clients_list)

# Route pour modifier une commande
@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    order = Commande.get_by_id(order_id)
    if request.method == 'POST':
        client_id = int(request.form['client_id'])
        produit_id = int(request.form['produit_id'])
        quantite = int(request.form['quantite'])
        Commande.update(order_id, client_id, produit_id, quantite)
        flash('Commande mise à jour avec succès!', 'success')
        return redirect(url_for('orders'))
    clients_list = Client.get_all()
    products_list = Produit.get_all()
    return render_template('edit_order.html', order=order, products=products_list, clients=clients_list)

# Route pour supprimer une commande
@app.route('/delete_order/<int:order_id>')
def delete_order(order_id):    
    Commande.delete(order_id)    
    flash('Commande supprimée avec succès!', 'success')    
    return redirect(url_for('orders'))    

# Route pour supprimer toutes les commandes
@app.route('/delete_all_orders')
def delete_all_orders():
    """
    Permet de supprimer toutes les commandes existantes.
    """
    Commande.delete_all()  # Suppression de toutes les commandes
    flash('Toutes les commandes supprimées avec succès!', 'success')
    return redirect(url_for('orders'))  # Redirige vers la liste des commandes   

if __name__ == '__main__':

    # Initialize the database by pushing the app context
    app.app_context().push()
    db.create_all()

    app.run(debug=True)