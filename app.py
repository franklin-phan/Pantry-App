from flask import Flask, render_template, request, redirect, url_for
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from datetime import datetime
import os
# from dotenv import load_dotenv
# load_dotenv()

app = Flask(__name__)

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/Contractor')

client = MongoClient(host=f'{host}?retryWrites=false')  
db = client.get_default_database()
pantry = db.pantry
item = db.item
ingredients = db.ingredients
recipes = db.recipes


spoon_apiKey = os.getenv("spoonacular_API_KEY")

#Return pantry
@app.route('/')
def pantry_index():
    """Show all pantry items."""

    r = requests.get("https://api.spoonacular.com/food/jokes/random?apiKey=" + spoon_apiKey)
    r2 = requests.get("https://api.spoonacular.com/food/trivia/random?apiKey=" + spoon_apiKey)

    if r.status_code == 200:
        joke = json.loads(r.content)['text']
    else:
        joke = None
    if r2.status_code == 200:
        fact = json.loads(r2.content)['text']
    else:
        fact = None
    return render_template('pantry_index.html', pantry=pantry.find(),fact=fact,joke=joke)

@app.route('/pantry/new')
def pantry_new():
    """Create a new pantry item."""
    return render_template('pantry_new.html', item={}, title='New Pantry Item')

@app.route('/pantry', methods=['POST'])
def pantry_submit():
    """Submit a new pantry item."""
    item = {
        "name": request.form.get('name'),
        "image": request.form.get('image'),
        "description": request.form.get('description'),
        "favorite food": request.form.get('favorite'),
        "type": request.form.get('type'),
        "amount": request.form.get('amount'),
        "expiration": request.form.get('expiration')
    }
    print(item)
    item_id = pantry.insert_one(item).inserted_id
    return redirect(url_for('pantry_show', item_id=item_id))


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

@app.route('/pantry/<item_id>/edit_amount')
def panty_edit_amount(item_id):
    """Edit amount for a single pantry item"""
    item = pantry.find_one({'_id': ObjectId(item_id)})
    return render_template('pantry_edit_amount.html', item=item, title='Edit Pantry Item amount')

@app.route('/pantry/<item_id>', methods=['POST'])
def pantry_update(item_id):
    """Submit an edited item."""
    updated_item = {
        "name": request.form.get('name'),
        "image": request.form.get('image'),
        "description": request.form.get('description'),
        "favorite food": request.form.get('favorite'),
        "type": request.form.get('type'),
        "amount": request.form.get('amount'),
        "expiration": request.form.get('expiration')
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

#Shows ingredients
@app.route("/pantry/ingredients")
def ingredients_show():
    return render_template("show_ingredients.html", ingredients=ingredients.find())

#Shows item in user's ingredients
@app.route("/pantry/ingredients/<ingredients_item_id>")
def ingredients_item_show(ingredients_item_id):
    ingredients_item = ingredients.find_one({"_id": ObjectId(ingredients_item_id)})
    return render_template("ingredients_item_show.html", ingredients_item=ingredients_item)

#Delete an item from ingredients
@app.route("/pantry/ingredients/<ingredients_item_id>/delete", methods=["POST"])
def ingredients_delete_one(ingredients_item_id):
    ingredients.delete_one({'_id': ObjectId(ingredients_item_id)})
    return redirect(url_for("ingredients_show"))

#Delete all items in ingredients
@app.route("/pantry/ingredients/delete")
def ingredients_delete():
    ingredients.delete_one({"_id": ObjectId(ingredients_item["_id"])})
    return redirect(url_for("ingredients_show"))

#ingredients recipe find
@app.route("/pantry/ingredients/recipes")
def show_recipes():
    ingredient_list = ingredients.find()
    ingredient_names = []
    for ing in ingredient_list:
        ingredient_names.append(ing["name"])
    print (ingredient_names)
    ing_string = ""
    for ing in ingredient_names:
        #removes spaces in item names to search recipes
        if ing.count(" ") > 0:
            ing_list = ing.split()
            ing = ""
            for i in ing_list:
                ing += i
        ing_string += ing + ","
    
    #getting recipe JSON data
    r3 = requests.get("https://api.spoonacular.com/recipes/findByIngredients?ingredients="+ing_string+"&number=8&apiKey=" + spoon_apiKey)
    if r3.status_code == 200:
        recipes = json.loads(r3.content)
    else:
        recipes = None
    print(recipes)

    recipes_description = []
    recipes_URL = []
    calories = []
    carbs = []
    fat = []
    protein = []
    for recipe in recipes:
        r4 = requests.get("https://api.spoonacular.com/recipes/"+str(recipe["id"])+"/summary?apiKey=" + spoon_apiKey)
        if r4.status_code == 200:
            recipes_description.append(json.loads(r4.content)["summary"])
        else:
            recipes_description = None

    for recipe in recipes:
        r5 = requests.get("https://api.spoonacular.com/recipes/"+str(recipe["id"])+"/information?includeNutrition=false&apiKey=" + spoon_apiKey)
        if r5.status_code == 200:
            recipes_URL.append(json.loads(r5.content)["sourceUrl"])
        else:
            recipes_URL = None

    for recipe in recipes:
        r6 = requests.get("https://api.spoonacular.com/recipes/"+str(recipe["id"])+"/nutritionWidget.json?apiKey=" + spoon_apiKey)
        if r6.status_code == 200:
            calories.append(json.loads(r6.content)["calories"])
            carbs.append(json.loads(r6.content)["carbs"])
            fat.append(json.loads(r6.content)["fat"])
            protein.append(json.loads(r6.content)["protein"])

        else:
            calories = None
            carbs = None
            fat = None
            protein = None

    return render_template("recipes.html", recipes=recipes,recipes_description=recipes_description,recipes_URL=recipes_URL,calories=calories,carbs=carbs,fat=fat,protein=protein)

# #add recipe to recipe collection
# @app.route("/pantry/saved-recipes", methods=['POST', 'GET'])
# def saved_recipes():
#     recipe_item = pantry.find_one({"_id": ObjectId(recipe_item_id)})
#     new_recipe = {
#         "name": recipe.title,
#         "image":recipe.image,
#         "description": recipes_description[loop.index-1],
#         "link": recipes_URL[loop.index-1]
#         }
#     print(new_recipe)
#     recipes.insert_one(new_recipe)
#     return render_template("saved_recipes.html")


#Add item to ingredients
@app.route('/pantry/<ingredients_item_id>/add-to-ingredients', methods=['POST'])
def add_to_ingredients(ingredients_item_id):
    ingredients_item = pantry.find_one({"_id": ObjectId(ingredients_item_id)})
    new_item = {
        "name": ingredients_item['name'],
        "image": ingredients_item['image'],
        "type": ingredients_item['type'],
        "amount": ingredients_item['amount'],
        "expiration": ingredients_item['expiration']
        }
    ingredients.insert_one(new_item)
    return redirect(url_for('ingredients_show'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
