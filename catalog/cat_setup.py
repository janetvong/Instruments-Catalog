from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# Create User class to define profile of catalog user
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# Create Instrument class that will identify Instrument Categories
class Instrument(Base):
    __tablename__ = 'instrument'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'name': self.name,
           'id': self.id,
           }


# Create CatalogItem class for each item within Instrument categories
class CatalogItem(Base):
    __tablename__ = 'catalog_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    warranty = Column(String(20))
    picture = Column(String(250))
    instrument_id = Column(Integer, ForeignKey('instrument.id'))
    instrument = relationship(Instrument)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'name': self.name,
           'description': self.description,
           'id': self.id,
           'price': self.price,
           'warranty': self.warranty,
           'picture': self.picture,
           }

engine = create_engine('sqlite:///instrumentswithusers.db')


Base.metadata.create_all(engine)
