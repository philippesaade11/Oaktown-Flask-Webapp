from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials", "Access-Control-Allow-Origin", "Access-Control-Allow-Headers", "x-access-token"], supports_credentials=True)
db = SQLAlchemy(app)

class Admin(db.Model):
    __tablename__ = "Admin"
    username = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(65))
    reservation = db.relationship('Reservation', backref='Admin', lazy="dynamic")


class Reservation(db.Model):
    __tablename__ = 'Reservation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    numPeople = db.Column(db.Integer)
    moreInfo = db.Column(db.String(500))
    isPicnic = db.Column(db.Boolean, default=False)
    isCamping = db.Column(db.Boolean, default=False)
    isResto = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    added_date = db.Column(db.BigInteger)
    added_by = db.Column(db.String(100), db.ForeignKey('Admin.username'))
    picnic = db.relationship('Picnic', backref='Reservation', lazy="dynamic")
    camping = db.relationship('Camping', backref='Reservation', lazy="dynamic")
    resto = db.relationship('Resto', backref='Reservation', lazy="dynamic")

class Picnic(db.Model):
    __tablename__ = 'Picnic'
    id = db.Column(db.Integer, primary_key=True)
    res_id = db.Column(db.Integer, db.ForeignKey('Reservation.id'))
    table = db.Column(db.String(100), default="")
    withBBQ = db.Column(db.Boolean, default=False)
    date = db.Column(db.BigInteger)
    pricePerson = db.Column(db.Integer)

class Camping(db.Model):
    __tablename__ = 'Camping'
    id = db.Column(db.Integer, primary_key=True)
    res_id = db.Column(db.Integer, db.ForeignKey('Reservation.id'))
    table = db.Column(db.String(100), default="")
    withBBQ = db.Column(db.Boolean, default=False)
    withTent = db.Column(db.Boolean, default=False)
    withMatress = db.Column(db.Boolean, default=False)
    withFood = db.Column(db.Boolean, default=False)
    fromDate = db.Column(db.BigInteger)
    toDate = db.Column(db.BigInteger)
    pricePerson = db.Column(db.Integer)

class Resto(db.Model):
    __tablename__ = 'Resto'
    id = db.Column(db.Integer, primary_key=True)
    res_id = db.Column(db.Integer, db.ForeignKey('Reservation.id'))
    table = db.Column(db.String(100), default="")
    date = db.Column(db.BigInteger)
    priceTotal = db.Column(db.Integer)

class Costs(db.Model):
    __tablename__ = 'Costs'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    moreInfo = db.Column(db.String(500))

def add_admin():
    import getpass
    from hashlib import sha256

    username = input("Input Username: ")
    password = getpass.getpass("Input password: ")
    password2 = getpass.getpass("Confirm password: ")

    if(password != password2):
        print("Password Don't Match")
    else:
        password = sha256(password.encode()).hexdigest()
        password = sha256(password.encode()).hexdigest()
        admin = Admin.query.filter_by(username=username).first()
        if(not admin):
            admin = Admin(username=username, password=password)
            db.session.add(admin)
            db.session.commit()
        else:
            admin.password = password
            db.session.commit()

