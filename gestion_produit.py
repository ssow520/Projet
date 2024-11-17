import sqlite3
from datetime import datetime

# Décorateur pour vérifier si l'utilisateur est authentifié
def authenticate_user(func):
    """Vérifie si l'utilisateur est authentifié avant d'exécuter la fonction."""
    def wrapper(*args, **kwargs):
        # Simule la vérification de l'authentification
        user_authenticated = True  # Cette valeur est simulée; il faudrait une vraie logique d'authentification
        if user_authenticated:
            return func(*args, **kwargs)  # Si l'utilisateur est authentifié, on exécute la fonction
        else:
            print("Erreur : utilisateur non authentifié.") # Si l'utilisateur n'est pas authentifié, on affiche une erreur
    return wrapper  # Retourne la fonction wrapper qui va être utilisée pour le décorateur

# Décorateur pour la journalisation des actions
def log_action(func):
    """Enregistre l'action de l'utilisateur dans la console avec un horodatage."""
    def wrapper(*args, **kwargs):
        # Affiche un message de début d'exécution de la fonction avec un horodatage
        print(f"[{datetime.now()}] Exécution de : {func.__name__}")
        result = func(*args, **kwargs)  # Exécute la fonction décorée
        # Affiche un message de fin d'exécution de la fonction avec un horodatage
        print(f"[{datetime.now()}] Fin de l'exécution de : {func.__name__}")
        return result # Retourne le résultat de l'exécution de la fonction
    return wrapper # Retourne la fonction wrapper qui va être utilisée pour le décorateur


# Décorateur pour gérer les erreurs
def handle_errors(func):
    """Gère les erreurs et affiche un message en cas d'exception."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs) # Essaie d'exécuter la fonction décorée
        except Exception as e:
             # En cas d'erreur, on affiche l'exception
            print(f"Erreur lors de l'exécution de {func.__name__}: {e}")
    return wrapper  # Retourne la fonction wrapper qui va être utilisée pour le décorateur


# Classe Produit pour manipuler les produits dans la base de données
class Produit:
    def __init__(self, nom="", prix=0.0, description="", stock=0):
        self.nom = nom # Attribue le nom du produit
        self.prix = prix # Attribue le prix du produit
        self.description = description # Attribue la description du produit
        self.stock = stock # Attribue la quantité en stock du produit
        self.create_table() # Crée la table des produits si elle n'existe pas déjà

    def create_table(self):
        """ Crée la table Produits si elle n'existe pas déjà """
         # Connexion à la base de données SQLite
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor() # Crée un objet cursor pour exécuter des requêtes SQL
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produits (
                    id INTEGER PRIMARY KEY,
                    nom TEXT NOT NULL,
                    prix REAL NOT NULL,
                    description TEXT,
                    stock INTEGER NOT NULL
                );
            """) # Exécute une requête SQL pour créer la table des produits si elle n'existe pas déjà
            conn.commit() # Valide la transaction

    # Ajoute un produit dans la base de données
    @authenticate_user
    @log_action
    @handle_errors
    def add(self):
        """ Ajoute un produit dans la base de données """
        # Connexion à la base de données SQLite
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor() # Crée un objet cursor pour exécuter des requêtes SQL
            cursor.execute("INSERT INTO produits (nom, prix, description, stock) VALUES (?, ?, ?, ?)",
                           (self.nom, self.prix, self.description, self.stock)) # Exécute une requête pour insérer un produit
            conn.commit()
        print("Produit ajouté avec succès.") # Affiche un message de confirmation

    #Récupère les produits (tous ou un seul)
    @handle_errors
    def read(self):
        """ Récupère un produit spécifique ou tous les produits """
        try:
                # Connexion à la base de données SQLite
                with sqlite3.connect("app_database.db") as conn:
                    cursor = conn.cursor() # Crée un objet cursor pour exécuter des requêtes SQL
                    cursor.execute("SELECT * FROM produits") # Exécute une requête pour récupérer tous les produits
                    return cursor.fetchall()# Retourne toutes les lignes (tous les produits)
        except Exception as e:
            conn.rollback()
            return f"Erreur dans l'affichage de données {str(e)}"
        finally:
            # Finalement, fermer la base de données
            conn.close()
        
            


    
              

    # Met à jour un produit dans la base de données
    @authenticate_user
    @log_action
    @handle_errors
    def update(self, product_id, nom="", prix=0, description="", stock=-1):
        """ Met à jour un produit spécifique """
        # Connexion à la base de données SQLite
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()  # Crée un objet cursor pour exécuter des requêtes SQL
            update_champs = [] # Liste pour stocker les champs à mettre à jour
            values = [] # Liste pour stocker les valeurs des champs

            # Vérifie chaque champ et ajoute les changements à la liste si nécessaire
            if nom != "":
                update_champs.append("nom = ?")
                values.append(nom)
            if prix != 0:
                update_champs.append("prix = ?")
                values.append(prix)
            if description != "":
                update_champs.append("description = ?")
                values.append(description)
            if stock != -1:
                update_champs.append("stock = ?")
                values.append(stock)

            # Si aucun champ n'a été ajouté à la liste, il n'y a rien à mettre à jour
            if not update_champs:
                print("Aucune modification à apporter.")
                return

            values.append(product_id) # Ajoute l'ID du produit à la fin de la liste des valeurs
            query = f"UPDATE produits SET {', '.join(update_champs)} WHERE id = ?" # Crée la requête SQL
            cursor.execute(query, values) # Exécute la requête SQL avec les valeurs à mettre à jour
            conn.commit() # Valide la transaction
            print("Produit mis à jour avec succès.") # Affiche un message de confirmation

    # Supprime un produit de la base de données
    @authenticate_user
    @log_action
    @handle_errors
    def delete(self, product_id):
        """ Supprime un produit en fonction de son ID """
        # Connexion à la base de données SQLite
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor() # Crée un objet cursor pour exécuter des requêtes SQL
            cursor.execute("DELETE FROM produits WHERE id = ?", (product_id,)) # Exécute une requête pour supprimer un produit
            conn.commit() # Valide la transaction
        print("Produit supprimé avec succès.") # Affiche un message de confirmation

    # Utilisation d'un générateur pour gérer de grandes quantités de données dans read
    def read_large_data(self, chunk_size=5):
        """ Générateur pour récupérer les produits par morceaux """
         # Connexion à la base de données SQLite
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor() # Crée un objet cursor pour exécuter des requêtes SQL
            cursor.execute("SELECT * FROM produits") # Exécute une requête pour récupérer tous les produits
            while True:
                rows = cursor.fetchmany(chunk_size)  # Charge un morceau de données de la taille spécifiée
                if not rows:
                    break # Si aucune donnée n'est disponible, on arrête
                for row in rows:
                    yield row  # Renvoie chaque produit un par un

# Classe Client
class Client:
    def __init__(self, nom="", email="", adresse=""):
        self.nom = nom
        self.email = email
        self.adresse = adresse
        self.create_table()

    def create_table(self):
        """ Crée la table Clients si elle n'existe pas déjà """
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY,
                    nom TEXT NOT NULL,
                    email TEXT NOT NULL,
                    adresse TEXT NOT NULL
                );
            """)
            conn.commit()

    @authenticate_user
    @log_action
    @handle_errors
    def add(self):
        """ Ajoute un client dans la base de données """
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clients (nom, email, adresse) VALUES (?, ?, ?)",
                           (self.nom, self.email, self.adresse))
            conn.commit()
        print("Client ajouté avec succès.")

    @handle_errors
    def read(self, client_id=0):
        """ Récupère un client spécifique ou tous les clients """
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            if client_id:
                cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
                return cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM clients")
                return cursor.fetchall()

    @authenticate_user
    @log_action
    @handle_errors
    def update(self, client_id, nom="", email="", adresse=""):
        """ Met à jour un client spécifique """
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            update_champs = []
            values = []

            if nom != "":
                update_champs.append("nom = ?")
                values.append(nom)
            if email != "":
                update_champs.append("email = ?")
                values.append(email)
            if adresse != "":
                update_champs.append("adresse = ?")
                values.append(adresse)

            if not update_champs:
                print("Aucune modification à apporter.")
                return

            values.append(client_id)
            query = f"UPDATE clients SET {', '.join(update_champs)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            print("Client mis à jour avec succès.")

    @authenticate_user
    @log_action
    @handle_errors
    def delete(self, client_id):
        """ Supprime un client en fonction de son ID """
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()
        print("Client supprimé avec succès.")

# Classe Commande
class Commande:
    def __init__(self, client_id=0, produit_id=0, quantite=0):
        self.client_id = client_id
        self.produit_id = produit_id
        self.quantite = quantite
        self.create_table()

    def create_table(self):
        """ Crée la table Commandes si elle n'existe pas déjà """
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commandes (
                    id INTEGER PRIMARY KEY,
                    client_id INTEGER,
                    produit_id INTEGER,
                    quantite INTEGER NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(id),
                    FOREIGN KEY (produit_id) REFERENCES produits(id)
                );
            """)
            conn.commit()

    @authenticate_user
    @log_action
    @handle_errors
    def add(self):
        """ Ajoute une commande dans la base de données """
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO commandes (client_id, produit_id, quantite) VALUES (?, ?, ?)",
                           (self.client_id, self.produit_id, self.quantite))
            conn.commit()
        print("Commande ajoutée avec succès.")

    @handle_errors
    def read(self, order_id=0):
        """ Récupère une commande spécifique ou toutes les commandes """
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            if order_id:
                cursor.execute("SELECT * FROM commandes WHERE id = ?", (order_id,))
                return cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM commandes")
                return cursor.fetchall()

    @authenticate_user
    @log_action
    @handle_errors
    def update(self, order_id, client_id=-1, produit_id=-1, quantite=-1):
        """ Met à jour une commande spécifique """
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            update_champs = []
            values = []

            if client_id != -1:
                update_champs.append("client_id = ?")
                values.append(client_id)
            if produit_id != -1:
                update_champs.append("produit_id = ?")
                values.append(produit_id)
            if quantite != -1:
                update_champs.append("quantite = ?")
                values.append(quantite)

            if not update_champs:
                print("Aucune modification à apporter.")
                return

            values.append(order_id)
            query = f"UPDATE commandes SET {', '.join(update_champs)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            print("Commande mise à jour avec succès.")

    @authenticate_user
    @log_action
    @handle_errors
    def delete(self, order_id):
        """ Supprime une commande en fonction de son ID """
        with sqlite3.connect("app_database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM commandes WHERE id = ?", (order_id,))
            conn.commit()
        print("Commande supprimée avec succès.")


# Menu principal pour gérer les options
@log_action
def menu():
    while True:
        print("\n-- Menu Principal --")
        print("1. Gérer les produits")
        print("2. Gérer les clients")
        print("3. Gérer les commandes")
        print("4. Quitter")
        
        choix = input("Choisissez une option : ")
        
        if choix == "1":
            menu_produit() # Fonction pour gérer les produits
        elif choix == "2":
            menu_client() # Fonction pour gérer les clients
        elif choix == "3":
            menu_commande() # Fonction pour gérer les commandes
        elif choix == "4":
            print("Au revoir !")
            break
        else:
            print("Option invalide. Veuillez réessayer.")

# Menu pour gérer les produits
@log_action
def menu_produit():

    # Affiche les options pour les produits et appelle les méthodes correspondantes
    produit = Produit()
    while True:
        print("\n-- Menu Produits --")
        print("1. Ajouter un produit")
        print("2. Afficher les produits")
        print("3. Mettre à jour un produit")
        print("4. Supprimer un produit")
        print("5. Retour au menu principal")
        
        choix = input("Choisissez une option : ")
        
        if choix == "1":
            nom = input("Nom du produit : ")
            prix = float(input("Prix du produit : "))
            description = input("Description du produit : ")
            stock = int(input("Stock du produit : "))
            produit = Produit(nom, prix, description, stock)
            produit.add()
        elif choix == "2":
            produits = produit.read()
            for p in produits:
                print(p)
        elif choix == "3":
            product_id = int(input("ID du produit à mettre à jour : "))
            nom = input("Nom (laisser vide pour ne pas modifier) : ")
            prix = float(input("Prix (0 pour ne pas modifier) : "))
            description = input("Description (laisser vide pour ne pas modifier) : ")
            stock = int(input("Stock (-1 pour ne pas modifier) : "))
            produit.update(product_id, nom, prix, description, stock)
        elif choix == "4":
            product_id = int(input("ID du produit à supprimer : "))
            produit.delete(product_id)
        elif choix == "5":
            break
        else:
            print("Option invalide. Veuillez réessayer.")

# Menu pour gérer les clients
@log_action
def menu_client():

    # Affiche les options pour les clients et appelle les méthodes correspondantes
    client = Client()
    while True:
        print("\n-- Menu Clients --")
        print("1. Ajouter un client")
        print("2. Afficher les clients")
        print("3. Mettre à jour un client")
        print("4. Supprimer un client")
        print("5. Retour au menu principal")
        
        choix = input("Choisissez une option : ")
        
        if choix == "1":
            nom = input("Nom du client : ")
            email = input("Email du client : ")
            adresse = input("Adresse du client : ")
            client = Client(nom, email, adresse)
            client.add()
        elif choix == "2":
            clients = client.read()
            for c in clients:
                print(c)
        elif choix == "3":
            client_id = int(input("ID du client à mettre à jour : "))
            nom = input("Nom (laisser vide pour ne pas modifier) : ")
            email = input("Email (laisser vide pour ne pas modifier) : ")
            adresse = input("Adresse (laisser vide pour ne pas modifier) : ")
            client.update(client_id, nom, email, adresse)
        elif choix == "4":
            client_id = int(input("ID du client à supprimer : "))
            client.delete(client_id)
        elif choix == "5":
            break
        else:
            print("Option invalide. Veuillez réessayer.")

# Menu pour gérer les commandes
@log_action
def menu_commande():
    # Affiche les options pour les commandes et appelle les méthodes correspondantes
    commande = Commande()
    while True:
        print("\n-- Menu Commandes --")
        print("1. Ajouter une commande")
        print("2. Afficher les commandes")
        print("3. Mettre à jour une commande")
        print("4. Supprimer une commande")
        print("5. Retour au menu principal")
        
        choix = input("Choisissez une option : ")
        
        if choix == "1":
            client_id = int(input("ID du client : "))
            produit_id = int(input("ID du produit : "))
            quantite = int(input("Quantité : "))
            commande = Commande(client_id, produit_id, quantite)
            commande.add()
        elif choix == "2":
            commandes = commande.read()
            for c in commandes:
                print(c)
        elif choix == "3":
            order_id = int(input("ID de la commande à mettre à jour : "))
            client_id = int(input("ID du client (-1 pour ne pas modifier) : "))
            produit_id = int(input("ID du produit (-1 pour ne pas modifier) : "))
            quantite = int(input("Quantité (-1 pour ne pas modifier) : "))
            commande.update(order_id, client_id, produit_id, quantite)
        elif choix == "4":
            order_id = int(input("ID de la commande à supprimer : "))
            commande.delete(order_id)
        elif choix == "5":
            break
        else:
            print("Option invalide. Veuillez réessayer.")


# Lancer le programme
# Exécute le menu principal si le script est lancé directement
if __name__ == "__main__":
    menu()
