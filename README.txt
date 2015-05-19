Gallery Inventory

This application is a database of artworks, allowing users to search by both artist name and title. The artworks are part of collections (inventory) of art galleries, and the idea behind this application is to allow users to find whether an artwork is on display and if so in which gallery.
Unlogged users can view a list of galleries, the inventory of each gallery, a list of artists and a list of works of for each artist. There is a search box in which users can enter either artist names or artwork titles. The search works even if the name or title is incomplete. 
Logged users can add new galleries, in doing so they become the galleries administrator. Administrators can edit gallery details, add, edit and delete artworks to/from the inventory. They are not allowed to add, edit or delete artworks from galleries they don't administer.

Setup

1- In Postgres create a database called gallerydbwithusers:
	CREATE DATABASE gallerydbwithusers;

2- In the console, run gallerydatabase_setup.py:
	python gallerydatabase_setup.py

3- Still in the console, import the example database gallerydb.sql 
	psql -d gallerydbwithusers -f gallerydb.sql
the file gallerydb.sql was generated with pg_dump 


4- run final_project.py

	python final_project.py

Now the app is serving on http://localhost:5000/
The main page displays a list of a few galleries.
A search for 'gainsborough' or even 'gains' will return artworks from both Tate Britain and The National Gallery. 

Once logged in, a user can add a new gallery to administer, and artworks for this gallery.

In the /galleries page, only galleries for the user logged in have links to edit or delete.


API 

The data can be accessed via the app's API.
/galleries/JSON returns a json file of the galleries table
/gallery/xx/inventory/JSON returns the inventory of gallery xx
/gallery/xx/inventory/yy/JSON returns the data on artwork yy of gallery xx


