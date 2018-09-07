# Instruments-Catalog

# Musical Instruments and Accesories Catalog Website

This project focuses in CRUD capabilities. Create, Read, Update and Delete information from a database. The core functionality of the website relies on these four capabilities to create and maintain a catalog for music instruments.
This catalog is developed using as guide the examples exposed in Udacity in the BackEnd section.


## Getting Started

Clone or download this project (folder: catalog) in your local machine to be able to run the website.

### Need to have/install a command line application to run a virtual environment where the website will be run.

GitBash recommended:

Follow [this](https://git-scm.com/downloads) link and download it according to your system.

### Need to have/install a Virtual Box to run the Virtual Machine:

If you do not have one you can download it [here](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)

### Need to have/install software to configure the virtual machine and share files between host computer and VM's filesystem:

Vagrant is recommended. If you do not have it you can download it [here](https://www.vagrantup.com/downloads.html)


###  Authentication key

In this project, Google Authentication is used to provide third-party authorization for CRUD functionality in the catalog.
Please get your key in [Google developers website](https://developers.google.com/) - You need a google email account. 
IMPORTANT: Please place your own client-secrets.JSON file in the catalog folder (you can get it from your application page in Google developers website), and update the 'data-clientid' field in the login.html template.

## Running the Music Instruments Website

1. Open the command line application (e.g. Git Bash)
2. Go to the directory where the music catalog folder was downloaded/cloned
3. Start Vagrant. (e.g. vagrant up and then vagrant ssh)
4. Once in the catalog directory within the virtual machine confirm that the following folders/files are in it:

- templates: Folder with all the html templates utilized in this project. The template names are self explanatory. Templates with 'public' at the beginning
			 indicate that they do not allow CRUD functionality. After a correct login, the user will be re-directed to their CRUD equivalents.
- static: Folder with styles.css file and an image subfolder
- cat_setup.py: Python file that configures the database utilized in the catalog. There are three main elements in it: 1. User, 2. Instrument (Instrument Category) and 3. CatalogItem (The specific instrument or accessory within a category).
- someinstruments.py: Python file that defines two instrument categories, each with two items for a defined user (Me)
- application.py: This is the main Python file that performs all the CRUD operations for the website and calls the different html templates accordingly. The file is built following CRUD recommendations given in class for third-party authentication and CRUD functionality. It also defines port 8000 for local website hosting.

5. How to run?
In the music catalog folder in Vagrant run the following files in order:

-Setup the Database
```
python cat_setup.py 
```

-Initialize the Database
```
python someinstruments.py 
```

-Start the catalog application
```
python application.py 
```

- Go to your preferred web browser and load http://localhost:8000/instruments : This should get your website loaded an running.


Just give it a try!

## Test the website

### Catalog Visualization
It is recommended to first navigate through the catalog without logging in with the provided authentication method (Google).
You should be able to see the current two instruments categories defined in the initialization file (someinstruments.py). You can open each of the categories to visualize their two defined catalog items.
It is important to highlight that you WON'T be able to make any change to catalog in general. You're not logged in!

### Catalog CRUD functionality
Log in! (Remember, you need a google account). If you're in the front page (http://localhost:8000/instruments) you will see an additional button to create a new instrument category. Create one that you like. A new object will show up in the front page containing your new category.
If you enter it, you will be re-directed to the catalog item page. It's empty, right? But now you have the rights to edit/delete that category you just created and also to create a new catalog item.

If you create a new catalog item you'll need the following information:
1. Name of item
2. Short description
3. Price in dollars
4. Warranty (has warranty, for how long? eg. 6 months, No)
5. Picture. I want to stress this item particularly. I implemented image visualization in the catalog through links of images' locations. You will need to input the link of the picture location based on the port in which the catalog runs.
All the current pictures in the website are located in /catalog/static/images. They are called in the application by using the port http address (http://localhost:8000/static/images/picture.jpg). You can include your own pictures in the 'images' folder and call them using the aforementioned link.
A size of (640 X 436 pxls) is utilized for the samples provided, however, the website counts on image scaling from bootstrap should you use a different size. I included some extra pictures in the folder that you can use to test your new catalog item. (Note: All catalog  pictures were taken from Pexel.com and front page pic from https://covers.alphacoders.com/by_category/22/3/linkedin-background)
 
Editing an instrument category or catalog item follows similar steps as creating.

To delete an instrument category or catalog item, hit 'delete' to be redirected to a deletion confirmation page.

You can always cancel any edit/deletion if you decide not to proceed by hitting CANCEL.

### JSON Points

The following addresses will provide the JSON API points depending on the information requested:

1. (http://localhost:8000/instruments/JSON) : List of instrument categories in the Database.
2. (http://localhost:8000//instruments/<int:instrument_id>/catalog/JSON) : List of items within instrument category identified with 'instrument_id'.
3. (http://localhost:8000//instruments/<int:instrument_id>/catalog/<int:item_id>/JSON) : Items (item_id) within instrument category identified with 'instrument_id'.

### Potential Improvements

## Image handling
Automatic searching (opening a browsing window that locates the picture) to save images directly in the images folder.

## Catalog Front-End
I used many of the design patterns that were presented in Udacity's catalog restaurant (styles, bootstrap) with some customizations to improve visualization.
However, a more friendly interface can be developed.
I would also like to add the 'buy' and 'contact' capabilities to the catalog in order to have shopping cart.

NOTE: Please feel free to suggest modifications/improvements or to make a pull request to contribute.

## Authors

* **Jhon Diaz** - [jfbeyond](https://github.com/jfbeyond)

## Acknowledgments

* Udacity (Restaurant catalog)
* Bootstrap, Google devtools, Pexel
* Inspiration
