import os
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import tkinter
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from datetime import datetime
from gestion_produit import Produit, Commande, Client
from forms import AddProductForm, AddClientForm


app = Flask(__name__)

# Définir les couleurs principales pour les graphiques
plt.style.use('default')
plt.rcParams['axes.prop_cycle'] = plt.cycler('color', ['#3498db', '#8e44ad'])  # bleu et violet

# Define the base directory and set up the database URI
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

# Définition du modèle Produit avec le champ type_produit
class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    stock = db.Column(db.Integer, nullable=False)
    type_produit = db.Column(db.String(100), nullable=False)

# Définition du modèle Client
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    adresse = db.Column(db.String(200))

    def __repr__(self):
        return f'<Client {self.nom}>'
    
# Définition du modèle Commande
class Commande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produit.id'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    date_commande = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship('Client', backref=db.backref('commandes', lazy=True))
    produit = db.relationship('Produit', backref=db.backref('commandes', lazy=True))

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


@app.route('/add_produit', methods=['GET', 'POST'])
def add_produit():
    form = AddProductForm()  # Créez une instance du formulaire

    if form.validate_on_submit():  # Si le formulaire est soumis et valide
        # Récupérez les données du formulaire
        product_name = form.nom.data
        product_price = form.prix.data
        product_description = form.description.data
        product_stock = form.stock.data
        product_type = form.type_produit.data

        # Ajoutez le produit à la base de données
        new_product = Produit(
            nom=product_name,
            prix=product_price,
            description=product_description,
            stock=product_stock,
            type_produit=product_type
        )
        db.session.add(new_product)
        db.session.commit()

        #flash(f"Produit ajouté avec succès : {product_name} - {product_price}", "success")

        return redirect(url_for('produits'))  # Redirigez vers la liste des produits

    return render_template('add_product.html', form=form)  # Affichez le formulaire pour GET

@app.route('/edit_produit/<int:produit_id>', methods=['GET', 'POST'])
def edit_produit(produit_id):
    produit = Produit.query.get_or_404(produit_id)
    form = AddProductForm()  # Formulaire pour l'édition du produit

    if form.validate_on_submit():
        # Mise à jour des informations du produit
        produit.nom = form.nom.data
        produit.prix = form.prix.data
        produit.description = form.description.data
        produit.stock = form.stock.data
        produit.type_produit = form.type_produit.data  # Assurez-vous que le formulaire contient ce champ

        db.session.commit()  # Enregistrer les modifications dans la base de données
        flash("Produit mis à jour avec succès", "success")
        return redirect(url_for('produits'))  # Rediriger vers la liste des produits après la modification

    # Pré-remplir le formulaire avec les données actuelles du produit
    form.nom.data = produit.nom
    form.prix.data = produit.prix
    form.description.data = produit.description
    form.stock.data = produit.stock
    form.type_produit.data = produit.type_produit  # Pré-remplir le type de produit

    return render_template('edit_product.html', form=form, produit=produit)

@app.route('/delete_produit/<int:produit_id>', methods=['POST'])
def delete_produit(produit_id):
    produit = Produit.query.get_or_404(produit_id)
    db.session.delete(produit)
    db.session.commit()
    flash("Produit supprimé avec succès", "success")
    return redirect(url_for('produits'))  # Rediriger vers la liste des produits après suppression


@app.route('/produits', methods=['GET'])
def produits():
    # Récupérez tous les produits de la base de données
    all_produits = Produit.query.all()
    return render_template('produits.html', produits=all_produits)
    # Routes pour les produits



@app.route('/add_produit', methods=['GET'])
def form_add_produit():
    return render_template('add_product.html')  # Formulaire pour ajouter un produit

@app.route('/clients')
def list_clients():
    clients = Client.query.all()  # Récupérer les clients depuis la base de données
    return render_template('clients.html', clients=clients)

@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    form = AddClientForm()
    if form.validate_on_submit():
        # Ajouter un client dans la base de données
        new_client = Client(
            nom=form.nom.data,
            email=form.email.data,
            adresse=form.adresse.data
        )
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('list_clients'))  # Rediriger vers la page des clients
    return render_template('add_client.html', form=form)


@app.route('/delete_client/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    # Trouver le client à supprimer
    client = Client.query.get_or_404(client_id)
    
    # Supprimer le client de la base de données
    db.session.delete(client)
    db.session.commit()
    
    flash("Client supprimé avec succès!", "danger")
    return redirect(url_for('list_clients'))  # Rediriger vers la page des clients

@app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)  # Récupère le client par ID
    form = AddClientForm(obj=client)
    
    if form.validate_on_submit():
        client.nom = form.nom.data
        client.email = form.email.data
        client.adresse = form.adresse.data
        db.session.commit()
        return redirect(url_for('list_clients'))  # Rediriger après la mise à jour

    return render_template('edit_client.html', form=form, client=client)


@app.route('/commandes', methods=['GET'])
def liste_commandes():
    commandes = Commande.query.all()
    clients = Client.query.all()
    produits = Produit.query.all()
    return render_template('orders.html', orders=commandes, clients=clients, produits=produits)

@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    clients = Client.query.all()
    produits = Produit.query.all()
    if not clients or not produits:
        flash('Impossible d\'ajouter une commande : il n\'y a pas de clients ou de produits disponibles.')
        return render_template('add_order.html', clients=clients, produits=produits)
    
    if request.method == 'POST':
        client_id = request.form['client']
        produit_id = request.form['produit']
        quantite = int(request.form['quantite'])
        
        produit = Produit.query.get(produit_id)
        
        # Vérifier que la quantité demandée est disponible
        if quantite > produit.stock:
            flash('Quantité demandée supérieure à la quantité disponible.')
            return redirect(url_for('add_order'))
        
        # Créer une nouvelle commande
        commande = Commande(client_id=client_id, produit_id=produit_id, quantite=quantite)
        db.session.add(commande)
        
        # Mettre à jour la quantité du produit
        produit.stock -= quantite
        db.session.commit()
        
        flash('Commande ajoutée avec succès.')
        return redirect(url_for('liste_commandes'))
    
    return render_template('add_order.html', clients=clients, produits=produits)

@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    order = Commande.query.get_or_404(order_id)
    clients = Client.query.all()
    produits = Produit.query.all()
    
    if request.method == 'POST':
        client_id = request.form['client']
        produit_id = request.form['produit']
        quantite = int(request.form['quantite'])
        
        produit = Produit.query.get(produit_id)
        
        if quantite > produit.stock:
            flash('Quantité demandée supérieure à la quantité disponible.')
            return redirect(url_for('edit_order', order_id=order_id))
        
        order.client_id = client_id
        order.produit_id = produit_id
        order.stock = quantite
        db.session.commit()
        
        flash('Commande mise à jour avec succès.')
        return redirect(url_for('liste_commandes'))
    
    return render_template('edit_order.html', order=order, clients=clients, produits=produits)
# Route pour supprimer une commande
@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    # Récupérer la commande à supprimer par son ID, ou renvoyer une erreur 404 si elle n'existe pas
    order = Commande.query.get_or_404(order_id)
    
    # Récupérer le produit associé à la commande
    produit = order.produit
    
    # Ajuster le stock du produit en fonction de la quantité de la commande
    produit.stock += order.quantite  # Ajouter la quantité de la commande au stock du produit
    
    # Supprimer la commande de la base de données
    db.session.delete(order)
    db.session.commit()  # Appliquer les changements à la base de données
    
    # Afficher un message flash pour informer l'utilisateur du succès
    flash('Commande supprimée avec succès.', 'success')
    
    # Rediriger vers la page listant les commandes après suppression
    return redirect(url_for('liste_commandes'))

def generate_pie_chart():
    # Connexion à la base de données
    conn = sqlite3.connect('app_database.db')
    cursor = conn.cursor()

    # Requête pour récupérer les données des types de produits
    cursor.execute('SELECT type_produit, COUNT(*) FROM produits GROUP BY type_produit')
    rows = cursor.fetchall()

    # Vérifier si les données existent
    if not rows:
        print("Aucune donnée trouvée pour le graphique.")
        return

    # Extraire les types de produits et leurs comptes
    types = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    # Afficher les données pour débogage
    print("Types de produits :", types)
    print("Comptes :", counts)

    # Créer le graphique circulaire
    plt.figure(figsize=(8, 6))  # Taille du graphique
    plt.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Assurer que le graphique est un cercle
    plt.title('Répartition des Produits par Type')

    # Sauvegarder le graphique dans un fichier
    plt.savefig('static/product_share.png', transparent=True)
    plt.close()

    # Fermer la connexion à la base de données
    conn.close()

def generate_category_bar_chart():
    # Connexion à la base de données
    conn = sqlite3.connect('app_database.db')
    cursor = conn.cursor()

    # Requête pour récupérer les données des catégories
    cursor.execute('SELECT stock, COUNT(*) FROM produits GROUP BY stock ORDER BY COUNT(*) DESC LIMIT 5')
    rows = cursor.fetchall()

    # Extraire les noms de catégories et les comptes
    categories = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    # Créer le graphique en barres
    plt.bar(categories, counts)
    plt.xlabel('Catégorie')
    plt.ylabel('Nombre de Produits')
    plt.title('Top 5 des Catégories par Nombre de Produits')

    # Sauvegarder le graphique dans un fichier
    plt.savefig('static/category_bar_chart.png', transparent=True)
    plt.close()

def generate_price_histogram():
    # Connexion à la base de données
    conn = sqlite3.connect('app_database.db')
    cursor = conn.cursor()

    # Requête pour récupérer les données de prix
    cursor.execute('SELECT prix FROM produits')
    rows = cursor.fetchall()

    # Extraire les valeurs des prix
    prices = [row[0] for row in rows]

    # Créer l'histogramme
    plt.hist(prices, bins=50)
    plt.xlabel('Prix')
    plt.ylabel('Fréquence')
    plt.title('Répartition des Prix des Produits')

    # Sauvegarder le graphique dans un fichier
    plt.savefig('static/price_histogram.png', transparent=True)
    plt.close()

@app.route('/graph')
def graph():
    # Générer les graphiques à chaque chargement de la page
    generate_pie_chart()
    generate_category_bar_chart()
    generate_price_histogram()

    # Rendre la page avec les graphiques
    return render_template('graph.html')




@app.route('/static/<path:filename>')
def send_file(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':

    # Initialize the database by pushing the app context
    app.app_context().push()
    db.create_all()

    app.run(debug=True)