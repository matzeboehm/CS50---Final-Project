# MY PERSONAL COOKBOOK
#### Video Demo:  https://youtu.be/wnntE2DlMTI
#### Description:

##### Introduction
My Personal Cookbook is a collection of my personal favorite recipes. It gives the user the possibility to collaborate in the cookbook.
Since I personally struggle at cooking good food, it has been an idea of myself for a while to archive the recipes I like and summarize them in one collection,
compared to an oldschool cookbook.
This web application handles an overview of recipes. You can also add recipes, including a picture of your food, a list of ingredients, instructions on how to
make it, and how long it will take you. From the recipes implemented, you can also choose to derive a shopping list based on the recipes you want to make.
This shopping list will give you an overview of everything needed to make the perfect dish.

##### First Design Choices
Let's start with the first design choices. I chose to code a webapp over an iOS app for the simple reason that my girlfriend does not have an iPhone. This means
she would not be able to access it.

I also made a mobile friendly version of the application, since I usually take my recipes from my phone when cooking. Also, when I go grocery shopping, I always
have a grocery shopping list on my phone for convenience.

The last major design choice was using the CS50 IDE over Visual Studio Code. I started off with VSCode and had a first running prototype of the application before
I migrated my code to the CS50 IDE. I chose to do so for the simple reason that I can host this application live on the internet for free for my girlfriend to
test it (she currently lives abroad). I will continue working on the code to try to improve it. When finding more time, I will host it on a private server for
personal use.

##### Code
The web application is running on flask using sessions. Therefore, the structure of application.py, static and template folder are kept. For saving data,
a SQL database is added. Additional data is saved in .txt files, pictures are saved as .jpg.

###### application.py
application.py is the controller and backbone of this web application. Here all functions and the database are handeled. There are several routes for the sake of
handling user input and data manipulation. Logging into the user interface is required to access those functions.

- @app.route("/"):
This is the home screen of the application. Here, the user gets greeted and a random recipe of the day is suggested.

- @app.route("/receipt"):
This is a standard recipe template. Depending on which recipe the user clicked on, the required information to build the html will be collected. For this,
the information about the ingredients, the instructions, the cooking time and the picture will be loaded.

- @app.route("/receiptOverview"):
Here you can see a overview of all recipes currently implemented in the cookbook. The corresponding html page is generated based on the data saved in teh SQL database.

- @app.route("/generateReceipt"):
This route is used to generate a recipe based on user input. Therefore, there is the need to switch between GET and POST. On GET, only the input html will  be shown.
On POST, the user input is processed and saved to the required location for later reuse. The picture is saved as a .jpg, while the instructions and ingredients
are saved as a .txt file. The name and cooking duration are saved in the SQL database.

- @app.route("/shoopingcart"):
This route also has a GET and a POST way. The GET way loads the user interface, the post way lets you choose which recipts you would like to add to the shopping cart.
Based on the user's choices, the ingredients of the chosen dishes will be summarized and passed to the right html to show the grocery list.

- @app.route("/login"), @app.route("/logout"), @app.route("/register"):
These three methods are used to log the user in and out of the system and also to register him. Those functions work in cooperation with the users database, where
the hashed password and corresponding user name is stored.

###### recipes.db
This is a SQL database of all recipes implemented in the system. A second table caputres the users and their hashed passwords.

###### static
The static folder contains all data which is not changed dynamically. Here, the user input, which is not stored in the database, is saved. There are folders for
the ingredients and instructions specifications. Also the pictures of the dishes are saved here. The CSS stylesheet for the application is also stored here.

###### templates
This folder contains all html sites.
- layout.html
This html site contains the template for all other html sites used in this application. The following html files extend layout.html to generate a uniform look.
Also, a navigation bar is implemented here, so the user is able to skip between sites from every page.

- login.html
The login.html site handles the login process of the user and the corresponding user input. When submitted, it sends the user input to the route of the same
name. This site and mechanics has been mostly copied by problem set 9 of CS50.

- register.html
The register.html site handles the registration of new users and adds them to the database of users. When submitted, it sends the user input to the route of the
same name. This site and mechanics has been mostly copied by problem set 9 of CS50.

- index.html
The index.html site is the main page of the web application. Here, the user gets greeted and a suggestion of what to cook today.

- receiptOverview.html
The receiptOverview.html site summarizes all recipes that are currently implemented in the database. This site is created based on the controller.

- receipt.html
The receipt.html site is a template for all recipes. Based on what the user clicked on the receiptOverview.html site, the receipt.html site is generated. It
shows a picture of the dish, plus a list of ingredients and instructions on how to make the dish.

- generateReceipt.html
This html site is used to capture user input when creating a new recipe and adding it to the library of existing ones. There are several user input options.
The user is required to input a name, then he can caputre a picture of the dish. Later, he can add a list of ingredients, instructions and a guess on how long
cooking this dish will take. After submitting, the data is sent to the controller for processing and saving.

- shoppingcart.html
The shoppincart.html site shows the user a summary of all dishes available in the cookbook. The user can tick the boxes of the recipes he feels like cooking.
Further inspecting of the recipes is also possibly by clicking on their name. After submitting the checkbox form, the data is processed in the controller.

- shoppinglist.html
The shoppinglist.html site is directly generated from the controller data, after submitting the shoppingcart.html form. Here, a summary of the ingredients across
the ticked recipes is shown. This site can be used as a grocery shopping list for the next grocery store visit.

###### requirements.txt
Summary of libraries used in the application.