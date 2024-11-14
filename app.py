from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Fonction pour se connecter à la base de données
def get_db_connection():
    conn = sqlite3.connect('app_database.db')
    conn.row_factory = sqlite3.Row  # Pour récupérer les résultats sous forme de dictionnaire
    return conn

# Page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

# CRUD pour les produits
@app.route('/products')
def products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM produits').fetchall()
    conn.close()
    return render_template('products.html', products=products)

# Ajouter un produit
@app.route('/add_product.', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        nom = request.form['nom']
        prix = request.form['prix']
        description = request.form['description']
        stock = request.form['stock']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO produits (nom, prix, description, stock) VALUES (?, ?, ?, ?)', 
                     (nom, prix, description, stock))
        conn.commit()
        conn.close()
        return redirect(url_for('products'))  # Redirige vers la page des produits
    return render_template('add_product.html')

# Modifier un produit
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM produits WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        nom = request.form['nom']
        prix = request.form['prix']
        description = request.form['description']
        stock = request.form['stock']
        
        conn.execute('UPDATE produits SET nom = ?, prix = ?, description = ?, stock = ? WHERE id = ?',
                     (nom, prix, description, stock, id))
        conn.commit()
        conn.close()
        return redirect(url_for('products'))
    
    conn.close()
    return render_template('edit_product.html', product=product)

# Je vais a l'ecole

# Supprimer un produit
@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM produits WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('products'))

if __name__ == '__main__':
    app.run(debug=True)
