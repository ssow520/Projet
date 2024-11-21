import sqlite3
from flask_sqlalchemy import SQLAlchemy

# Initialisation de SQLAlchemy
db = SQLAlchemy()

# Définition du modèle Produit
class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID du produit, clé primaire
    nom = db.Column(db.String(50), nullable=False)  # Nom du produit
    prix = db.Column(db.Float, nullable=False)  # Prix du produit
    description = db.Column(db.Text, nullable=True)  # Description du produit
    stock = db.Column(db.Integer, nullable=False)  # Stock disponible
    type_produit = db.Column(db.String(100), nullable=False)  # Type de produit (par exemple, fruits, légumes)

    # Méthode pour afficher l'objet de manière lisible
    def __repr__(self):
        return f'<Produit {self.nom}>'
    
class Produit:
    def __init__(self, nom="", prix=0.0, description="", stock=0, type_produit=""):
        self.nom = nom
        self.prix = prix
        self.description = description
        self.stock = stock
        self.type_produit = type_produit

    # Créer la base de données et la table si elles n'existent pas
    def create_table_product(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prix REAL NOT NULL,
                    description TEXT NOT NULL,
                    stock INTEGER NOT NULL,
                    type_produit TEXT NOT NULL
                )
            """)
            connection.commit()

    # Ajouter un nouveau produit à la base de données
    def add_product(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO produits (nom, prix, description, stock, type_produit)
                VALUES (?, ?, ?, ?, ?)
            """, (self.nom, self.prix, self.description, self.stock, self.type_produit))
            connection.commit()

    # Récupérer tous les produits de la base de données
    def get_products(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM produits")
            produits = cursor.fetchall()
            return produits

    # Mettre à jour un produit existant dans la base de données
    def update_product(self, product_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE produits
                SET nom = ?, prix = ?, description = ?, stock = ?, type_produit = ?
                WHERE id = ?
            """, (self.nom, self.prix, self.description, self.stock, self.type_produit, product_id))
            connection.commit()

    # Supprimer un produit de la base de données
    def delete_product(self, product_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM produits WHERE id = ?", (product_id,))
            connection.commit()

# Créer les tables
produit = Produit()
produit.create_table_product()


class Client:
    def __init__(self, nom="", email="", adresse=""):
        self.nom = nom
        self.email = email
        self.adresse = adresse

    # Create the database and table if they don't exist
    def create_table_client(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    email TEXT NOT NULL,
                    adresse TEXT NOT NULL
                )
            """)
            connection.commit()

    # Add a new client to the database
    def add_client(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO clients (nom, email, adresse)
                VALUES (?, ?, ?)
            """, (self.nom, self.email, self.adresse))
            connection.commit()

    # Retrieve all clients from the database
    def get_clients(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM clients")
            clients = cursor.fetchall()
            return clients

    # Update an existing client in the database
    def update_client(self, client_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE clients
                SET nom = ?, email = ?, adresse = ?
                WHERE id = ?
            """, (self.nom, self.email, self.adresse, client_id))
            connection.commit()

    # Delete a client from the database
    def delete_client(self, client_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            connection.commit()

client = Client()
client.create_table_client()


class Commande:
    def __init__(self, client_id=0, produit_id=0, quantite=0):
        self.client_id = client_id
        self.produit_id = produit_id
        self.quantite = quantite

    # Create the database and table if they don't exist
    def create_table_commande(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commandes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    produit_id INTEGER NOT NULL,
                    quantite INTEGER NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients (id),
                    FOREIGN KEY (produit_id) REFERENCES produits (id)
                )
            """)
            connection.commit()

    # Add a new commande to the database
    def add_commande(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO commandes (client_id, produit_id, quantite)
                VALUES (?, ?, ?)
            """, (self.client_id, self.produit_id, self.quantite))
            connection.commit()

    # Retrieve all commandes from the database
    def get_commandes(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM commandes")
            commandes = cursor.fetchall()
            return commandes

    # Update an existing commande in the database
    def update_commande(self, commande_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE commandes
                SET client_id = ?, produit_id = ?, quantite = ?
                WHERE id = ?
            """, (self.client_id, self.produit_id, self.quantite, commande_id))
            connection.commit()

    # Delete a commande from the database
    def delete_commande(self, commande_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM commandes WHERE id = ?", (commande_id,))
            connection.commit()

commande = Commande()
commande.create_table_commande()