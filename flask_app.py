from database import db, app, Admin, Reservation, Picnic, Camping, Resto
from flask import request, jsonify, render_template
import jwt
import datetime
import time
from hashlib import sha256
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return error('Token is missing!')
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            admin = Admin.query.filter_by(username=data['username']).first()
            if(not admin):
                return error("Admin not found")
        except:
            return error('Token is invalid!')
        return f(admin, *args, **kwargs)
    return decorated

#Home
@app.route('/', methods = ['GET'])
def home():
    return render_template('index.html')

#Check Token
@app.route('/checkToken', methods = ['POST'])
@token_required
def checkToken(admin):
    return admin.username

#Admin Login
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.authorization:
        username = request.authorization.username
        password = request.authorization.password
        if(username and password):
            admin = Admin.query.filter_by(username=username).first()
            if(not admin):
                return error('Admin not found')
            if(admin.password != sha256(password.encode()).hexdigest()):
                return error('Wrong password')
            token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=20)}, app.config['SECRET_KEY'])
            return jsonify({'token' : token.decode("UTF-8")})
        return error('Missing prameters')
    return error('Send authentication')

@app.route('/addReservation', methods = ['POST'])
@token_required
def addReservation(admin):
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        numPeople = int(request.form['numPeople'])
        moreInfo = request.form['moreInfo']
        added_date = int(time.time())
        added_by = admin.username
        mytype = int(request.form['type'])

        if(name and phone and numPeople>0 and (mytype in range(1,4))):
            if(mytype == 1):
                table = request.form['table']
                withBBQ = strtobool(request.form['withBBQ'])
                date = int(request.form['date'])
                pricePerson = int(request.form['pricePerson'])
                if(date and pricePerson):
                    res = Reservation(name = name, phone = phone, numPeople = numPeople, moreInfo = moreInfo, isPicnic=True, isCamping=False, isResto=False, added_date = added_date, added_by = added_by)
                    db.session.add(res)
                    db.session.commit()
                    p = Picnic(table = table, withBBQ = withBBQ, date = date, pricePerson = pricePerson, res_id = res.id)
                    db.session.add(p)
                    db.session.commit()
                    return "1"

            if(mytype == 2):
                table = request.form['table']
                withBBQ = strtobool(request.form['withBBQ'])
                withMatress = strtobool(request.form['withMatress'])
                withTent = strtobool(request.form['withTent'])
                withFood = strtobool(request.form['withFood'])
                fromDate = int(request.form['fromDate'])
                toDate = int(request.form['toDate'])
                pricePerson = int(request.form['pricePerson'])
                if(fromDate and toDate and fromDate <= toDate and pricePerson):
                    res = Reservation(name = name, phone = phone, numPeople = numPeople, moreInfo = moreInfo, isPicnic=False, isCamping=True, isResto=False, added_date = added_date, added_by = added_by)
                    db.session.add(res)
                    db.session.commit()
                    c = Camping(table = table, withBBQ = withBBQ, withMatress = withMatress, withTent = withTent, withFood = withFood, fromDate = fromDate, toDate = toDate, pricePerson = pricePerson, res_id = res.id)
                    db.session.add(c)
                    db.session.commit()
                    return "1"

            if(mytype == 3):
                table = request.form['table']
                date = int(request.form['date'])
                if(date):
                    res = Reservation(name = name, phone = phone, numPeople = numPeople, moreInfo = moreInfo, isPicnic=False, isCamping=False, isResto=True, added_date = added_date, added_by = added_by)
                    db.session.add(res)
                    db.session.commit()
                    r = Resto(table = table, date = date, res_id = res.id)
                    db.session.add(r)
                    db.session.commit()
                    return "1"

        return error("Missing parameters")
    return error("Send POST request")

@app.route('/changeReservation', methods = ['POST'])
@token_required
def changeReservation(admin):
    if request.method == 'POST':
        id = int(request.form['id'])
        name = request.form['name']
        phone = request.form['phone']
        numPeople = int(request.form['numPeople'])
        moreInfo = request.form['moreInfo']
        res = db.session.query(Reservation).filter(Reservation.id == id).first()

        if(res and name and phone and numPeople>0):
            res.name = name
            res.phone = phone
            res.numPeople = numPeople
            res.moreInfo = moreInfo

            if(res.isPicnic):
                table = request.form['table']
                withBBQ = strtobool(request.form['withBBQ'])
                date = int(request.form['date'])
                pricePerson = int(request.form['pricePerson'])
                if(date and pricePerson):
                    p = db.session.query(Picnic).filter(Picnic.res_id == id).first()
                    p.table = table
                    p.withBBQ = withBBQ
                    p.date = date
                    p.pricePerson = pricePerson
                    db.session.commit()
                    return "1"

            if(res.isCamping):
                table = request.form['table']
                withBBQ = strtobool(request.form['withBBQ'])
                withMatress = strtobool(request.form['withMatress'])
                withTent = strtobool(request.form['withTent'])
                withFood = strtobool(request.form['withFood'])
                fromDate = int(request.form['fromDate'])
                toDate = int(request.form['toDate'])
                pricePerson = int(request.form['pricePerson'])
                if(fromDate and toDate and fromDate <= toDate and pricePerson):
                    c = db.session.query(Camping).filter(Camping.res_id == id).first()
                    c.table = table
                    c.withBBQ = withBBQ
                    c.withMatress = withMatress
                    c.withTent = withTent
                    c.withFood = withFood
                    c.fromDate = fromDate
                    c.toDate = toDate
                    c.pricePerson = pricePerson
                    db.session.commit()
                    return "1"

            if(res.isResto):
                table = request.form['table']
                date = int(request.form['date'])
                if(date):
                    r = db.session.query(Resto).filter(Resto.res_id == id).first()
                    r.table = table
                    r.date = date
                    db.session.commit()
                    return "1"

        return error("Missing parameters")
    return error("Send POST request")

@app.route('/viewReservation', methods = ['POST'])
@token_required
def viewReservation(admin):
    if request.method == 'POST':
        fromDate = request.form['fromDate']
        toDate = request.form['toDate']
        if(ifNone(toDate)):
            toDate = 100000000000
        else: toDate = int(toDate)
        if(ifNone(fromDate)):
            fromDate = 0
        else: fromDate = int(fromDate)

        query_c = db.session.query(Reservation, Camping).filter(Reservation.id == Camping.res_id, Reservation.deleted == False, Reservation.isCamping == 1, db.or_(db.and_(Camping.fromDate >= fromDate, Camping.fromDate <= toDate), db.and_(Camping.toDate >= fromDate, Camping.toDate <= toDate))).all()
        query_p = db.session.query(Reservation, Picnic).filter(Reservation.id == Picnic.res_id, Reservation.deleted == False, Reservation.isPicnic == 1, db.and_(Picnic.date >= fromDate, Picnic.date <= toDate)).all()
        query_r = db.session.query(Reservation, Resto).filter(Reservation.id == Resto.res_id, Reservation.deleted == False, Reservation.isResto == 1, db.and_(Resto.date >= fromDate, Resto.date <= toDate)).all()

        resp = []
        for c in query_c:
            resp.append({"id": c.Reservation.id,
                        "name": c.Reservation.name,
                        "phone": c.Reservation.phone,
                        "numPeople": c.Reservation.numPeople,
                        "moreInfo": c.Reservation.moreInfo,
                        "type": "Camping",
                        "added_date": c.Reservation.added_date,
                        "added_by": c.Reservation.added_by,
                        "fromDate": c.Camping.fromDate,
                        "toDate": c.Camping.toDate,
                        "withBBQ": c.Camping.withBBQ,
                        "withTent": c.Camping.withTent,
                        "withMatress": c.Camping.withMatress,
                        "withFood": c.Camping.withFood,
                        "table": c.Camping.table,
                        "pricePerson": c.Camping.pricePerson})
        for c in query_p:
            resp.append({"id": c.Reservation.id,
                        "name": c.Reservation.name,
                        "phone": c.Reservation.phone,
                        "numPeople": c.Reservation.numPeople,
                        "moreInfo": c.Reservation.moreInfo,
                        "type": "Picnic",
                        "added_date": c.Reservation.added_date,
                        "added_by": c.Reservation.added_by,
                        "date": c.Picnic.date,
                        "withBBQ": c.Picnic.withBBQ,
                        "table": c.Picnic.table,
                        "pricePerson": c.Picnic.pricePerson})
        for c in query_r:
            resp.append({"id": c.Reservation.id,
                        "name": c.Reservation.name,
                        "phone": c.Reservation.phone,
                        "numPeople": c.Reservation.numPeople,
                        "moreInfo": c.Reservation.moreInfo,
                        "type": "Resto",
                        "added_date": c.Reservation.added_date,
                        "added_by": c.Reservation.added_by,
                        "date": c.Resto.date,
                        "table": c.Resto.table})
        return jsonify(resp)
    return error("Send POST request")

@app.route('/deleteReservation', methods = ['POST'])
@token_required
def deleteReservation(admin):
    if request.method == 'POST':
        id = request.form['id']

        res = Reservation.query.filter_by(id = id).one()
        res.deleted = True
        db.session.commit()

        return "1"
    return error("Send POST request")

def ifNone(str):
    return (str==None or str == "" or str.lower() == "nan" or str.lower() == "none")

def error(msg):
    return jsonify({'error': msg}), 401

def strtobool(str):
    if(str.lower() in ["true", "t", 1, "1", "on"]):
        return True
    return False
