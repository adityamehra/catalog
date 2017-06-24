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
def showCatalog():
    return render_template('index.html', categories=getCategories())


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
