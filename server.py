from flask import Flask, render_template, request, redirect, jsonify, url_for
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

app = Flask('__name__')

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

def getCategories():
    return session.query(Category).all()


@app.route('/')
@app.route('/catalog')
@app.route('/catalog/')
def showCatalog():
    return render_template('index.html', categories=getCategories())

@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/items/')
def showItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return render_template('items.html', items=items, category=category)

@app.route('/catalog/<int:category_id>/JSON')
@app.route('/catalog/<int:category_id>/items/JSON')
def categoryMenuJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/category/<int:category_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(category_id, menu_id):
    Item = session.query(Item).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/catalog/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Catalog=[r.serialize for r in categories])



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
