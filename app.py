from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/contractor')

client = MongoClient(host=f'{host}?retryWrites=false')  
db = client.get_default_database()
pantry = db.pantry
item = db.item
cart = db.cart
#Return pantry
@app.route('/')
def pantry_index():
    """Show all pantry items."""
    return render_template('pantry_index.html', pantry=pantry.find())

@app.route('/pantry/new')
def pantry_new():
    """Create a new pantry item."""
    return render_template('pantry_new.html', item={}, title='New Item')

@app.route('/pantry', methods=['POST'])
def pantry_submit():
    """Submit a new pantry item."""
    item = {
        "name": request.form.get('name'),
        "image": request.form.get('image'),
        "price": request.form.get('price'),
        "description and quantity": request.form.get('description'),
        'created_at': datetime.now()
    }
    print(item)
    item_id = pantry.insert_one(item).inserted_id
    return redirect(url_for('pantry_show', item_id=item_id))

# @app.route('/pantry', methods=['GET'])
# def pantry_homepage():
#         return render_template('pantry_index.html',item_id=item_id)


@app.route('/pantry/<item_id>')
def pantry_show(item_id):
    """Show a single pantry item."""
    item = pantry.find_one({'_id': ObjectId(item_id)})
    return render_template('pantry_show.html', item=item)

@app.route('/pantry/<item_id>/edit')
def pantry_edit(item_id):
    """Show the edit form for a pantry item."""
    item = pantry.find_one({'_id': ObjectId(item_id)})
    return render_template('pantry_edit.html', item=item, title='Edit Pantry Item')

@app.route('/pantry/<item_id>', methods=['POST'])
def pantry_update(item_id):
    """Submit an edited item."""
    updated_item = {
        "name": request.form['name'],
        "image": request.form['image'],
        "price": request.form['price'],
        "description and quantity": request.form['description'],
        'created_at': datetime.now()
    }
    pantry.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': updated_item})
    return redirect(url_for('pantry_show', item_id=item_id, item=item))

@app.route('/pantry/<item_id>/delete', methods=['POST'])
def pantry_delete(item_id):
    """Delete one pantry item."""
    pantry.delete_one({'_id': ObjectId(item_id)})
    return redirect(url_for('pantry_index'))
#Shows cart
@app.route("/pantry/cart")
def cart_show():
    return render_template("show_cart.html", cart=cart.find())

#Shows item in user's cart
@app.route("/pantry/cart/<cart_item_id>")
def cart_item_show(cart_item_id):
    cart_item = cart.find_one({"_id": ObjectId(cart_item_id)})
    return render_template("cart_item_show.html", cart_item=cart_item)

#Delete an item from cart
@app.route("/pantry/cart/<cart_item_id>/delete", methods=["POST"])
def cart_delete(cart_item_id):
    cart.delete_one({"_id": ObjectId(cart_item_id)})
    return redirect(url_for("show_cart"))

#Delete all items in cart
@app.route("/pantry/cart/destroy")
def cart_destroy():
    for cart_item in cart.find():
        cart.delete_one({"_id": ObjectId(cart_item["_id"])})
    return redirect(url_for("show_cart"))

#Cart Checkout
@app.route("/pantry/cart/checkout")
def cart_checkout():
    total = 0
    for item in cart.find():
        total += int(item["price"])
    print("$" + str(total))
    return redirect(url_for("cart_destroy"))

#Add item to cart
@app.route('/pantry/<cart_item_id>/add-to-cart', methods=['POST'])
def add_to_cart(cart_item_id):
    cart_item = pantry.find_one({"_id": ObjectId(cart_item_id)})
    # for _ in range(int(request.form.get("quant"))):
    #     new_item = {
    #         "food name": cart_item["name"],
    #         "image": cart_item["image"],
    #         "price": cart_item["price"],
    #         "description and quantity": cart_item["description"]
    #         }
    cart.insert_one(cart_item)
    return redirect(url_for('cart_show'))

if __name__ == '__main__':
    app.run(debug=True)