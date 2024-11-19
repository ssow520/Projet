import sqlite3  # Module pour interagir avec la base de données SQLite
from werkzeug.security import check_password_hash  # Module pour la gestion des mots de passe sécurisés

# Constantes définissant les noms des tables
TABLE_PRODUIT = "produits"  # Nom de la table contenant les informations des produits
TABLE_CLIENT = "clients"  # Nom de la table contenant les informations des clients
TABLE_COMMANDE = "commandes"  # Nom de la table contenant les informations des commandes

class Produit:
    """
    Classe pour gérer les produits dans une base de données SQLite.
    Permet de créer la table, ajouter, lire, mettre à jour et supprimer des produits.
    """

    def __init__(self, nom="", prix=0.0, description="", stock=0, type_produit=""):
        """
        Initialise un objet Produit avec les attributs nécessaires.

        :param nom: Nom du produit (par défaut, chaîne vide).
        :param prix: Prix du produit (par défaut, 0.0).
        :param description: Description du produit (par défaut, chaîne vide).
        :param stock: Quantité en stock (par défaut, 0).
        :param type_produit: Catégorie ou type du produit (par défaut, chaîne vide).
        """
        self.nom = nom
        self.prix = prix
        self.description = description
        self.stock = stock
        self.type_produit = type_produit

    def create_table(self):
        """
        Crée la table `produits` dans la base de données si elle n'existe pas déjà.
        La table contient les colonnes : id, nom, prix, description, stock et type_produit.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:  # Connexion à la base de données
                cursor = conn.cursor()  # Création d'un curseur pour exécuter des commandes SQL
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {TABLE_PRODUIT} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nom TEXT NOT NULL,                   
                        prix REAL NOT NULL,                
                        description TEXT,                
                        stock INTEGER NOT NULL,             
                        type_produit TEXT NOT NULL           
                    );
                """)
                conn.commit()  # Validation des modifications
        except sqlite3.Error as e:
            print(f"Erreur lors de la création de la table : {e}")

    def add(self):
        """
        Ajoute un produit dans la table `produits`.

        :return: Un dictionnaire contenant les détails du produit ajouté ou un message d'erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    INSERT INTO {TABLE_PRODUIT} (nom, prix, description, stock, type_produit)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.nom, self.prix, self.description, self.stock, self.type_produit))
                conn.commit()
                product_id = cursor.lastrowid  # Récupération de l'ID généré pour le produit
                return {
                    "id": product_id,
                    "nom": self.nom,
                    "prix": self.prix,
                    "description": self.description,
                    "stock": self.stock,
                    "type_produit": self.type_produit
                }
        except sqlite3.Error as e:
            return {"error": str(e)}

    def read(self, product_id=None):
        """
        Lit les informations d'un produit spécifique ou de tous les produits.

        :param product_id: ID du produit à lire. Si None, tous les produits sont retournés.
        :return: Une liste de produits ou un dictionnaire contenant un message d'erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                if product_id:
                    cursor.execute(f"SELECT * FROM {TABLE_PRODUIT} WHERE id = ?", (product_id,))
                    return cursor.fetchone()  # Récupère un seul produit
                else:
                    cursor.execute(f"SELECT * FROM {TABLE_PRODUIT}")
                    return cursor.fetchall()  # Récupère tous les produits
        except sqlite3.Error as e:
            return {"error": str(e)}

    def update(self, product_id, **kwargs):
        """
        Met à jour les informations d'un produit en fonction des champs fournis.

        :param product_id: ID du produit à mettre à jour.
        :param kwargs: Dictionnaire contenant les champs à mettre à jour et leurs nouvelles valeurs.
        :return: Un message indiquant le succès ou une erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                update_fields = []
                values = []
                for field, value in kwargs.items():
                    if value is not None:
                        update_fields.append(f"{field} = ?")
                        values.append(value)
                if not update_fields:
                    return {"message": "Aucune modification à apporter."}
                values.append(product_id)  # Ajoute l'ID à la fin des valeurs
                query = f"UPDATE {TABLE_PRODUIT} SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                return {"message": "Produit mis à jour avec succès."}
        except sqlite3.Error as e:
            return {"error": str(e)}

    def delete(self, product_id):
        """
        Supprime un produit de la table `produits` en fonction de son ID.

        :param product_id: ID du produit à supprimer.
        :return: Un message indiquant le succès ou une erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {TABLE_PRODUIT} WHERE id = ?", (product_id,))
                conn.commit()
                return {"message": "Produit supprimé avec succès."}
        except sqlite3.Error as e:
            return {"error": str(e)}
        
Produit().create_table()


class Client:
    """
    Classe pour gérer les clients dans une base de données SQLite.
    Permet de créer la table, ajouter, lire, mettre à jour et supprimer des clients.
    """

    def __init__(self, nom="", email="", adresse=""):
        """
        Initialise un objet Client avec les attributs nécessaires.

        :param nom: Nom du client (par défaut, chaîne vide).
        :param email: Email du client (par défaut, chaîne vide).
        :param adresse: Adresse du client (par défaut, chaîne vide).
        """
        self.nom = nom
        self.email = email
        self.adresse = adresse

    def create_table(self):
        """
        Crée la table `clients` dans la base de données si elle n'existe pas déjà.
        La table contient les colonnes : id, nom, email et adresse.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:  # Connexion à la base de données
                cursor = conn.cursor()  # Création d'un curseur pour exécuter des commandes SQL
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {TABLE_CLIENT} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identifiant unique pour chaque client
                        nom TEXT NOT NULL,                     -- Nom du client
                        email TEXT NOT NULL UNIQUE,            -- Email unique
                        adresse TEXT NOT NULL                  -- Adresse du client
                    );
                """)
                conn.commit()  # Validation des modifications
        except sqlite3.Error as e:
            print(f"Erreur lors de la création de la table : {e}")

    def add(self):
        """
        Ajoute un client dans la table `clients`.

        :return: Un dictionnaire contenant les détails du client ajouté ou un message d'erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    INSERT INTO {TABLE_CLIENT} (nom, email, adresse)
                    VALUES (?, ?, ?)
                """, (self.nom, self.email, self.adresse))
                conn.commit()
                client_id = cursor.lastrowid  # Récupération de l'ID généré pour le client
                return {
                    "id": client_id,
                    "nom": self.nom,
                    "email": self.email,
                    "adresse": self.adresse
                }
        except sqlite3.Error as e:
            return {"error": str(e)}

    def read(self, client_id=None):
        """
        Lit les informations d'un client spécifique ou de tous les clients.

        :param client_id: ID du client à lire. Si None, tous les clients sont retournés.
        :return: Une liste de clients ou un dictionnaire contenant un message d'erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                if client_id:
                    cursor.execute(f"SELECT * FROM {TABLE_CLIENT} WHERE id = ?", (client_id,))
                    return cursor.fetchone()  # Récupère un seul client
                else:
                    cursor.execute(f"SELECT * FROM {TABLE_CLIENT}")
                    return cursor.fetchall()  # Récupère tous les clients
        except sqlite3.Error as e:
            return {"error": str(e)}

    def update(self, client_id, **kwargs):
        """
        Met à jour les informations d'un client en fonction des champs fournis.

        :param client_id: ID du client à mettre à jour.
        :param kwargs: Dictionnaire contenant les champs à mettre à jour et leurs nouvelles valeurs.
        :return: Un message indiquant le succès ou une erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                update_fields = []
                values = []
                for field, value in kwargs.items():
                    if value is not None:
                        update_fields.append(f"{field} = ?")
                        values.append(value)
                if not update_fields:
                    return {"message": "Aucune modification à apporter."}
                values.append(client_id)  # Ajoute l'ID à la fin des valeurs
                query = f"UPDATE {TABLE_CLIENT} SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                return {"message": "Client mis à jour avec succès."}
        except sqlite3.Error as e:
            return {"error": str(e)}

    def delete(self, client_id):
        """
        Supprime un client de la table `clients` en fonction de son ID.

        :param client_id: ID du client à supprimer.
        :return: Un message indiquant le succès ou une erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {TABLE_CLIENT} WHERE id = ?", (client_id,))
                conn.commit()
                return {"message": "Client supprimé avec succès."}
        except sqlite3.Error as e:
            return {"error": str(e)}
Client().create_table()


class Commande:
    """
    Classe pour gérer les commandes dans une base de données SQLite.
    Permet de créer la table, ajouter, lire et supprimer des commandes.
    """

    def __init__(self, client_id=0, produit_id=0, quantite=0):
        """
        Initialise un objet Commande avec les attributs nécessaires.

        :param client_id: ID du client (par défaut, 0).
        :param produit_id: ID du produit (par défaut, 0).
        :param quantite: Quantité commandée (par défaut, 0).
        """
        self.client_id = client_id
        self.produit_id = produit_id
        self.quantite = quantite

    def create_table(self):
        """
        Crée la table `commandes` dans la base de données si elle n'existe pas déjà.
        La table contient les colonnes : id, client_id, produit_id et quantite.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:  # Connexion à la base de données
                cursor = conn.cursor()  # Création d'un curseur pour exécuter des commandes SQL
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {TABLE_COMMANDE} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identifiant unique pour chaque commande
                        client_id INTEGER NOT NULL,            -- ID du client (référence)
                        produit_id INTEGER NOT NULL,           -- ID du produit (référence)
                        quantite INTEGER NOT NULL,             -- Quantité commandée
                        FOREIGN KEY (client_id) REFERENCES {TABLE_CLIENT}(id),  -- Relation avec la table clients
                        FOREIGN KEY (produit_id) REFERENCES {TABLE_PRODUIT}(id) -- Relation avec la table produits
                    );
                """)
                conn.commit()  # Validation des modifications
        except sqlite3.Error as e:
            print(f"Erreur lors de la création de la table : {e}")

    def add(self):
        """
        Ajoute une commande dans la table `commandes`.

        :return: Un dictionnaire contenant les détails de la commande ajoutée ou un message d'erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    INSERT INTO {TABLE_COMMANDE} (client_id, produit_id, quantite)
                    VALUES (?, ?, ?)
                """, (self.client_id, self.produit_id, self.quantite))
                conn.commit()
                commande_id = cursor.lastrowid  # Récupération de l'ID généré pour la commande
                return {
                    "id": commande_id,
                    "client_id": self.client_id,
                    "produit_id": self.produit_id,
                    "quantite": self.quantite
                }
        except sqlite3.Error as e:
            return {"error": str(e)}

    def read(self, commande_id=None):
        """
        Récupère une commande spécifique ou toutes les commandes.

        :param commande_id: ID de la commande à lire. Si None, toutes les commandes sont retournées.
        :return: Une liste des commandes ou un dictionnaire contenant un message d'erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                if commande_id:
                    cursor.execute(f"SELECT * FROM {TABLE_COMMANDE} WHERE id = ?", (commande_id,))
                    return cursor.fetchone()  # Récupère une seule commande
                else:
                    cursor.execute(f"SELECT * FROM {TABLE_COMMANDE}")
                    return cursor.fetchall()  # Récupère toutes les commandes
        except sqlite3.Error as e:
            return {"error": str(e)}

    def update(self, commande_id, **kwargs):
        """
        Met à jour une commande en fonction des champs fournis.

        :param commande_id: ID de la commande à mettre à jour.
        :param kwargs: Dictionnaire contenant les champs à mettre à jour et leurs nouvelles valeurs.
        :return: Un message indiquant le succès ou une erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                update_fields = []
                values = []
                for field, value in kwargs.items():
                    if value is not None:
                        update_fields.append(f"{field} = ?")
                        values.append(value)
                if not update_fields:
                    return {"message": "Aucune modification à apporter."}
                values.append(commande_id)  # Ajoute l'ID de la commande à la fin des valeurs
                query = f"UPDATE {TABLE_COMMANDE} SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                return {"message": "Commande mise à jour avec succès."}
        except sqlite3.Error as e:
            return {"error": str(e)}

    def delete(self, commande_id):
        """
        Supprime une commande de la table `commandes` en fonction de son ID.

        :param commande_id: ID de la commande à supprimer.
        :return: Un message indiquant le succès ou une erreur.
        """
        try:
            with sqlite3.connect("app_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {TABLE_COMMANDE} WHERE id = ?", (commande_id,))
                conn.commit()
                return {"message": "Commande supprimée avec succès."}
        except sqlite3.Error as e:
            return {"error": str(e)}
# Appel de la méthode create_table au démarrage de l'application
Commande().create_table()
