from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from gallerydatabase_setup import Base, Galleries, Inventory, User
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('postgresql:///gallerydbwithusers')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Helper functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# public access urls

@app.route('/', methods=['GET', 'POST'])
@app.route('/galleries/', methods=['GET', 'POST'])
def galleryList():
    if request.method == 'POST':
        search = request.form['search']
        if search:
            search = '%'+search+'%'
            results = session.query(Inventory, Galleries).filter(
                Inventory.gallery_id == Galleries.id).filter(or_(
                Inventory.artist.ilike(search), Inventory.title.ilike(search))).all()
            return render_template('search.html', results=results)
    else:
        galleries = session.query(Galleries)
        if 'user_id' in login_session:
            user_id = login_session['user_id']
        else:
            user_id = None
        return render_template('galleries2.html', galleries=galleries, user_id=user_id)


@app.route('/artists/', methods=['GET', 'POST'])
def artistList():
    if request.method == 'POST':
        search = request.form['search']
        if search:
            search = '%'+search+'%'
            results = session.query(Inventory, Galleries).filter(
                Inventory.gallery_id == Galleries.id).filter(or_(
                Inventory.artist.ilike(search), Inventory.title.ilike(search))).all()
            return render_template('search.html', results=results)
    else:
        artists = session.query(Inventory.artist).group_by(Inventory.artist).\
            order_by(Inventory.artist).all()
    return render_template('all_artists.html', artists=artists)


@app.route('/artist_works/<artist_name>', methods=['GET', 'POST'])
def artistWorks(artist_name):
    if request.method == 'POST':
        search = request.form['search']
        if search:
            search = '%'+search+'%'
            results = session.query(Inventory, Galleries).filter(
                Inventory.gallery_id == Galleries.id).filter(or_(
                Inventory.artist.ilike(search), Inventory.title.ilike(search))).all()
            return render_template('search.html', results=results)
    else:
        artworks = session.query(Inventory, Galleries).\
                join(Galleries).filter(Inventory.artist==artist_name).\
                values(Inventory.title, Inventory.date, Inventory.medium, Galleries.name)
        #print [x[0] for x in artworks]
    return render_template('artist_works.html', artist=artist_name, artworks=artworks)


@app.route('/gallery/<int:gallery_id>/')
@app.route('/gallery/<int:gallery_id>/inventory/', methods=['GET', 'POST'])
def galleryInventory(gallery_id):
    gallery = session.query(Galleries).filter_by(id=gallery_id).one()
    items = session.query(Inventory).filter_by(gallery_id=gallery_id)
    if 'username' not in login_session:
        return render_template('public_inventory.html', gallery=gallery, items=items)
    else:
        return render_template('inventory.html', gallery=gallery, items=items)


@app.route('/gallery/<int:gallery_id>/artists/')
def galleryArtists(gallery_id):
    gallery = session.query(Galleries).filter_by(id=gallery_id).one()
    artists = session.query(Inventory.artist).filter_by(gallery_id=gallery_id).\
        group_by(Inventory.artist).order_by(Inventory.artist).all()
    return render_template('artists.html', gallery=gallery, artists=artists)


@app.route('/gallery/<int:gallery_id>/artists/<artist_name>')
def artistInventory(gallery_id, artist_name):
    gallery = session.query(Galleries).filter_by(id=gallery_id).one()
    items = session.query(Inventory).filter(and_(
        Inventory.gallery_id == gallery_id, Inventory.artist == artist_name))
    if 'username' not in login_session:
        return render_template('public_artistinventory.html', items=items,
                           artist=artist_name, gallery=gallery)
    else:
        return render_template('artistinventory.html', items=items,
                           artist=artist_name, gallery=gallery)


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.
                                  digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# the following urls need admin access


@app.route('/gallery/new/', methods=['GET', 'POST'])
def newGallery():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGallery = Galleries(name=request.form['name'],
                               address=request.form['address'],
                               times=request.form['times'],
                               url=request.form['url'],
                               user_id=login_session['user_id'])
        session.add(newGallery)
        session.commit()
        flash('New gallery created')
        return redirect(url_for('galleryList'))
    else:
        return render_template('newgallery.html')


@app.route('/gallery/<int:gallery_id>/edit/', methods=['GET', 'POST'])
def editGallery(gallery_id):
    if 'username' not in login_session:
        return redirect('/login')
    gallery = session.query(Galleries).filter_by(id=gallery_id).one()
    if gallery.user_id != login_session['user_id']:
        response = make_response(json.dumps(
            "You don't have permission to edit this gallery"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    if request.method == 'POST':
        if request.form['name']:
            gallery.name = request.form['name']
        if request.form['address']:
            gallery.address = request.form['address']
        if request.form['times']:
            gallery.times = request.form['times']
        if request.form['url']:
            gallery.url = request.form['url']
        session.add(gallery)
        session.commit()
        flash('Gallery edited')
        return redirect(url_for('galleryList'))
    else:
        return render_template('editgallery.html', gallery=gallery)


@app.route('/gallery/<int:gallery_id>/delete', methods=['GET', 'POST'])
def deleteGallery(gallery_id):
    if 'username' not in login_session:
        return redirect('/login')
    gallery = session.query(Galleries).filter_by(id=gallery_id).one()
    if gallery.user_id != login_session['user_id']:
        response = make_response(json.dumps(
            "You don't have permission to delete this gallery"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    if request.method == 'POST':
        session.delete(gallery)
        session.commit()
        flash('Gallery deleted')
        return redirect(url_for('galleryList'))
    else:
        return render_template('deletegallery.html', gallery=gallery)


@app.route('/gallery/<int:gallery_id>/inventory/new/', methods=['GET', 'POST'])
def newInventoryItem(gallery_id):
    if 'username' not in login_session:
        return redirect('/login')
    gallery = session.query(Galleries).filter_by(id=gallery_id).one()
    if gallery.user_id != login_session['user_id']:
        response = make_response(json.dumps(
            "You don't have permission to add an item to this gallery"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    if request.method == 'POST':
        newItem = Inventory(title=request.form['title'],
                            artist=request.form['artist'],
                            date=request.form['date'],
                            dimensions=request.form['dimensions'],
                            medium=request.form['medium'],
                            ondisplay=request.form['ondisplay'],
                            imgurl=request.form['imgurl'],
                            gallery_id=gallery_id)
        session.add(newItem)
        session.commit()
        flash('New artwork added')
        return redirect(url_for('galleryInventory', gallery_id=gallery_id))
    else:
        gallery = session.query(Galleries).filter_by(id=gallery_id).one()
        return render_template('newitem.html', gallery=gallery)


@app.route('/gallery/<int:gallery_id>/inventory/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editInventoryItem(gallery_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    gallery = session.query(Galleries).filter_by(id=gallery_id).one()
    if gallery.user_id != login_session['user_id']:
        response = make_response(json.dumps(
            "You don't have permission to edit items for this gallery"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    item = session.query(Inventory).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['title']:
            item.title = request.form['title']
        if request.form['artist']:
            item.artist = request.form['artist']
        if request.form['date']:
            item.date = request.form['date']
        if request.form['dimensions']:
            item.dimensions = request.form['dimensions']
        if request.form['medium']:
            item.medium = request.form['medium']
        if request.form['ondisplay']:
            item.ondisplay = request.form['ondisplay']
        if request.form['imgurl']:
            item.imgurl = request.form['imgurl']
        session.add(item)
        session.commit()
        flash('Item edited')
        return redirect(url_for('galleryInventory', gallery_id=gallery_id))
    else:
        return render_template('edititem.html', gallery_id=gallery_id, item=item)


@app.route('/gallery/<int:gallery_id>/inventory/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteInventoryItem(gallery_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    gallery = session.query(Galleries).filter_by(id=gallery_id).one()
    if gallery.user_id != login_session['user_id']:
        response = make_response(json.dumps(
            "You don't have permission to delete items for this gallery"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    item = session.query(Inventory).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item deleted')
        return redirect(url_for('galleryInventory', gallery_id=gallery_id))
    else:
        return render_template('deleteitem.html', item=item, gallery_id=gallery_id)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # upgrade the authorisation code into a credential object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the auth code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    
    # if there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json_dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    
    # verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's"), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),200)
        response.headers['Content-Type'] = 'application/json'
        return response
        
    # store the access token in the session for later use
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    
    # get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['picture'] = data['picture']
    login_session['provider'] = 'google'
    
    # check if user exists in the db
    user_id = getUserId(data['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    
    output = ''
    output += '<h1> welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash('you are logged in as %s' % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # only disconnect a connected user
    credentials = login_session.get('credentials')
    print 'credentials:', credentials
    
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # execute HTTP GET request to revoke current token
    access_token = credentials.access_token
    print 'access_token:', access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    
    if result['status'] != '200':
        # if for whatever reason the token was invalid
        response = make_response(json.dumps('Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
        

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    
    # Exchange client token for long-lived server side token with GET /oauth/
    # acces_token?grant_type=fb_exchange_token&client_id={app-id}
    # &client_secret={app-secret}&fb_exchange_token={short-lived-token}
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    
    # Use token to get user info from API
    userinfo_url = 'https://graph.facebook.com/v2.3/me'
    # strip expire tag from access token
    token = result.split('&')[0]
    
    url = 'https://graph.facebook.com/v2.3/me?%s' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    
    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token
    
    # check if user exists in the db
    user_id = getUserId(data['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    
    output = ''
    output += '<h1> welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash('you are logged in as %s' % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'you have been logged out.'


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        del login_session['provider']
        flash('You have successfully been logged out.')
        return redirect(url_for('galleryList'))
    else:
        flash('You were not logged in.')
        return redirect(url_for('galleryList'))
        

# API endpoint


@app.route('/galleries/JSON')
def galleryListJSON():
    galleries = session.query(Galleries)
    return jsonify(Galleries=[i.serialize for i in galleries])


@app.route('/gallery/<int:gallery_id>/inventory/JSON')
def inventoryJSON(gallery_id):
    gallery = session.query(Galleries).filter_by(id=gallery_id).one()
    items = session.query(Inventory).filter_by(gallery_id=gallery.id)
    return jsonify(Inventory=[i.serialize for i in items])


@app.route('/gallery/<int:gallery_id>/inventory/<int:artwork_id>/JSON')
def itemJSON(gallery_id, artwork_id):
    item = session.query(Inventory).filter_by(id=artwork_id).one()
    return jsonify(Inventory=item.serialize)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    