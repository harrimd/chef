# chef
Infocentric Design of Systems Project

Computer Helping Eat Food

## Application Setup

# Environment

This README assumes that your machine is appropriately setup 
to run Python scripts via the `python3` CLI, and that you have
the Python package manager installed.

### Install dependencies
* `pip install tkinter`
* `pip install dotenv`
* `pip install neo4j`

## Neo4J

There are two options when setting up the Neo4J database. You can either use a free AuraDB instance, which is cloud-based, but has limited plugin support (found [here](https://neo4j.com/cloud/platform/aura-graph-database/)). Simply create an account and follow the instructions listed on the website, then move on to "Setting Environment Variables")

Or, you can install and initialize a local instance on your machine, which has far more robust plugin support, but is not cloud-located. Simply navigate to [this link](https://neo4j.com/docs/operations-manual/current/installation/) and follow the instructions for your environment.

## Setting Environment Variables

In order for CHEF to query the database properly, you must set up a `.env` file with the correct variables. Create a file named `.env` with the variables as specified below:

```
DB_URI=<localhost:port> (if you are running a local instance), or <provided AuraDB endpoint> (if you are running there)
DB_USER=neo4j (by default)
DB_PASS=<as specified by your instance>
```

When your environment variables are set, run `python3 DAO.py` to populate the DB with the starting data.

# GUI Info
Once the database is setup and the dependencies are installed, running the GUI is very simple. All you need to do is run the `chef_gui.py` file using `python3 chef_gui.py`. If you want to init the database when running chef, ensure the `DAO_OBJ.init_db()` call at the top of the file is not commented out.

The GUI is split into rendering different pages, each rendered page can be found by looking for the methods that are of the form `create_<some page>()`. All drawn elements are added to a list at the bottom of the functions, and removed in the `reset_screen()` method. For the most part, related methods will be grouped together.

For actually using the GUI, it is quite simple. The sub-parts that exist are the shopping list, recipe list, week meal plan, and inventory. Inside these, there are other pages like a singular recipe, ingredient, or week day page.

The shopping list is just a list of ingredients that can be added to the database. You can enter items by typing them into the entry box on the shopping list page, or by clicking the "Shop Missing Ingredients" button on a recipe page. The "Buy/Inventory All Items" button on the shopping list page will clear the shopping list and take all the items and add them to the inventory.

The recipe list page will list all the recipes that a user has, and report the likability score based on the user preferences. Clicking on any of the recipes will link you to that recipes page, which lists all the information about them. More recipes can be added into the database, which will allow you to scroll from page to page between the recipes. You can click the "Filter Preparable" button at the top right to only show the recipes that are preparable, i.e. you have the ingredients in your inventory. In the individual recipe page, you can click the "Complete Recipe" button at the botom right to indiciate that you made the recipe and CHEF should remove the ingredients from your inventory.

The week meal plan page will list 7 boxes, each corresponding to a day of the week. Currently, whenever CHEF is run, it will create a new week meal plan upon first visiting the page. It will persist until CHEF is closed and opened again. The week meal plan will take all recipes for a user that does not have a likability score of 0 (meaning allergy or strong dislike), and create a 7 day plan of meals. It will go through all possible recipes before repeating to reduce the chance of making the same meal. You can click on the day of the week, which will link you to the recipe page, and also a button to complete the meal. This button will add a visual indicator showing that the recipe was completed in the week meal plan page and also remove the ingredients from your inventory.

The food inventory page is very similar to the recipe page. However, here it only lists all the ingredients you have added to your inventory. Again you can go from page to page to see all your ingredients and also the likability score is listed for each ingredient. You can change the likability scores of these ingredients directly through the "User Preferences" button on the main page (explained next). Upon visiting this page after changing the preference, the score will be changed. Again you can click on a row to bring up a food page which lists all the information about the ingredient and any substitutions that are possible for it.

The final option on main menu is the "User Preferences" button. This will allow you to change your preferences for individual ingredients. You can do this by entering the name of the ingredient in the text box at the top left, then choosing a number 0-10 in the dropdown. 0 means allergic or never want to eat, and 10 means you very much like the ingredient. Once the two forms are filled, you can click the button on the right to add the preference, updating the database. The text box showing the user preferences currently is reset every time upon visiting the page, but the preferences are still there in the database.
