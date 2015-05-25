
apt-get -qqy update
apt-get -qqy install postgresql python-psycopg2
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip
sudo pip install werkzeug==0.8.3
sudo pip install flask==0.9
sudo pip install Flask-Login==0.1.3
pip install requests
pip install bleach
pip install oauth2client
pip install flask-seasurf
su postgres -c 'createuser -dRS vagrant'
su vagrant -c 'createdb'
su vagrant -c 'createdb gallerydbwithusers'
su vagrant -c 'python /vagrant/gallerydatabase_setup.py'
su vagrant -c 'psql -d gallerydbwithusers -f /vagrant/gallerydb.sql'



