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

category1 = Category(name="Cricket")
session.add(category1)
session.commit()

category2 = Category(name="Hockey")
session.add(category2)
session.commit()

category3 = Category(name="Football")
session.add(category3)
session.commit()

category4 = Category(name="Tennis")
session.add(category4)
session.commit()

category5 = Category(name="Baseball")
session.add(category5)
session.commit()

category6 = Category(name="Biking")
session.add(category6)
session.commit()
