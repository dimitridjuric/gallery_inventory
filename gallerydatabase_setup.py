import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):

    __tablename__ = 'user'
    
    name = Column(
        String(250),
        nullable=False)
    id = Column(
        Integer,
        primary_key=True)
    email = Column(
        String(250),
        nullable=False)
    picture = Column(
        String(250))
    
    
class Galleries(Base):
    
    __tablename__ = 'galleries'
    
    name = Column(
        String(80),
        nullable=False)
    id = Column(
        Integer,
        primary_key=True)
    address = Column(
        String(250))
    times = Column(
        String(250))
    url = Column(
        String(80))
    user_id = Column(
        Integer,
        ForeignKey('user.id'))
    user = relationship(User)
    
    @property
    def serialize(self):
        return {
            'name': self.name,
            'address': self.address,
            'times': self.times,
            'url': self.url
        }

    
class Inventory(Base):
    
    __tablename__ = 'inventory'
    
    title = Column(
        String(80),
        nullable=False)
    artist = Column(
        String(80),
        nullable=False)
    id = Column(
        Integer,
        primary_key=True)
    date = Column(
        String(80))
    dimensions = Column(
        String(80))
    medium = Column(
        String(80))
    ondisplay = Column(
        String(80))
    imgurl = Column(
        String(80))
    gallery_id = Column(
        Integer,
        ForeignKey('galleries.id'))
    galleries = relationship(Galleries)
    
    @property
    def serialize(self):
        return {
            'title': self.title,
            'artist': self.artist,
            'date': self.date,
            'dimensions': self.dimensions,
            'medium': self.medium,
            'ondisplay': self.ondisplay
        }

    
engine = create_engine('postgresql:///gallerydbwithusers')
Base.metadata.create_all(engine)