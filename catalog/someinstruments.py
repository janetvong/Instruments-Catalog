from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cat_setup import Instrument, Base, CatalogItem, User

engine = create_engine('sqlite:///instrumentswithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create my user profile
User1 = User(name="Jhon Diaz", email="jfd2124@columbia.edu",
             picture='http://localhost:8000/static/jhon-small.jpg')

session.add(User1)
session.commit()

# Guitars Category
instrument1 = Instrument(user_id=1, name="Guitars")

session.add(instrument1)
session.commit()

# Guitars catalog items
catalogItem1 = CatalogItem(user_id=1, name="Acoustic Guitar",
                           description="Wooden acoustic guitar",
                           price="$127.50", warranty="Two years",
                           picture='http://localhost:8000/static/images/'
                           'acoustic-guitar.jpeg', instrument=instrument1)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, name="Professional Electrical Guitar",
                           description="Electrical guitar from Aerosmith",
                           price="$1027.50", warranty="Six months",
                           picture='http://localhost:8000/static/images/'
                           'electric-guitar.jpeg', instrument=instrument1)

session.add(catalogItem2)
session.commit()

# Keyboards category
instrument2 = Instrument(user_id=1, name="Keyboards")

session.add(instrument2)
session.commit()

# Keyboards catalog items
catalogItem1 = CatalogItem(user_id=1, name="Grand Piano",
                           description="Wooden acoustic Piano",
                           price="$25227.50", warranty="1 year",
                           picture='http://localhost:8000/static/'
                           'images/wooden-piano.jpeg', instrument=instrument2)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, name="Digital Piano",
                           description="Digital Piano",
                           price="$1027.50", warranty="No",
                           picture='http://localhost:8000/static/'
                           'images/keyboard.jpg', instrument=instrument2)

session.add(catalogItem2)
session.commit()

print "Added Instruments"
