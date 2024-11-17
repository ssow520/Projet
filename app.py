from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from datetime import datetime

# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = 'votre_clé_secrète_ici'  # Nécessaire pour les sessions et les messages flash

# Importation des classes existantes
# Assurez-vous que ces classes sont dans le même dossier que ce fichier
from gestion_produit import Produit, Client, Commande

# Fonction pour créer la table des utilisateurs
def create_users_table():
    with sqlite3.connect("app_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        conn.commit()

             # Ajoutez un utilisateur de test si la table est vide
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            hashed_password = generate_password_hash('1234')
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('ssow', hashed_password))

# Appel de la fonction pour créer la table des utilisateurs
create_users_table()

# Décorateur pour vérifier si l'utilisateur est connecté
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route pour la page d'accueil
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Route pour la page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]
                flash('Connexion réussie!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
    return render_template('login.html')

# Route pour la déconnexion
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

# Route pour la gestion des produits
@app.route('/products')
@login_required
def products():
    produit = Produit()
    products_list = produit.read()
    return render_template('products.html', products=products_list)

# Route pour ajouter un produit
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        nom = request.form['nom']
        prix = float(request.form['prix'])
        description = request.form['description']
        stock = int(request.form['stock'])
        produit = Produit(nom, prix, description, stock)
        produit.add()
        flash('Produit ajouté avec succès!', 'success')
        return redirect(url_for('products'))
    return render_template('add_product.html')

# Route pour modifier un produit
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    produit = Produit()
    if request.method == 'POST':
        nom = request.form['nom']
        prix = float(request.form['prix'])
        description = request.form['description']
        stock = int(request.form['stock'])
        produit.update(product_id, nom, prix, description, stock)
        flash('Produit mis à jour avec succès!', 'success')
        return redirect(url_for('products'))
    product = produit.read(product_id)
    return render_template('edit_product.html', product=product)

# Route pour supprimer un produit
@app.route('/delete_product/<int:product_id>')
@login_required
def delete_product(product_id):
    produit = Produit()
    produit.delete(product_id)
    flash('Produit supprimé avec succès!', 'success')
    return redirect(url_for('products'))

# Route pour la gestion des clients
@app.route('/clients')
@login_required
def clients():
    client = Client()
    clients_list = client.read()
    return render_template('clients.html', clients=clients_list)

# Route pour ajouter un client
@app.route('/add_client', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        adresse = request.form['adresse']
        client = Client(nom, email, adresse)
        client.add()
        flash('Client ajouté avec succès!', 'success')
        return redirect(url_for('clients'))
    return render_template('add_client.html')

# Route pour modifier un client
@app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client()
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        adresse = request.form['adresse']
        client.update(client_id, nom, email, adresse)
        flash('Client mis à jour avec succès!', 'success')
        return redirect(url_for('clients'))
    client_data = client.read(client_id)
    return render_template('edit_clients.html', client=client_data)

# Route pour supprimer un client
@app.route('/delete_client/<int:client_id>')
@login_required
def delete_client(client_id):
    client = Client()
    client.delete(client_id)
    flash('Client supprimé avec succès!', 'success')
    return redirect(url_for('clients'))

# Route pour la gestion des commandes
@app.route('/commandes')
@login_required
def commandes():
    commande = Commande()
    commandes_list = commande.read()
    return render_template('commandes.html', commandes=commandes_list)

# Route pour ajouter une commande
@app.route('/add_commande', methods=['GET', 'POST'])
@login_required
def add_commande():
    if request.method == 'POST':
        client_id = int(request.form['client_id'])
        produit_id = int(request.form['produit_id'])
        quantite = int(request.form['quantite'])
        commande = Commande(client_id, produit_id, quantite)
        commande.add()
        flash('Commande ajoutée avec succès!', 'success')
        return redirect(url_for('commandes'))
    return render_template('add_commande.html')

# Route pour modifier une commande
@app.route('/edit_commande/<int:commande_id>', methods=['GET', 'POST'])
@login_required
def edit_commande(commande_id):
    commande = Commande()
    if request.method == 'POST':
        client_id = int(request.form['client_id'])
        produit_id = int(request.form['produit_id'])
        quantite = int(request.form['quantite'])
        commande.update(commande_id, client_id, produit_id, quantite)
        flash('Commande mise à jour avec succès!', 'success')
        return redirect(url_for('commandes'))
    commande_data = commande.read(commande_id)
    return render_template('edit_commande.html', commande=commande_data)

# Route pour supprimer une commande
@app.route('/delete_commande/<int:commande_id>')
@login_required
def delete_commande(commande_id):
    commande = Commande()
    commande.delete(commande_id)
    flash('Commande supprimée avec succès!', 'success')
    return redirect(url_for('commandes'))

# Lancement de l'application
if __name__ == '__main__':
    app.run(debug=True)