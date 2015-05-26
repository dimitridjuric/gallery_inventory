# Gallery Inventory


This application is a database of artworks, allowing users to search by both artist name and title. The artworks are part of collections (inventory) of art galleries, and the idea behind
this application is to allow users to find whether an artwork is on display and if so in which gallery.
Unlogged users can view a list of galleries, the inventory of each gallery, a list of artists and a list of works of for each artist. There is a search box in which users can enter either
artist names or artwork titles. The search works even if the name or title is incomplete. Logged users can add new galleries, in doing so they become the galleries administrator.
Administrators can edit gallery details, add, edit and delete artworks to/from the inventory. They are not allowed to add, edit or delete artworks from galleries they don't administer.


### Setup

If you vagrant up this project it will create a postgres database called gallerydbwithusers.
Then it's going to run gallerydatabase_setup.py to create the tables.
Finally it's going to import a small example database. (This database was exported from my testing using pg_dump)

Before running the app you need to add the client secrets, and app id to these files:
client_secrets.json
fb_client_secrets.json

Once this is done you can run the app with
python final_project.py

Now the app is serving on http://localhost:8850/


### Using the app

The main page displays a list of a few galleries. Each gallery has links showing a list of artists and a list of artworks.
Once logged in, a user can add a new gallery to administer, and artworks for this gallery. The user can also edit and delete artworks.
In the `/galleries` page, only galleries for which the user is an administrator have links to edit or delete.


### Search functionality

A search for 'gainsborough' or even 'gains' will return artworks from both Tate Britain and
The National Gallery. 


### API 

The data can be accessed via the app's API.
`/galleries/JSON` returns a json file of the galleries table
`/gallery/xx/inventory/JSON` returns the inventory of gallery xx
`/gallery/xx/inventory/yy/JSON` returns the data on artwork yy of gallery xx


