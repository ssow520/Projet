'''
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

    app.run(debug=True)'''

from flask import Flask, render_template, redirect, url_for, flash,session, current_app
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')
#from flask_bcrypt import Bcrypt
#from flask_login import UserMixin
from gestion_produit import Produit, Client, Commande
from forms import AddProductForm, AddClientForm, AddOrderForm, EditClientForm
import matplotlib.pyplot as plt
#from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_database.db'  # Chemin vers ta base de données SQLite des tables 
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Désactive les notifications inutiles

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # Chemin vers ta base de données SQLite des utilisateurs
db = SQLAlchemy(app)

#------------------------Classe, Methodes et Routes pour accéder au site------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class RegisterForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('S\'inscrire')

class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Connexion')

def create_database():
    with sqlite3.connect('users.db') as connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            );
        """)
        connection.commit()

def create_user(username, password):
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

def check_login(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return True
    return False

@app.route('/')
def index():
    user = session.get('user')
    if user:
        return render_template('index.html', user=user)
    else:
        return render_template('index.html', user=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        create_user(username, password)
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if check_login(username, password):
            user = {'username': username}
            session['user'] = user
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', form=form, error='Nom d\'utilisateur ou mot de passe incorrect')
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    if user:
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


#------------------------Routes pour accéder au site------------------------

'''class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError("That username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")
    
# Initialisation de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Spécifie la vue de connexion

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)'''


# ----------------------- Routes pour les Produits -----------------------

'''# Ajouter un produit
@app.route('/add_produit', methods=['GET', 'POST'])
def add_produit():
    form = AddProductForm()
    if form.validate_on_submit():
        produit = Produit(
            nom=form.nom.data,
            prix=form.prix.data,
            description=form.description.data,
            stock=form.stock.data,
            type_produit=form.type_produit.data
        )
        produit.add_product()
        #flash('Produit ajouté avec succès !', 'success')
        return redirect(url_for('list_produits'))
    return render_template('add_product.html', form=form)

# Modifier un produit
@app.route('/edit_produit/<int:produit_id>', methods=['GET', 'POST'])
def edit_produit(produit_id):
    produit = Produit()
    produits = produit.get_products()
    produit_specifique = next((p for p in produits if p[0] == produit_id), None)
    
    if produit_specifique is None:
        # Gérer le cas où le produit n'est pas trouvé
        return "Produit non trouvé"
    
    # Utiliser les informations du produit spécifique
    form = AddProductForm()
    
    if form.validate_on_submit():
        # Mise à jour des informations du produit
        produit.update_product(produit_id, form.nom.data, float(form.prix.data), form.description.data, form.stock.data, form.type_produit.data)
        #flash("Produit mis à jour avec succès", "success")
        return redirect(url_for('list_produits'))  # Rediriger vers la liste des produits après la modification

    # Pré-remplir le formulaire avec les données actuelles du produit
    form.nom.data = produit_specifique[1]
    form.prix.data = Decimal(produit_specifique[2])
    form.description.data = produit_specifique[3]
    form.stock.data = produit_specifique[4]
    form.type_produit.data = produit_specifique[5]

    return render_template('edit_product.html', form=form, produit=produit_specifique)

# Supprimer un produit
@app.route('/delete_produit/<int:produit_id>', methods=['POST'])
def delete_produit(produit_id):
    produit = Produit()
    produit.delete_product(produit_id)
    #flash('Produit supprimé avec succès !', 'danger')
    return redirect(url_for('list_produits'))

# Afficher la liste des produits
@app.route('/list_produits', methods=['GET'])
def list_produits():
    produit = Produit()
    produits = produit.get_products()
    products_dict = [{'id': produit[0], 'nom': produit[1], 'prix': produit[2], 'description': produit[3], 'stock': produit[4], 'type_produit': produit[5]} for produit in produits]
    return render_template('list_produits.html', produits=products_dict)'''


# Route pour ajouter un nouveau produit
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        # Créer un nouvel objet Produit avec les données du formulaire
        new_produit = Produit(
            nom=form.nom.data,
            prix=form.prix.data,
            description=form.description.data,
            stock=form.stock.data,
            type_produit=form.type_produit.data
        )
        new_produit.add_product()  # Appeler la méthode pour ajouter le produit dans la base de données
        #flash('Produit ajouté avec succès!', 'success')
        return redirect(url_for('list_produits'))

    return render_template('add_product.html', form=form)


# Route pour modifier un produit
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    produit = Produit()  # Créer une instance de la classe Produit
    produit_to_update = next((p for p in produit.get_products() if p.id == id), None)  # Trouver le produit à modifier
    
    if produit_to_update is None:
        flash('Produit non trouvé', 'danger')
        return redirect(url_for('list_produits'))

    form = AddProductForm(obj=produit_to_update)
    
    if form.validate_on_submit():
        # Convertir le prix en float si nécessaire
        prix = float(form.prix.data) if isinstance(form.prix.data, Decimal) else form.prix.data
        produit.update_product(id, form.nom.data, prix, form.description.data, form.stock.data, form.type_produit.data)
        #flash('Produit mis à jour avec succès!', 'success')
        return redirect(url_for('list_produits'))

    return render_template('edit_product.html', form=form, produit=produit_to_update)


# Route pour supprimer un produit
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_product(id):
    produit = Produit()  # Créer une instance de la classe Produit
    produit.delete_product(id)  # Appeler la méthode pour supprimer le produit de la base de données
    flash('Produit supprimé avec succès!', 'danger')
    return redirect(url_for('list_produits'))


# Route pour afficher la liste des produits
@app.route('/list', methods=['GET'])
def list_produits():
    produit = Produit()  # Créer une instance de la classe Produit
    produits = produit.get_products()  # Appeler la méthode pour obtenir la liste des produits de la base de données
    return render_template('list_produits.html', produits=produits)


# ----------------------- Routes pour les Clients -----------------------
# Ajouter un client
@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    form = AddClientForm()
    if form.validate_on_submit():
        print("Formulaire validé :")
        print(f"Nom: {form.nom.data}, Email: {form.email.data}, Adresse: {form.adresse.data}")
        client = Client(
            nom=form.nom.data,
            email=form.email.data,
            adresse=form.adresse.data
        )
        client.add_client()
        return redirect(url_for('list_clients'))
    else:
        print("Erreur de validation : ", form.errors)
    return render_template('add_client.html', form=form)


# Route d'édition du client
@app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    client_instance = Client("", "", "")  # Crée une instance de Client
    client_data = client_instance.get_client_by_id(client_id)  # Appelle la méthode pour récupérer un client par ID

    if not client_data:
        return "Client non trouvé", 404  # Si le client n'existe pas dans la base de données

    # Convertir les données du client en un dictionnaire
    client_dict = {
        'id': client_id,
        'nom': client_data[1],
        'email': client_data[2],
        'adresse': client_data[3]
    }

    # Initialiser le formulaire avec les données actuelles du client
    form = EditClientForm(data=client_dict)

    if form.validate_on_submit():
        # Créer une instance de Client avec les nouvelles données
        client = Client(id=client_id,
                        nom=form.nom.data,
                        email=form.email.data,
                        adresse=form.adresse.data)
        
        # Mettre à jour le client dans la base de données
        client.update_client(client_id)

        # Rediriger vers la liste des clients
        return redirect(url_for('list_clients'))

    # Si la méthode est GET, ou si le formulaire n'est pas valide, afficher le formulaire avec les données actuelles
    return render_template('edit_client.html', form=form, client_id=client_id)



# Supprimer un client
@app.route('/delete_client/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    try:
        # Créez une instance de la classe Client avec l'ID du client à supprimer
        client = Client(nom=None, email=None, adresse=None)  # Utilisez des valeurs par défaut pour les autres attributs
        client.delete_client(client_id)  # Appelez la méthode d'instance delete_client
        flash("Client supprimé avec succès.", "success")
    except Exception as e:
        flash(f"Erreur lors de la suppression du client : {str(e)}", "danger")
    
    return redirect(url_for('list_clients'))  # Redirige vers la liste des clients


# Afficher la liste des clients
@app.route('/list_clients')
def list_clients():
    client_instance = Client()  # Créer une instance de Client
    clients = client_instance.get_clients()  # Appeler la méthode d'instance
    return render_template('list_clients.html', clients=clients)




# ----------------------- Routes pour les Commandes -----------------------

@app.route('/commandes')
def list_commandes():
    # Récupérer les clients et les produits depuis la base de données
    clients = Client()
    clients = clients.get_clients()
    
    # Récupérer les produits
    produits = Produit()
    produits = produits.get_products()
    return render_template('list_commandes.html', clients=clients, produits=produits)


@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    form = AddOrderForm()
    client = Client()
    produit = Produit()
    
    clients = client.get_clients()
    produits = produit.get_products()
    
    # Vérifiez si des clients ou produits sont disponibles
    if not clients or not produits:
        flash("Aucun client ou produit disponible pour passer une commande.", 'danger')
        return redirect(url_for('list_commandes'))
    
    # Générer les choix pour le formulaire
    form.client_id.choices = [(c[0], c[1]) for c in clients]
    form.produit_id.choices = [(p.id, p.nom) for p in produits]

    if form.validate_on_submit():
        commande = Commande(
            client_id=form.client_id.data,
            produit_id=form.produit_id.data,
            quantite=form.quantite.data
        )
        commande.add_commande()
        flash('Commande ajoutée avec succès.', 'success')
        return redirect(url_for('list_commandes'))
    
    return render_template('add_order.html', form=form)


@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    order = Commande.query.get_or_404(order_id)
    form = AddOrderForm(obj=order)
    form.client_id.choices = [(c[0], c[1]) for c in Client.get_clients()]
    form.produit_id.choices = [(p[0], p[1]) for p in Produit.get_products()]

    if form.validate_on_submit():
        order.client_id = form.client_id.data
        order.produit_id = form.produit_id.data
        order.quantite = form.quantite.data

        # Mettre à jour le produit et ajuster le stock
        produit = Produit.query.get(order.produit_id)
        produit.stock -= form.quantite.data  # Réduire le stock selon la nouvelle quantité
        
        db.session.commit()
        flash('Commande mise à jour avec succès.', 'success')
        return redirect(url_for('list_commandes'))

    return render_template('edit_order.html', form=form, order=order)

@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    order = Commande.query.get_or_404(order_id)
    produit = Produit.query.get(order.produit_id)

    # Réajuster le stock du produit après la suppression de la commande
    produit.stock += order.quantite

    # Supprimer la commande de la base de données
    db.session.delete(order)
    db.session.commit()

    flash('Commande supprimée avec succès.', 'success')
    return redirect(url_for('list_commandes'))


#-----------------------Methodes et Routes pour les Graphiques -----------------------

def generate_pie_chart(app):
    # Connexion à la base de données
    with app.open_resource('app_database.db') as db_file:
        conn = sqlite3.connect(db_file.name)
        cursor = conn.cursor()

        # Requête pour récupérer les données des types de produits
        cursor.execute('SELECT type_produit, COUNT(*) FROM produits GROUP BY type_produit')
        rows = cursor.fetchall()

        # Extraire les types de produits et leurs comptes
        types = [row[0] for row in rows]
        counts = [row[1] for row in rows]

        # Créer le graphique circulaire
        plt.figure(figsize=(8, 6))  # Taille du graphique
        plt.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')  # Assurer que le graphique est un cercle
        plt.title('Répartition des Produits par Type')

        # Sauvegarder le graphique dans un fichier
        plt.savefig('static/product_share.png', transparent=True)
        plt.close()

def generate_category_bar_chart(app):
    # Connexion à la base de données
    with app.open_resource('app_database.db') as db_file:
        conn = sqlite3.connect(db_file.name)
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

def generate_price_histogram(app):
    # Connexion à la base de données
    with app.open_resource('app_database.db') as db_file:
        conn = sqlite3.connect(db_file.name)
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
    generate_pie_chart(current_app)
    generate_category_bar_chart()
    generate_price_histogram()

    # Rendre la page avec les graphiques
    return render_template('graph.html', 
                           product_share='static/product_share.png', 
                           category_bar_chart='static/category_bar_chart.png', 
                           price_histogram='static/price_histogram.png')

if __name__ == '__main__':

    # Initialize the database by pushing the app context
    app.app_context().push()
    db.create_all()
    app.run(debug=True)

