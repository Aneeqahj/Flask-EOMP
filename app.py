import hmac
import sqlite3

from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_jwt import JWT, jwt_required


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[2], data[3]))
    return new_data


users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


def init_user_table():
    conn = sqlite3.connect('database.db')
    print('Database opened successfully')

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "full_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")


def init_product_table():
    conn = sqlite3.connect('database.db')
    print('Database opened successfully')

    conn.execute("CREATE TABLE IF NOT EXISTS product(product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "name TEXT NOT NULL,"
                 "price TEXT NOT NULL,"
                 "category TEXT NOT NULL,"
                 "description TEXT NOT NULL)")
    print("product table created successfully")
    conn.close()


init_user_table()
init_product_table()

app = Flask(__name__)
app.debug = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'aneeqahlotto@gmail.com'
app.config['MAIL_PASSWORD'] = 'lotto2021'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
app.config['SECRET_KEY'] = 'super-secret'
CORS(app)

jwt = JWT(app, authenticate, identity)


@app.route("/registration/", methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form["email"]
        password = request.form['password']

        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO user("
                           "full_name,"
                           "username,"
                           "password) VALUES(?, ?, ?)", (full_name, username, password))
            connection.commit()
            response["message"] = "success"
            response["status_code"] = 201

            if response["status_code"] == 201:
                msg = Message('Success', sender='aneeqahlotto@gmail.com', recipients=[email])
                msg.body = "Your registration was successful."
                mail.send(msg)
                return "Message sent"


@app.route('/adding/', methods=['POST'])
@jwt_required()
def add_products():
    response = {}

    if request.method == "POST":
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        description = request.form['description']

        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO product("
                           "name,"
                           "price,"
                           "category,"
                           "description) VALUES(?, ?, ?, ?)", (name, price, category, description))
            connection.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/view/', methods=['GET'])
def view_products():
    response = {}

    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM product")

        products = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = products
    return jsonify(response)


@app.route('/view-one/<int:product_id>/', methods=['GET'])
def view_product(product_id):
    response = {}

    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM product WHERE product_id=?", str(product_id))
        products = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = products
    return response


@app.route('/update/<int:product_id>/', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('database.db') as conn:
            print(request.json)
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("name") is not None:
                put_data["name"] = incoming_data.get("name")
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET name =? WHERE product_id=?", (put_data["name"], product_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200

            elif incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET price =? WHERE product_id=?", (put_data["price"], product_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200

            elif incoming_data.get("category") is not None:
                put_data["category"] = incoming_data.get("category")
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET category =? WHERE product_id=?", (put_data["category"],
                                                                                         product_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200

            elif incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET description =? WHERE product_id=?", (put_data["description"],
                                                                                            product_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200
            return response


@app.route('/delete_product/<int:product_id>/')
@jwt_required()
def delete_product(product_id):
    response = {}

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE product_id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "product deleted successfully."
    return response


if __name__ == "__main__":
    app.run()
    app.debug = True
