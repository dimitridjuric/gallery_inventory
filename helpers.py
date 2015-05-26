from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from gallerydatabase_setup import Base, Galleries, Inventory, User

engine = create_engine('postgresql:///gallerydbwithusers')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def search_db(term):
    '''search the db for artworks having the search term (the argument) in
    either the artist name or the artwork title'''
    term = '%'+term+'%'
    results = session.query(Inventory, Galleries).filter(
                Inventory.gallery_id == Galleries.id).filter(or_(
                Inventory.artist.ilike(term), Inventory.title.ilike(term))).all()
    return results


def get_galleries(gallery_id=None):
    '''returns the list of galleries in the db, or if there's a gallery id param,
    returns the gallery object'''
    if gallery_id is None:
        return session.query(Galleries)
    else:
        return session.query(Galleries).filter_by(id=gallery_id).one()


def get_artists(gallery_id=None):
    '''return a list of all the artist names in the db, or if there's a gallery_id
    returns all the artists having works in the gallery'''
    if gallery_id is None:
        return session.query(Inventory.artist).group_by(Inventory.artist).\
            order_by(Inventory.artist).all()
    else:
        return session.query(Inventory.artist).filter_by(gallery_id=gallery_id).\
            group_by(Inventory.artist).order_by(Inventory.artist).all()


def get_artworks(artist_name=None, gallery_id=None):
    '''returns a list of the artworks for a specific artist or a specific gallery.
    If both parameters are present, the function returns a list of
    artworks for the artist in the gallery inventory, if there's no gallery_id
    the function returns a list of all the artwork in the db for the artist and
    if there no artist the function return all the artworks in the gallery
    inventory'''
    if gallery_id is None:
        artworks = session.query(Inventory, Galleries).\
                join(Galleries).filter(Inventory.artist==artist_name).\
                values(Inventory.title, Inventory.date, Inventory.medium, Galleries.name)
    elif artist_name is None:
        artworks = session.query(Inventory).filter_by(gallery_id=gallery_id)
    else:
        artworks = session.query(Inventory).filter(and_(Inventory.gallery_id\
                    == gallery_id, Inventory.artist == artist_name))
    return artworks


def get_artwork(item_id):
    "return a specific artwork"
    return session.query(Inventory).filter_by(id=item_id).one()


def create_gallery(form, user_id):
    '''create a new gallery using the form. the administrator of the gallery
    is user_id'''
    newGallery = Galleries(name=form['name'],
                           address=form['address'],
                           times=form['times'],
                           url=form['url'],
                           user_id=user_id)
    session.add(newGallery)
    session.commit()


def edit_gallery(form, gallery):
    '''edit a gallery using the form passed'''
    if form['name']:
        gallery.name = form['name']
    if form['address']:
        gallery.address = form['address']
    if form['times']:
        gallery.times = form['times']
    if form['url']:
        gallery.url = form['url']
    session.add(gallery)
    session.commit()


def delete_gallery(gallery, items):
    '''delete a gallery from the db'''
    # first delete all the artworks of the gallery from the database
    for item in items:
        session.delete(item)
    # then delete the gallery from the DB
    session.delete(gallery)
    session.commit()


def new_artwork(form, gallery_id):
    '''create a new artwork in the inventory of gallery_id'''
    newItem = Inventory(title=form['title'],
                        artist=form['artist'],
                        date=form['date'],
                        dimensions=form['dimensions'],
                        medium=form['medium'],
                        ondisplay=form['ondisplay'],
                        imgurl=form['imgurl'],
                        gallery_id=gallery_id)
    session.add(newItem)
    session.commit()


def edit_artwork(form, item):
    '''edit an artwork'''
    if form['title']:
        item.title = form['title']
    if form['artist']:
        item.artist = form['artist']
    if form['date']:
        item.date = form['date']
    if form['dimensions']:
        item.dimensions = form['dimensions']
    if form['medium']:
        item.medium = form['medium']
    if form['ondisplay']:
        item.ondisplay = form['ondisplay']
    if form['imgurl']:
        item.imgurl = form['imgurl']
    session.add(item)
    session.commit()


def delete_artwork(item):
    '''delete an artwork from the db'''
    session.delete(item)
    session.commit()


# Helper functions for authentication


def createUser(login_session):
    '''Creates a new user in the database with the name, email,
    and picture from the login_session'''
    newUser = User(name=login_session['username'], email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    '''gets a user info from the database'''
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserId(email):
    '''gets a user id from the database, or returns None if the user doesn't
    exist'''
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None