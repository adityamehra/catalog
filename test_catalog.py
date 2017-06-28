from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item
#from flask.ext.sqlalchemy import SQLAlchemy
from random import randint
import datetime
import random


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def myTests():
    '''Checks if the cascade worked fine'''

    # getting first item from first category
    item = session.query(Item).first()
    print "Testing READ 1 - "
    print item.id
    print item.name
    print item.category_id
    print ""

    # deleting first category, items should get deleted too
    print "Deleting category 1..."
    categoryToDelete = session.query(Category).filter_by(id=1).one()
    session.delete(categoryToDelete)
    session.commit()
    print "If cascade worked, items should be deleted along-with the category"
    print ""

    # should return first item of second category
    item = session.query(Item).first()
    print "Testing READ 2 - "
    print item.id
    print item.name
    print item.category_id
    print ""

    # deleting first item of second category
    itemToDelete = session.query(Item).filter_by(category_id=2).first()
    print "Deleting first item from category 2 - "
    session.delete(itemToDelete)
    session.commit()
    print ""

    # deleting item should not delete category
    print "Showing category 2..."
    category = session.query(Category).filter_by(id=2).one()
    print category.id
    print category.name
    print "If cascade worked, category should show"
    print ""

    # show second item which became first
    item = session.query(Item).filter_by(category_id=2).first()
    print "Testing READ 2 - "
    print item.id
    print item.name
    print item.category_id
    print ""

myTests()
