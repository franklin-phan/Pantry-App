from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)
@app.route("/")
def pantry_index():
    """Return homepage"""
    return render_template("pantry_index.html", pantry=pantry.find())


@app.route("/pantry/new")
def new_item():
    """Return new listing creation page"""
    return render_template("pantry_new.html", item={},
                           title='New listing')


@app.route("/pantry/new", methods=["POST"])
def pantry_new():
    """Allow the user to create a new listing"""
    item = {
        "food name": request.form.get("name"),
        "picture": request.form.get("picture"),
        "price": request.form.get("price"),
        "description": request.form.get("description")
    }
    listing_id = pantry.insert_one(pantry).inserted_id
    return redirect(url_for("pantry_show", item_id=item_id))


@app.route("/pantry/<item_id>")
def pantry_show(item_id):
    """Show a single listing."""
    item = pantry.find_one({"_id": ObjectId(item_id)})
    return render_template("pantry_show.html", item=item)


@app.route('/pantrys/<item_id>', methods=['POST'])
def pantry_update(item_id):
    """Submit an edited listing."""
    item_updated = {
        "food name": request.form.get("name"),
        "picture": request.form.get("picture"),
        "price": request.form.get("price"),
        "description": request.form.get("description")
    }
    pantry.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': item_updated})
    return redirect(url_for('pantry_show', item_id=item_id))


@app.route("/pantry/<item_id>/edit")
def pantry_edit(item_id):
    """Show the edit form for a listing."""
    item = pantry.find_one({"_id": ObjectId(item_id)})
    return render_template("pantry_edit.html", item=item,
                           title="Edit listing")


@app.route('/pantry/<item_id>/delete', methods=['POST'])
def pantry_delete(item_id):
    """Delete one listing."""
    pantry.delete_one({'_id': ObjectId(item_id)})
    return redirect(url_for('pantry_index'))

if __name__ == '__main__':
    app.run(debug=True)
