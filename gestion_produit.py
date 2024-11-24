import sqlite3

#--------------------Class Produit--------------------#

class Produit:
    def __init__(self, nom="", prix=0.0, description="", stock=0, type_produit="", id=None):
        self.nom = nom
        self.prix = prix
        self.description = description
        self.stock = stock
        self.type_produit = type_produit
        self.id = id

    # Méthode pour créer la table des produits si elle n'existe pas
    def create_table_product(self):
        try:
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
        except sqlite3.Error as e:
            print(f"Erreur lors de la création de la table : {e}")

    def exists(self, produit_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM produits WHERE id = ?", (produit_id,))
            result = cursor.fetchone()
            return result is not None
        
    # Méthode pour ajouter un nouveau produit
    def add_product(self):
        try:
            with sqlite3.connect("app_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO produits (nom, prix, description, stock, type_produit)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.nom, format(self.prix, ".2f"), self.description, self.stock, self.type_produit))
                self.id = cursor.lastrowid
                connection.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout du produit : {e}")



    # Méthode pour récupérer tous les produits
    def get_products(self):
        try:
            with sqlite3.connect("app_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM produits")
                produits = cursor.fetchall()
                # Retourner des objets Produit au lieu de tuples
                return [Produit(nom=row[1], prix=row[2], description=row[3], stock=row[4], type_produit=row[5], id=row[0]) for row in produits]
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des produits : {e}")
            return []
        
    #Méthode pour filtrer les produits par type
    def filter_products_by_type(self, type_produit):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, nom, prix, type_produit, description, stock FROM produits WHERE type_produit = ?", (type_produit,))
            rows = cursor.fetchall()

        # Conversion des résultats en dictionnaires
        columns = ['id', 'nom', 'prix', 'type_produit', 'description', 'stock']  # Colonnes de la table produits
        produits = [dict(zip(columns, row)) for row in rows]
        
        return produits



    # Méthode pour mettre à jour un produit existant
    def update_product(self, produit_id, nom, prix, description, stock, type_produit):
        try:
            with sqlite3.connect("app_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE produits
                    SET nom = ?, prix = ?, description = ?, stock = ?, type_produit = ?
                    WHERE id = ?
                """, (nom, prix, description, stock, type_produit, produit_id))
                connection.commit()
                print(f"Produit avec ID {produit_id} mis à jour.")  # Pour déboguer
        except sqlite3.Error as e:
            print(f"Erreur lors de la mise à jour du produit : {e}")


    # Méthode pour supprimer un produit
    def delete_product(self, product_id):
        try:
            with sqlite3.connect("app_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM produits WHERE id = ?", (product_id,))
                connection.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression du produit : {e}")


produit = Produit()
produit.create_table_product()



#--------------------Class Client--------------------#

class Client:
    def __init__(self, id=None, nom=None, email=None, adresse=None):
        self.id = id
        self.nom = nom
        self.email = email
        self.adresse = adresse


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


    def exists(self, client_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM clients WHERE id = ?", (client_id,))
            result = cursor.fetchone()
            return result is not None
        
    def add_client(self):
            try:
                with sqlite3.connect("app_database.db") as connection:
                    cursor = connection.cursor()
                    cursor.execute("""
                        INSERT INTO clients (nom, email, adresse)
                        VALUES (?, ?, ?)
                    """, (self.nom, self.email, self.adresse))
                    connection.commit()
            except sqlite3.Error as e:
                connection.close()


    def get_clients(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, nom, email FROM clients")
            return cursor.fetchall()
        
        # Méthode pour récupérer un client par ID
    def get_client_by_id(self, client_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, nom, email, adresse FROM clients WHERE id = ?", (client_id,))
            return cursor.fetchone()  # Retourne un seul client

    def update_client(self, client_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE clients
                SET nom = ?, email = ?, adresse = ?
                WHERE id = ?
            """, (self.nom, self.email, self.adresse, client_id))
            connection.commit()

    def delete_client(self, client_id):
        try:
            with sqlite3.connect("app_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
                connection.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression du client : {str(e)}")

client = Client()
client.create_table_client()


#--------------------Class Commande--------------------#

class Commande:
    def __init__(self, client_id=0, produit_id=0, quantite=0):
        self.client_id = client_id
        self.produit_id = produit_id
        self.quantite = quantite

    # Créer la table commandes si elle n'existe pas
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

    # Ajouter une nouvelle commande à la base de données
    def add_commande(self):
        produit = Produit()
        if not produit.exists(self.produit_id):
            raise ValueError("Le produit n'existe pas.")
        if not client.exists(self.client_id):
            raise ValueError("Le client n'existe pas.")
        

        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO commandes (client_id, produit_id, quantite)
                VALUES (?, ?, ?)
            """, (self.client_id, self.produit_id, self.quantite))
            connection.commit()

    # Récupérer toutes les commandes
    def get_commandes(self):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM commandes")
            commandes = cursor.fetchall()
            return commandes

    # Mettre à jour une commande existante
    def update_commande(self, commande_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE commandes
                SET client_id = ?, produit_id = ?, quantite = ?
                WHERE id = ?
            """, (self.client_id, self.produit_id, self.quantite, commande_id))
            connection.commit()

    # Supprimer une commande
    def delete_commande(commande_id):
        with sqlite3.connect("app_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM commandes WHERE id = ?", (commande_id,))
            connection.commit()

commande = Commande()
commande.create_table_commande()