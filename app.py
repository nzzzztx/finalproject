import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, render_template, request
from pymongo import MongoClient

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)


@app.route('/daftaradmin')
def daftaradmin():
    return render_template('daftaradmin.html')


@app.route('/daftarvisitor')
def daftarvisitor():
    return render_template('daftarvisitor.html')


@app.route('/editbuku')
def editbuku():
    return render_template('editbuku.html')


@app.route('/homeadmin')
def homeadmin():
    return render_template('homeadmin.html')


@app.route('/homevisitor')
def homevisitor():
    return render_template('homevisitor.html')


@app.route('/')
def login():
    return render_template('index.html')


@app.route('/keranjang')
def keranjang():
    return render_template('keranjang.html')


@app.route('/listbuku')
def list():
    return render_template('list.html')


@app.route('/belibuku')
def belibuku():
    return render_template('pembelian.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/tambahbuku')
def tambahbuku():
    return render_template('tambahbuku.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
