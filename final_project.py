from helpers import search_db, get_galleries, get_artists, get_artworks, get_artwork
from helpers import create_gallery, edit_gallery, delete_gallery, new_artwork
from helpers import edit_artwork, delete_artwork, create_user, get_user_info, get_user_id
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps
from flask.ext.seasurf import SeaSurf
from gallerydatabase_setup import Galleries, Inventory

app = Flask(__name__)
# Cross site forgery request protection
csrf = SeaSurf(app)
# client secret for google authentication
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


# public access urls routes


@app.route('/', methods=['GET', 'POST'])
@app.route('/galleries/', methods=['GET', 'POST'])
def galleryList():
    "Main page. Shows a list of the galleries in the database with details."
    # The only POST request is the search box
    if request.method == 'POST':
        search = request.form['search']
        if search:
            results = search_db(search)
            return render_template('search.html', results=results)
    else:
        # the GET request renders the page
        galleries = get_galleries()
        # check if user is logged in
        if 'user_id' in login_session:
            user_id = login_session['user_id']
        else:
            user_id = None
        return render_template('galleries2.html', galleries=galleries,
                               user_id=user_id)


@app.route('/artists/', methods=['GET', 'POST'])
def artistList():
    "Artists page. Lists all the artists in the db."
    # The only POST request is the search box
    if request.method == 'POST':
        search = request.form['search']
        if search:
            results = search_db(search)
            return render_template('search.html', results=results)
    # the GET request renders the page
    else:
        # query to get the artists in the gallery inventory
        artists = get_artists()
    return render_template('all_artists.html', artists=artists)


@app.route('/artist_works/<artist_name>', methods=['GET', 'POST'])
def artistWorks(artist_name):
    "List of all the works in the db for a specific artist."
    # The only POST request is the search box
    if request.method == 'POST':
        search = request.form['search']
        if search:
            results = search_db(search)
            return render_template('search.html', results=results)
    else:
        # query to get the artworks of the specific artist
        artworks = get_artworks(artist_name)
    return render_template('artist_works.html', artist=artist_name,
                           artworks=artworks)


@app.route('/gallery/<int:gallery_id>/')
@app.route('/gallery/<int:gallery_id>/inventory/', methods=['GET', 'POST'])
def galleryInventory(gallery_id):
    '''Inventory of works for a specific gallery. Artworks are only editable if
    user is the gallery administrator'''
    gallery = get_galleries(gallery_id)
    items = get_artworks(gallery_id=gallery_id)
    if 'username' not in login_session or gallery.user_id != login_session[
            'user_id']:
        return render_template('public_inventory.html', gallery=gallery,
                               items=items)
    else:
        return render_template('inventory.html', gallery=gallery, items=items)


@app.route('/gallery/<int:gallery_id>/artists/')
def galleryArtists(gallery_id):
    '''Lists all the artists of a specific gallery'''
    gallery = get_galleries(gallery_id)
    artists = get_artists(gallery_id)
    return render_template('artists.html', gallery=gallery, artists=artists)


@app.route('/gallery/<int:gallery_id>/artists/<artist_name>')
def artistInventory(gallery_id, artist_name):
    '''Lists all the works of a specific artist in a specific gallery.
    Artworks are only editable if user is the gallery administrator'''
    gallery = get_galleries(gallery_id)
    items = get_artworks(artist_name, gallery_id)
    if 'username' not in login_session or gallery.user_id != login_session[
            'user_id']:
        return render_template('public_artistinventory.html', items=items,
                               artist=artist_name, gallery=gallery)
    else:
        return render_template('artistinventory.html', items=items,
                               artist=artist_name, gallery=gallery)


# For the following urls the user need to be logged in.


def login_required(f):
    '''Login required decorator. use this to decorate all the routes where the
    user has to be logged in. If the user isn't logged in, it redirects to the
    login page'''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin', next_url=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/gallery/new/', methods=['GET', 'POST'])
@login_required
def newGallery():
    '''Create a new gallery'''
    # POST request is the form with the details of the new gallery
    if request.method == 'POST':
        create_gallery(request.form, login_session['user_id'])
        # flash message confirmation
        flash('New gallery created')
        return redirect(url_for('galleryList'))
    # GET request renders the page
    else:
        return render_template('newgallery.html')


@app.route('/gallery/<int:gallery_id>/edit/', methods=['GET', 'POST'])
@login_required
def editGallery(gallery_id):
    '''Edit the details of an existing gallery. For this the user has to
    be the administrator of the gallery.'''
    # gallery = session.query(Galleries).filter_by(id=gallery_id).one()
    gallery = get_galleries(gallery_id)
    # check if user is authorised
    if gallery.user_id != login_session['user_id']:
        response = make_response(json.dumps(
            "You don't have permission to edit this gallery"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # POST request is the form to edit the details
    if request.method == 'POST':
        edit_gallery(request.form, gallery)
        flash('Gallery edited')
        return redirect(url_for('galleryList'))
    # GET request renders the page
    else:
        return render_template('editgallery.html', gallery=gallery)


@app.route('/gallery/<int:gallery_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteGallery(gallery_id):
    '''Delete an existing gallery. For this the user has to be the administrator
    of the gallery.'''
    # get the objects from the DB
    gallery = get_galleries(gallery_id)
    items = get_artworks(gallery_id=gallery_id)
    # check if the user is authorised to delete the gallery
    if gallery.user_id != login_session['user_id']:
        response = make_response(json.dumps(
            "You don't have permission to delete this gallery"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    if request.method == 'POST':
        # delete the items in the gallery inventory, then the gallery from
        # the db
        delete_gallery(gallery, items)
        flash('Gallery deleted')
        return redirect(url_for('galleryList'))
    else:
        return render_template('deletegallery.html', gallery=gallery)


@app.route('/gallery/<int:gallery_id>/inventory/new/', methods=['GET', 'POST'])
@login_required
def newInventoryItem(gallery_id):
    '''Add an artwork to the inventory of a gallery, user has to be the
    administrator of the gallery'''
    gallery = get_galleries(gallery_id)
    # check if user is authorised
    if gallery.user_id != login_session['user_id']:
        response = make_response(json.dumps(
            "You don't have permission to add an item to this gallery"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # POST request is the form for the new artwork
    if request.method == 'POST':
        new_artwork(request.form, gallery_id)
        flash('New artwork added')
        return redirect(url_for('galleryInventory', gallery_id=gallery_id))
    # GET request renders the page
    else:
        return render_template('newitem.html', gallery=gallery)


@app.route('/gallery/<int:gallery_id>/inventory/<int:item_id>/edit/',
           methods=['GET', 'POST'])
@login_required
def editInventoryItem(gallery_id, item_id):
    '''Edit an artwork to the inventory of a gallery, user has to be the
    administrator of the gallery'''
    gallery = get_galleries(gallery_id)
    # check if user is authorised
    if gallery.user_id != login_session['user_id']:
        response = make_response(json.dumps(
            "You don't have permission to edit items for this gallery"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    item = get_artwork(item_id)
    # POST request is the form to edit artwork
    if request.method == 'POST':
        edit_artwork(request.form, item)
        flash('Item edited')
        return redirect(url_for('galleryInventory', gallery_id=gallery_id))
    # GET request renders the page
    else:
        return render_template('edititem.html', gallery_id=gallery_id,
                               item=item)


@app.route('/gallery/<int:gallery_id>/inventory/<int:item_id>/delete/',
           methods=['GET', 'POST'])
@login_required
def deleteInventoryItem(gallery_id, item_id):
    '''Edit an artwork of a gallery, user has to be the administrator of the
    gallery'''
    gallery = get_galleries(gallery_id)
    # check if user is authorised
    if gallery.user_id != login_session['user_id']:
        response = make_response(json.dumps(
            "You don't have permission to delete items for this gallery"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    item = get_artwork(item_id)
    if request.method == 'POST':
        delete_artwork(item)
        flash('Item deleted')
        return redirect(url_for('galleryInventory', gallery_id=gallery_id))
    else:
        return render_template('deleteitem.html', item=item,
                               gallery_id=gallery_id)


@app.route('/login')
def showLogin():
    '''Login page'''
    state = ''.join(random.choice(string.ascii_uppercase + string.
                                  digits) for x in xrange(32))
    login_session['state'] = state
    next_url = request.args.get('next_url') or '/galleries'
    print 'in showLogin, next_url: ', next_url
    return render_template('login.html', STATE=state, next_url=next_url)


@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''Oauth with Google account'''
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
        response = make_response(json.dumps('Failed to upgrade the auth code.'),
                                 401)
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
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
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
    user_id = get_user_id(data['email'])
    if user_id is None:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id
    
    output = 'Welcome ' + login_session['username']
    flash('you are logged in as %s' % login_session['username'])
    return output
    

@app.route('/gdisconnect')
def gdisconnect():
    '''Oauth disconnect of user connected with Google'''
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
        response = make_response(json.dumps(
            'Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
        

@csrf.exempt
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    '''Oauth with Facebook account'''
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    
    # Exchange client token for long-lived server side token with GET /oauth/
    # acces_token?grant_type=fb_exchange_token&client_id={app-id}
    # &client_secret={app-secret}&fb_exchange_token={short-lived-token}
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web'][
        'app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web'][
        'app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
            app_id, app_secret, access_token)
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
    
    # The token must be stored in the login_session in order to properly logout,
    # let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token
    
    # check if user exists in the db
    user_id = get_user_id(data['email'])
    if user_id is None:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id
    
    output = 'welcome ' + login_session['username']
    flash('you are logged in as %s' % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    '''Oauth disconnect for users of Facebook'''
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'you have been logged out.'


@app.route('/disconnect')
def disconnect():
    '''General disconnect, Will call the method specific to the oauth
    provider'''
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
        

# API endpoints


@app.route('/galleries/JSON')
def galleryListJSON():
    galleries = get_galleries()
    return jsonify(Galleries=[i.serialize for i in galleries])


@app.route('/gallery/<int:gallery_id>/inventory/JSON')
def inventoryJSON(gallery_id):
    gallery = get_galleries(gallery_id)
    items = get_artworks(gallery_id=gallery_id)
    return jsonify(Inventory=[i.serialize for i in items])


@app.route('/gallery/<int:gallery_id>/inventory/<int:artwork_id>/JSON')
def itemJSON(gallery_id, artwork_id):
    item = get_artwork(artwork_id)
    return jsonify(Inventory=item.serialize)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8050)
    