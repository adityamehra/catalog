from flask import Flask, render_template, request, redirect, jsonify, url_for
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

#import for create login request on client side
from flask import session as login_session
import random
import string

# import to handle login request on server side
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, flash
import requests

# HTML sanitizing library that escapes or strips markup and attributess
import bleach


app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog"

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# function to get all the categories
def getCategories():
    return session.query(Category).all()

# route for login
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
        # print "if result.get('error') is not None:"
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        # print "if result['user_id'] != gplus_id:"
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

    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        login_session.clear()
        # Re-direct to /catalog when disconnect
        return redirect('/catalog')
    else:
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

@app.route('/')
@app.route('/catalog')
@app.route('/catalog/')
def showCatalog():
    if 'username' not in login_session:
        return render_template('index_signin.html', categories=getCategories())
    else:
        return render_template('index_signout.html', categories=getCategories(), login_session=login_session)

@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/items/')
def showItems(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
        items = session.query(Item).filter_by(
            category_id=category_id).all()
        if 'username' not in login_session:
            return render_template('items_signin.html', items=items, category=category)
        else:
            return render_template('items_signout.html', items=items, category=category, login_session=login_session)
    except:
        return "No category with id %s. Please try a valid category id." % category_id

# CRUD operations for Category
@app.route('/catalog/add_category/', methods=['GET', 'POST'])
def addCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            category = Category(name=bleach.clean(request.form['name']))
            session.add(category)
            session.commit()
        # flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect('/catalog')
    else:
        return render_template('categoryToAdd.html', login_session=login_session)

@app.route('/catalog/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    categoryToEdit = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        categoryToEdit.name = bleach.clean(request.form['name'])
        session.add(categoryToEdit)
        session.commit()
        return redirect('/')
    else:
        return render_template('categoryToEdit.html', category=categoryToEdit, login_session=login_session)

@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect('/')
    else:
        return render_template('categoryToDelete.html', category=categoryToDelete, login_session=login_session)

# CRUD operations for items
@app.route('/catalog/<int:category_id>/item/add/', methods=['GET', 'POST'])
def addItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            newItem = Item(name=bleach.clean(request.form['name']), description=bleach.clean(request.form['description']),
                           price='$' + bleach.clean(request.form['price']), size=bleach.clean(request.form['size']), category=category)
            session.add(newItem)
            session.commit()
        # flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect('/catalog/%s/items/' % category.id)
    else:
        return render_template('itemToAdd.html', category=category, login_session=login_session)

@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    itemToEdit = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.name = bleach.clean(request.form['name'])
        if request.form['description']:
            itemToEdit.description = bleach.clean(request.form['description'])
        if request.form['price']:
            itemToEdit.price = bleach.clean(request.form['price'])
        if request.form['size']:
            itemToEdit.size = bleach.clean(request.form['size'])
        session.add(itemToEdit)
        session.commit()
        return redirect('/catalog/%s/items/' % category.id)
    else:
        return render_template('itemToEdit.html', item=itemToEdit, category=category, login_session=login_session)

@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect('/catalog/%s/items/' % category.id)
    else:
        return render_template('itemToDelete.html', item=itemToDelete, category=category,login_session=login_session)

# Routes for JSON endpoints

# JSON endpoint to view all categories/sports in the catalog
@app.route('/catalog/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Catalog=[r.serialize for r in categories])

# JSON endpoint to view all items in a category
@app.route('/catalog/<int:category_id>/JSON')
@app.route('/catalog/<int:category_id>/items/JSON')
def categoryItemsJSON(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
        items = session.query(Item).filter_by(category_id=category_id).all()
        return jsonify(Items=[i.serialize for i in items])
    except:
        return "No category with id %s. Please try a valid category id." % category_id

# JSON endpoint to view a particular item in a category/sport
@app.route('/catalog/<int:category_id>/item/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    try:
        item = session.query(Item).filter(Item.id == item_id, Item.category_id == category_id).one()
        print item
        return jsonify(Item=item.serialize)
    except:
        return "Please try a valid category id and item id combination."

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
