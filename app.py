import os
from os.path import join, dirname
from dotenv import load_dotenv
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
)
import json
from bson import ObjectId
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

SECRET_KEY = "SPARTA"

TOKEN_KEY = 'mytoken'


@app.route('/daftarvisitor')
def daftarvisitor():
    return render_template('daftarvisitor.html')


@app.route('/daftaradmin')
def daftaradmin():
    return render_template('daftaradmin.html')


@app.route('/homeadmin')
def homeadmin():
    return render_template('homeadmin.html')


@app.route('/homevisitor')
def homevisitor():
    try:
        # Retrieve reviews from the database
        reviews = list(db.reviews.find())

        return render_template('homevisitor.html', reviews=reviews)
    except Exception as e:
        return render_template('homevisitor.html', error=str(e))

@app.route('/add_review', methods=['POST'])
def add_review():
    try:
        nama = request.form.get('nama')
        ulasan = request.form.get('ulasan')

        # Simpan ulasan ke database
        db.reviews.insert_one({'nama': nama, 'ulasan': ulasan})

        return jsonify({'result': 'success', 'msg': 'Review added successfully'})
    except Exception as e:
        return jsonify({'result': 'fail', 'msg': f'Error adding review: {str(e)}'})
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


@app.route('/editbuku')
def editbukumain():
    return render_template('editbuku.html')


@app.route("/")
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('homevisitor.html', user_info=user_info)

    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired!'
        return redirect(url_for("login", msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in!'
        return redirect(url_for("login", msg=msg))


@app.route("/login")
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)


@app.route("/user/<username>")
def user(username):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        status = username == payload["id"]
        user_info = db.users.find_one({
            "username": username},
            {"_id": False}
        )
        return render_template(
            "user.html",
            user_info=user_info,
            status=status
        )
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/sign_in", methods=["POST"])
def sign_in():
    # Sign in
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )
    if result:
        payload = {
            "id": username_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    # Let's also handle the case where the id and
    # password combination cannot be found
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )


@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(
        password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # id
        "password": password_hash,                                  # password
        # user's name is set to their id by default
        "profile_name": username_receive,
        # profile image file name
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # a default profile image
        # a profile description
        "profile_info": ""
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# jinja


def get_all_products():
    products = db.products.find()
    return products


def get_product_details(product_id):
    product = db.products.find_one({'_id': ObjectId(product_id)})
    return product


def add_product(name, price):
    db.products.insert_one({'name': name, 'price': price})


def update_product(product_id, name, price):
    db.products.update_one({'_id': ObjectId(product_id)}, {
                           '$set': {'name': name, 'price': float(price)}})


def delete_product(product_id):
    db.products.delete_one({'_id': ObjectId(product_id)})


@app.route('/daftarbukuadmin')
def index():
    products = get_all_products()
    return render_template('daftaradmin.html', products=products)


@app.route('/add', methods=['GET', 'POST'])
def add_product_page():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        add_product(name, price)
        return redirect(url_for('index'))
    return render_template('tambahbuku.html')


@app.route('/edit/<string:product_id>', methods=['GET', 'POST'])
def edit_product_page(product_id):
    product = get_product_details(product_id)
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        update_product(product_id, name, price)
        return redirect(url_for('index'))
    return render_template('editbuku.html', product=product)


@app.route('/delete/<string:product_id>')
def delete_product_page(product_id):
    delete_product(product_id)
    return redirect(url_for('index'))


@app.route('/get_product/<string:product_id>')
def get_product(product_id):
    product = get_product_details(product_id)
    if product:
        return jsonify(product)
    else:
        return jsonify({'error': 'Product not found'}), 404


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
