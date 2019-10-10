from flask import Flask,request
import requests
import json

app = Flask(__name__)
@app.route('/')
def index():
    x=9
if __name__ == '__main__':
    app.run(debug=True)
