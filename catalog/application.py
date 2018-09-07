from flask import Flask, render_template, request, redirect
from flask import flash, jsonify, url_for
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from cat_setup import Base, Instrument, CatalogItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Music Instruments Catalog Application"


# Connect to Database and create database session
engine = create_engine(
    'sqlite:///instrumentswithusers.db?check_same_thread=False')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome to the best Instruments Catalog, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs points definition to view Instruments Information
@app.route('/instruments/JSON')
def instrumentsJSON():
    instruments = session.query(Instrument).all()
    return jsonify(instruments=[r.serialize for r in instruments])


@app.route('/instruments/<int:instrument_id>/catalog/JSON')
def instrumentCatalogJSON(instrument_id):
    instrument = session.query(Instrument).filter_by(id=instrument_id).one()
    items = session.query(CatalogItem).filter_by(
        instrument_id=instrument_id).all()
    return jsonify(CatalogItems=[i.serialize for i in items])


@app.route('/instruments/<int:instrument_id>/catalog/'
           '<int:item_id>/JSON')
def catalogItemJSON(instrument_id, item_id):
    item = session.query(CatalogItem).filter_by(
            instrument_id=instrument_id).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


# All instruments in the DB to be displayed
@app.route('/')
@app.route('/instruments/')
def showInstruments():
    instruments = session.query(Instrument).order_by(asc(Instrument.name))
    if 'username' not in login_session:
        return render_template('publicinstruments.html',
                               instruments=instruments)
    else:
        return render_template('instruments.html', instruments=instruments)


# Create a new Instrument Category
@app.route('/instruments/new/', methods=['GET', 'POST'])
def newInstrument():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newInstrument = Instrument(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newInstrument)
        flash('New Instrument %s Successfully Created' % newInstrument.name)
        session.commit()
        return redirect(url_for('showInstruments'))
    else:
        return render_template('newInstrument.html')


# Edit an Instrument category
@app.route('/instrument/<int:instrument_id>/edit/', methods=['GET', 'POST'])
def editInstrument(instrument_id):
    editedInstrument = session.query(
        Instrument).filter_by(id=instrument_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedInstrument.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to edit this instrument category. Please create your own "
                "instrument category in order to edit.');}</script><body "
                "onload='myFunction()'>")
    if request.method == 'POST':
        if request.form['name']:
            editedInstrument.name = request.form['name']
            flash('Instrument Category Successfully Edited %s'
                  % editedInstrument.name)
            return redirect(url_for('showInstruments'))
    else:
        return render_template('editinstrument.html',
                               instrument=editedInstrument)


# Delete an Instrument category
@app.route('/instrument/<int:instrument_id>/delete/', methods=['GET', 'POST'])
def deleteInstrument(instrument_id):
    instrumentToRemove = session.query(
        Instrument).filter_by(id=instrument_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if instrumentToRemove.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to delete this instrument. Please create your own instrument "
                "in order to delete.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        session.delete(instrumentToRemove)
        flash('%s Successfully Deleted' % instrumentToRemove.name)
        session.commit()
        return redirect(url_for('showInstruments',
                        instrument_id=instrument_id))
    else:
        return render_template('deleteInstrument.html',
                               instrument=instrumentToRemove)


# Show the items within the instrument category
@app.route('/instruments/<int:instrument_id>/')
@app.route('/instruments/<int:instrument_id>/catalogitem/')
def showCatalogItem(instrument_id):
    instrument = session.query(Instrument).filter_by(id=instrument_id).one()
    creator = getUserInfo(instrument.user_id)
    items = session.query(CatalogItem).filter_by(
        instrument_id=instrument_id).all()
    if 'username' not in login_session or \
            creator.id != login_session['user_id']:
        return render_template('publiccatalogitem.html', items=items,
                               instrument=instrument, creator=creator)
    else:
        return render_template('catalogitem.html', items=items,
                               instrument=instrument, creator=creator)


# Create a new item within the instrument category
@app.route('/instrument/<int:instrument_id>/catalogitem/new/',
           methods=['GET', 'POST'])
def newCatalogItem(instrument_id):
    if 'username' not in login_session:
        return redirect('/login')
    instrument = session.query(Instrument).filter_by(id=instrument_id).one()
    if login_session['user_id'] != instrument.user_id:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to add catalog items to this Instrument Category. Please "
                "create your own instrument Category in order to add "
                "items.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        print "I'm here"
        newItem = CatalogItem(name=request.form['name'],
                              description=request.form['description'],
                              price=request.form['price'],
                              warranty=request.form['warranty'],
                              picture=request.form['picture'],
                              instrument_id=instrument_id,
                              user_id=instrument.user_id)
        session.add(newItem)
        session.commit()
        flash('New Catalog %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showCatalogItem',
                        instrument_id=instrument_id))
    else:
        return render_template('newcatalogitem.html',
                               instrument_id=instrument_id)


# Edit an item within the instrument category
@app.route('/instrument/<int:instrument_id>/catalogitem/<int:catalogitem_id>'
           '/edit', methods=['GET', 'POST'])
def editCatalogItem(instrument_id, catalogitem_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CatalogItem).filter_by(id=catalogitem_id).one()
    instrument = session.query(Instrument).filter_by(id=instrument_id).one()
    if login_session['user_id'] != instrument.user_id:
        return ("<script>function myFunction() {alert('You are not "
                "authorized to edit catalog items in this instrument "
                "category. Please create your own instrument category "
                "in order to edit items.');}</script><body "
                "onload='myFunction()'>")
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['warranty']:
            editedItem.warranty = request.form['warranty']
        if request.form['picture']:
            editedItem.picture = request.form['picture']
        session.add(editedItem)
        session.commit()
        flash('Catalog Item Successfully Edited')
        return redirect(url_for('showCatalogItem',
                        instrument_id=instrument_id))
    else:
        return render_template('editcatalogitem.html',
                               instrument_id=instrument_id,
                               catalogitem_id=catalogitem_id,
                               item=editedItem)


# Delete an item within the instrument category
@app.route('/instrument/<int:instrument_id>/catalogitem/<int:catalogitem_id>'
           '/delete', methods=['GET', 'POST'])
def deleteCatalogItem(instrument_id, catalogitem_id):
    if 'username' not in login_session:
        return redirect('/login')
    instrument = session.query(Instrument).filter_by(id=instrument_id).one()
    itemToRemove = session.query(CatalogItem).filter_by(
                   id=catalogitem_id).one()
    print itemToRemove.instrument_id
    if login_session['user_id'] != instrument.user_id:
        return ("<script>function myFunction() {alert('You are not "
                "authorized to delete catalog items from this instrument "
                "category. Please create your own instrument category in "
                "order to delete.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        session.delete(itemToRemove)
        session.commit()
        flash('Catalog Item Successfully Deleted')
        return redirect(url_for('showCatalogItem',
                        instrument_id=instrument_id))
    else:
        return render_template('deletecatalogitem.html', item=itemToRemove)


# Disconnect based on third-party authentication provider (Google)
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showInstruments'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showInstruments'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
