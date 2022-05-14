import tkinter as tk
from tkinter import *
from tkinter import ttk
import random
from datetime import date, timedelta

# Keep track of which page we are on for going backwards
# main, recipe, recipe_list, shopping_list
BACK_STATE = []

# Default colors for some things
PURPLE_BUTTON_COLOR = '#9C8DFF'
DARK_BLUE_FRAME_BG = "#174169"
BACKGROUND_COLOR = '#2D9CB5'
GREY_BG_COLOR = "#9A9999"

FILTER_RECIPE_BY_PREPARABLE = False

# Keep track of which things on the shopping list are crossed off
CROSSED_SHOP_ITEMS = []

# Keep track of the weekly meal plan
WEEK_MEAL_PLAN = []

# Initializing the DAO
import DAO
from settings import DB_URI, DB_USER, DB_PASS
DAO_OBJ = DAO.DAO(DB_URI, DB_USER, DB_PASS)
USER = "Alan"
# DAO_OBJ.init_db()

def go_back():
    if len(BACK_STATE):
        BACK_STATE.pop()
        if len(BACK_STATE):
            # Figure out which was the previous state
            if BACK_STATE[-1] == "main":
                create_main_screen()
            elif BACK_STATE[-1] == "recipe":
                create_recipe_page(None, going_back=True)
            elif BACK_STATE[-1] == "recipe_list":
                create_recipe_list(going_back=True)
            elif BACK_STATE[-1] == "shopping_list":
                create_shopping_list(going_back=True)
            elif BACK_STATE[-1] == "food_inventory":
                create_food_inventory(going_back=True)
            elif BACK_STATE[-1] == "week_plan":
                create_weekplan_page(going_back=True)
            elif BACK_STATE[-1].startswith("day_plan_"):
                create_dayplan_page(BACK_STATE[-1].replace("day_plan_", ""), going_back=True)
            return
    create_main_screen()


def create_inner_box():
    border_size = 8
    # Outside frame to make a border
    border_frame = Frame(bg="black")
    # Inner frame for listing recipes
    inner_frame = Frame(border_frame, bg=GREY_BG_COLOR)
    inner_frame.pack(expand=True, fill='both', padx=border_size, pady=border_size)
    border_frame.place(relx=.5, rely= .25, relheight=.7, relwidth=.8, anchor="n")
    
    return border_frame, inner_frame


def bind_frame_and_children(frame, function):
    frame.bind('<Button-1>', function)
    # Bind all the children too
    for wid in frame.winfo_children():
        wid.bind("<Button-1>", function)

def create_left_right_arrows():
    left_list_btn = Button(text="\u2190", font=("gabriola", 50), bg=DARK_BLUE_FRAME_BG, bd=2, fg="white", activebackground='#CED500')
    left_list_btn.place(relx=0.01, rely=0.6, relheight=.18, anchor="w")

    right_list_btn = Button(text="\u2192", font=("gabriola", 50), bg=DARK_BLUE_FRAME_BG, bd=2, fg="white", activebackground='#CED500')
    right_list_btn.place(relx=0.99, rely=0.6, relheight=.18, anchor="e")

    nodes.append(left_list_btn)
    nodes.append(right_list_btn)

    return left_list_btn, right_list_btn


def changeTitle(test):
    title_lbl.config(text = test)
    for element in nodes:
        element.place_forget()


def reset_screen():
    global nodes
    for node in nodes:
        node.destroy()
    
    nodes = []
        

def shopping_list_item_click(event):
    global CROSSED_SHOP_ITEMS
    # get the index of the mouse click
    index = event.widget.index("@%s,%s" % (event.x, event.y))

    # get the indices of all "adj" tags
    tag_indices = list(event.widget.tag_ranges('tag')) + list(event.widget.tag_ranges('tag-crossed'))

    # iterate them pairwise (start and end index)
    for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
        # check if the tag matches the mouse click index
        if event.widget.compare(start, '<=', index) and event.widget.compare(index, '<', end):
            # Switch between crossed out or not
            print("CHANGING")
            if event.widget.get(start) != u'\u0336':
                new_line = ''.join([u'\u0336{}'.format(c) for c in event.widget.get(start, end)]) + u'\u0336'
                event.widget.replace(start, end, new_line, "tag-crossed")
                CROSSED_SHOP_ITEMS.append(new_line.replace(u'\u0336', ""))
            else:
                new_line = event.widget.get(start, end).replace(u'\u0336', "")
                event.widget.replace(start, end, new_line, "tag")
                CROSSED_SHOP_ITEMS.remove(new_line)
            print(new_line)
            
def add_item(event):
    global text_area
    try:
        new_item = event.widget.get()
        if new_item:
            # Add to the on-screen list
            text_area.insert("end", " \u2022 {}".format(new_item), "tag")
            text_area.insert("end", "\n")
            
            event.widget.delete(0, "end")
            # Update the backend list
            DAO_OBJ.add_shopping_item(USER, new_item)
    except Exception as e:
        print("error somehow adding item??")
        print(e)


def buy_shopping_list(text_area):
    print("Buy the list!")
    raw_text = text_area.get("1.0", "end-1c")
    # Need to remove the formatting we had
    for del_chars in [u'\u0336', " \u2022 "]:
        raw_text = raw_text.replace(del_chars, "")

    # Now go through the lines and remove them from the shopping list and add to inventory
    for line in raw_text.split("\n"):
        # Dont want to run on empty lines
        if line:
            print("deleting {}".format(line))
            # Delete from the shopping list
            DAO_OBJ.delete_shopping_item(USER, line)
            # Add to the inventory (make expiration just a random number for now)
            DAO_OBJ.add_inventory_item("Alan", {
                                       "name": line,
                                       "quantity":1, 
                                       "expiration": str(date.today() + timedelta(days=random.randint(10,25))), 
                                       "purchase": str(date.today())
                                        })
    # Now need to clear the text area
    text_area.delete(1.0, END)
    # Clear the list of crossed off things
    global CROSSED_SHOP_ITEMS
    CROSSED_SHOP_ITEMS = []

def create_shopping_list(going_back=False):
    global CROSSED_SHOP_ITEMS
    reset_screen()
    title_lbl.config(text = "Shopping List")
    if not going_back:
        BACK_STATE.append("shopping_list")
    
    shopping_list = DAO_OBJ.get_shopping_list(USER)
    global text_area
    global nodes
    
    border_color = Frame(background="black")
    text_area = tk.Text(border_color, border=0, bg="light grey", font=("Georgia", 20))
    text_area.bind("<B1-Motion>", lambda e: "break")
    text_area.bind("<Double-Button-1>", lambda e: "break")
    text_area.bind("<Key>", lambda e: "break")

    # Setting the clicking stuff
    text_area.tag_config("tag")
    text_area.tag_config("tag-crossed", foreground="red")
    text_area.tag_bind("tag", "<Button-1>", shopping_list_item_click)
    text_area.tag_bind("tag-crossed", "<Button-1>", shopping_list_item_click)
    
    # Insert each line separately for individual clicking
    print(CROSSED_SHOP_ITEMS)
    for item in shopping_list:
        item_tag = "tag"
        item_string = " \u2022 {}".format(item["name"])
        print(item)
        if item_string in CROSSED_SHOP_ITEMS:
            item_tag = "tag-crossed"
            item_string = ''.join([u'\u0336{}'.format(c) for c in item_string]) + u'\u0336'
        text_area.insert("end", item_string, item_tag)
        text_area.insert("end", "\n")
    
    # Creating the black border
    border_size = 5
    text_area.pack(expand=True, fill='both', padx=border_size, pady=border_size)
    border_color.place(relx=.5, rely=.3, anchor='n', relheight=.6, relwidth=.8)
    
    # Add a scroll bar
    scroll_bar = tk.Scrollbar(text_area, command=text_area.yview)
    scroll_bar.pack(side=tk.RIGHT, fill='y')
    text_area.config(yscrollcommand=scroll_bar.set)
    
    # Add the entry box for adding items
    entry = ttk.Entry(font=("Georgia", 15))
    entry.bind('<Return>', add_item)
    entry.place(relx=.5, rely=.3, relwidth=.8, relheight=.04, anchor="s")
    
    # Add the button to clear/inventory the shopping list
    buy_all_button=Button(text="Buy/Inventory All Items", fg='white', bg=DARK_BLUE_FRAME_BG, bd=7, font = ("Gariola", 18),
                            relief="solid", command=lambda ta=text_area: buy_shopping_list(ta), wraplength=300)
    buy_all_button.place(relx=0.99, rely=0.03, relheight=.14, anchor="ne")


    # Need to log the nodes for deletion later
    nodes.append(entry)
    nodes.append(buy_all_button)
    nodes.append(border_color)

    
def change_recipe_filtering(pass_through):
    global FILTER_RECIPE_BY_PREPARABLE
    FILTER_RECIPE_BY_PREPARABLE = not FILTER_RECIPE_BY_PREPARABLE
    create_recipe_list(going_back=True, pass_through=pass_through)


def check_recipe_prepable(recipe_name, prepable_recipes):
    for recipe in prepable_recipes:
        if recipe["name"] == recipe_name:
            return True
    return False


def create_recipe_list(page=0, going_back=False, pass_through=None):
    # First time into this page, so need to draw everything
    if not pass_through:
        reset_screen()
        border_frame, recipes_frame = create_inner_box()
    # Check lower bound on page
    if page < 0:
        page = 0
    if not going_back:
        BACK_STATE.append("recipe_list")
        
    global FILTER_RECIPE_BY_PREPARABLE
    
    # Get the full recipe list
    # Only need to query db if not passthrough, is slow
    if not pass_through:
        recipes = DAO_OBJ.get_scored_recipes(USER)
    else:
        recipes = pass_through["recipes"]

    # Get all completable recipes
    prepable_recipes = DAO_OBJ.find_ready_recipes_by_person(USER)

    if not pass_through:
        recipe_blocks = []
        for i in range(0, 5):
            # Keep references to all objects
            new_recipe_set = {}
            # Change the top label colors for visibility
            label_color = PURPLE_BUTTON_COLOR if i else "#B3388C"
            # Each "recipe" will be a box in a row, not scrollable, but able to go left to right
            entry_frame = Frame(recipes_frame, bg=DARK_BLUE_FRAME_BG)
            entry_frame.place(relx=.5, rely=.04 + .19 * i, relheight=.15, relwidth=.95, anchor="n")

            new_recipe_set["frame"] = entry_frame

            # Now need to add the internal blocks
            # Used for indexing for the name
            label_names = ["Name", "Type", "Time", "Likability"]
            # Adding the first three labels on the left side
            for j in range(0, 4):
                new_label = Label(entry_frame, text=label_names[j], fg='white', bg=label_color, borderwidth=3,
                              font=("Gariola", 12), wraplength=200)
                new_label.place(relx=.1 + .18 * j, rely=.1, relheight=.8, relwidth=.16, anchor='n')
                new_recipe_set[label_names[j].lower()] = new_label
            # Now add the preparable label on the right
            prepare_label = Label(entry_frame, text="Preparable", fg='white', bg=label_color, borderwidth=3,
                              font=("Gariola", 12), wraplength=200)
            prepare_label.place(relx=.9, rely=.1, relheight=.8, relwidth=.16, anchor='n')
            # Check mark = u"\u2713"
            new_recipe_set["preparable"] = prepare_label

            recipe_blocks.append(new_recipe_set)

    # Was pass through so just get the elements out
    else:
        recipe_blocks = pass_through["recipe_blocks"]
    
    # Now setting the different entries
    recipes_index = 0
    blank_rest = False
    # First need to raise the recipes_index for the current page
    if page != 0:
        for i in range(page):
            if recipes_index + 4 < len(recipes):
                recipes_index += 4
            else:
                page = i
                break
    # Set title after this so the page is consistent
    title_lbl.config(text = "Recipe List Page {}".format(page + 1))
    for i in range(4):
        if FILTER_RECIPE_BY_PREPARABLE:
            while recipes_index in range(len(recipes)):
                if not check_recipe_prepable(recipes[recipes_index]['name'], prepable_recipes):
                    recipes_index += 1
                else:
                    break
        if recipes_index not in range(len(recipes)):
            blank_rest = True
        recipe_blocks[i+1]['name'].config(text=recipes[recipes_index]['name'] if not blank_rest else "")
        recipe_blocks[i+1]['type'].config(text=recipes[recipes_index]['type'] if not blank_rest else "")
        recipe_blocks[i+1]['time'].config(text=str(recipes[recipes_index]['time']) + " hr(s)" if not blank_rest else "")
        recipe_blocks[i+1]['preparable'].config(text=(u"\u2713" if check_recipe_prepable(recipes[recipes_index]['name'], prepable_recipes) else "X") if not blank_rest else "")
        recipe_blocks[i+1]["likability"].config(text=recipes[recipes_index]["score"] if not blank_rest else "")
        if not blank_rest:
            # Set up the bind to click
            bind_frame_and_children(recipe_blocks[i+1]["frame"], lambda e, name=recipes[recipes_index]['name']: create_recipe_page(name))
        recipes_index += 1
    
    # Add the arrows
    l_arrow, r_arrow = create_left_right_arrows()
    l_arrow.config(command=lambda: create_recipe_list(page=page-1, going_back=True, pass_through=pass_through))
    r_arrow.config(command=lambda: create_recipe_list(page=page+1, going_back=True, pass_through=pass_through))

    if not pass_through:
        # Add a button to the top right for filtering by preparable
        shop_recipe_btn=Button(text="Filter Preparable [{}]".format(u"\u2713" if FILTER_RECIPE_BY_PREPARABLE else "X"), fg='white', bg=DARK_BLUE_FRAME_BG, bd=7, font = ("Gariola", 18),
                                relief="solid", command=lambda: change_recipe_filtering(pass_through), wraplength=300)
        shop_recipe_btn.place(relx=0.99, rely=0.03, relheight=.14, anchor="ne")
    
        nodes.append(shop_recipe_btn)
        
        # Log the border_frame for deletion later
        nodes.append(border_frame)

    # Pass through the UI elements so we dont need to redraw for no reason
    pass_through = {"recipe_blocks": recipe_blocks, "l_arrow": l_arrow, "r_arrow":r_arrow, "recipes": recipes}


def complete_recipe(recipe_name):
    for ingred in DAO_OBJ.find_ingredients_by_recipe(recipe_name):
        # First need to find the ingred purchase date to remove
        purch_date = None
        for owned_ingred in DAO_OBJ.get_inventory(USER):
            if owned_ingred["name"] == ingred:
                purch_date = owned_ingred["purchase"]
                break
        if purch_date:
            DAO_OBJ.delete_inventory_item(USER, {"name": ingred, "purchase": purch_date})
        else:
            print("Didn't use ingredient: {}!".format(ingred))


def create_recipe_page(recipe_name, going_back=False):
    reset_screen()
    title_lbl.config(text = "{} Page".format(recipe_name))
    if not going_back:
        BACK_STATE.append("recipe_page")
    
    recipe_info = DAO_OBJ.get_recipe(recipe_name)

    border_size = 8
    # Outside frame to make a border
    border_frame = Frame(bg="black")
    
    # Placing the labels for the recipe info
    grid_frame = Frame(border_frame, bg=DARK_BLUE_FRAME_BG, bd=5)
    grid_frame.pack(expand=True, fill='both', padx=border_size, pady=border_size)
    border_frame.place(relx=.5, rely= .21, relheight=.78, relwidth=.98, anchor="n")
    
    grid_frame.grid_rowconfigure(0, weight=2)
    grid_frame.grid_rowconfigure(1, weight=2)
    grid_frame.grid_rowconfigure(2, weight=50)
    grid_frame.grid_rowconfigure(3, weight=1)
    grid_frame.grid_columnconfigure(0, weight=1)
    grid_frame.grid_columnconfigure(1, weight=1)
    
#     recipe_label=Label(grid_frame, text="Recipe Name", fg='#227C19', bg='#F7FF00',
#                     font=("gabriola", 40), relief="solid", borderwidth=3).grid(columnspan=2, row=0, column=0,sticky='ew', pady=10, padx=150, ipady=20)
    type_label=Label(grid_frame, text="Type: {}".format(recipe_info["type"]), fg='white', bg=PURPLE_BUTTON_COLOR,
                    font=("gabriola", 20), relief="solid", borderwidth=3).grid(row=0, column=0,sticky='ew', padx=50, pady=10, ipady=20)
    time_label=Label(grid_frame, text="Time: {} hrs".format(recipe_info["time"]), fg='white', bg=PURPLE_BUTTON_COLOR,
                    font=("gabriola", 20), relief="solid", borderwidth=3).grid(row=0, column=1,sticky='ew', padx=50, pady=10, ipady=20)
    # nothing_label=Label(grid_frame, text="", fg='white', bg=PURPLE_BUTTON_COLOR,
    #                 font=("gabriola", 20), relief="solid", borderwidth=3).grid(columnspan=2, row=1, column=0, sticky='ew', ipady=40, pady=10)
    ingredients_label=Label(grid_frame, text="Ingredients", fg='white', bg=PURPLE_BUTTON_COLOR,
                    font=("gabriola", 20), relief="solid", borderwidth=3).grid(row=1, column=0,sticky='ew', padx=screen_width/10, ipady=25)
    steps_label=Label(grid_frame, text="Steps", fg='white', bg=PURPLE_BUTTON_COLOR,
                    font=("gabriola", 20), relief="solid", borderwidth=3).grid(row=1, column=1,sticky='ew', padx=screen_width/10, ipady=25)
    
    ingredients_text = tk.Text(grid_frame, border=3, fg='white', bg=PURPLE_BUTTON_COLOR, font=("Georgia", 20))
    ingredients_text.insert(END, "\n".join(DAO_OBJ.find_ingredients_by_recipe(recipe_name)))
    ingredients_text.configure(state="disabled")
    ingredients_text.grid(row=2, column=0,sticky='sew', padx=10, pady=10)
    steps_text = tk.Text(grid_frame, border=3, fg='white', bg=PURPLE_BUTTON_COLOR, font=("Georgia", 20))
    steps_text.insert(END, "\n".join(recipe_info["steps"]))
    steps_text.configure(state="disabled")
    steps_text.grid(row=2, column=1,sticky='sew', padx=10, pady=10)

    complete_recipe_btn = Button(grid_frame, text="Complete Recipe", fg='white', bg=PURPLE_BUTTON_COLOR, bd=7, font=("Georgia", 20),
                            command=lambda name=recipe_name: complete_recipe(recipe_name))
    complete_recipe_btn.grid(row=3, column=1, sticky="nsew", padx=50)
    
    # Add a button to the top right for adding ingredients to shopping list
    shop_recipe_btn=Button(text="Shop Missing Ingredients", fg='white', bg=DARK_BLUE_FRAME_BG, bd=7, font = ("Gariola", 18),
                            relief="solid", command=lambda: DAO_OBJ.shopping_by_recipe(USER, recipe_name), wraplength=300)
    shop_recipe_btn.place(relx=0.99, rely=0.03, relheight=.14, anchor="ne")
    nodes.append(shop_recipe_btn)
    
    # Log the border_frame for deletion later
    nodes.append(border_frame)


def get_food_score(food_name, food_scores):
    for item in food_scores:
        if item["name"] == food_name:
            return item["score"]
    else:
        return -1


def create_food_inventory(page=0, going_back=False, pass_through=None):
    # Only reset screen if need to draw for the first time
    if not pass_through:
        reset_screen()
        border_frame, inventory_frame = create_inner_box()
    # Check lower bound on page
    if page < 0:
        page = 0

    if not going_back:
        BACK_STATE.append("food_inventory")

    # Only draw the elements if this is first time through
    if not pass_through:
        food_blocks = []
        for i in range(0, 5):
            # Keep references to all objects
            new_food_set = {}
            # Change the top label colors for visibility
            label_color = PURPLE_BUTTON_COLOR if i else "#B3388C"
            # Each "recipe" will be a box in a row, not scrollable, but able to go left to right
            entry_frame = Frame(inventory_frame, bg=DARK_BLUE_FRAME_BG)
            entry_frame.place(relx=.5, rely=.04 + .19 * i, relheight=.15, relwidth=.95, anchor="n")

            new_food_set["frame"] = entry_frame

            # Now need to add the internal blocks
            # Used for indexing for the name
            label_names = ["Name", "Quantity", "Expiration Date", "Purchase Date", "Likability"] #took Location out
            # Adding the first three labels on the left side
            for j in range(0, 5):
                new_label = Label(entry_frame, text=label_names[j], fg='white', bg=label_color, borderwidth=3,
                              font=("Gariola", 12), wraplength=100)
                new_label.place(relx=.08 + .14 * j, rely=.1, relheight=.8, relwidth=.12, anchor='n')
                new_food_set[label_names[j].lower()] = new_label
            # Now add the preparable label on the right
            substitute_label = Label(entry_frame, text="Substitutes", fg='white', bg=label_color, borderwidth=3,
                              font=("Gariola", 12), wraplength=200)
            substitute_label.place(relx=.9, rely=.1, relheight=.8, relwidth=.16, anchor='n')
            # Check mark = u"\u2713"
            new_food_set["substitutes"] = substitute_label

            food_blocks.append(new_food_set)
    # Just grab the passed UI elements if they exist
    else:
        food_blocks = pass_through["food_blocks"]
    
    # Only get the inventory again if we are not passing through
    if not pass_through:
        food_inv = DAO_OBJ.get_inventory(USER)
    else:
        food_inv = pass_through["food_inventory"]

    food_scores = DAO_OBJ.get_scored_ingredients(USER)

    # First get the index we need based on the page
    food_index = 0
    blank_rest = False
    # First need to raise the recipes_index for the current page
    if page != 0:
        for i in range(page):
            if food_index + 4 < len(food_inv):
                food_index += 4
            else:
                page = i
                break
    # Set title after page is fixed
    title_lbl.config(text = "Food Inventory Page {}".format(page + 1))
    # Now setting the different entries
    for i in range(4):
        if food_index not in range(len(food_inv)):
            blank_rest = True

        if not blank_rest:
            # Set the click to reach food page
            bind_frame_and_children(food_blocks[i+1]["frame"], lambda e, food_inv=food_inv, name=food_inv[food_index]["name"]:create_food_page(name, food_inv))

        food_blocks[i+1]['name'].config(text=food_inv[food_index]["name"] if not blank_rest else "")
        food_blocks[i+1]['quantity'].config(text=food_inv[food_index]["quantity"] if not blank_rest else "")
        food_blocks[i+1]['likability'].config(text=get_food_score(food_inv[food_index]["name"], food_scores) if not blank_rest else "")
        food_blocks[i+1]['expiration date'].config(text=food_inv[food_index]["expiration"] if not blank_rest else "")
        food_blocks[i+1]['purchase date'].config(text=food_inv[food_index]["purchase"] if not blank_rest else "")
        if blank_rest:
            food_blocks[i+1]["substitutes"].config(text="")
        food_index += 1
    
    l_arrow, r_arrow = create_left_right_arrows()
    
    l_arrow.config(command=lambda: create_food_inventory(page=page-1, going_back=True, pass_through=pass_through))
    r_arrow.config(command=lambda: create_food_inventory(page=page+1, going_back=True, pass_through=pass_through))
    
    if not pass_through:
        nodes.append(border_frame)

    # Pass through the UI elements so we dont need to redraw for no reason
    pass_through = {"food_blocks": food_blocks, "l_arrow": l_arrow, "r_arrow":r_arrow, "food_inventory": food_inv}


def _get_food_by_name(food_name, food_inv):
    for food in food_inv:
        if food["name"] == food_name:
            return food 
    return None


def create_food_page(food_name, food_inv):
    reset_screen()
    title_lbl.config(text = "{} Page".format(food_name))
    BACK_STATE.append("food_page")

    food_obj = _get_food_by_name(food_name, food_inv)
    subs = DAO_OBJ.get_substitutes(food_name)
    
    border_frame, recipes_frame = create_inner_box()
    
    border_size = 8
    
    recipes_frame.grid_rowconfigure(0, weight=1)
    recipes_frame.grid_rowconfigure(1, weight=1)
    # recipes_frame.grid_rowconfigure(2, weight=2)
    recipes_frame.grid_columnconfigure(0, weight=1)
    recipes_frame.grid_columnconfigure(1, weight=1)
    
    quant_label = Label(recipes_frame, text="Quantity: {}".format(food_obj["quantity"]), fg='white', bg=PURPLE_BUTTON_COLOR, borderwidth=2, 
                          font=("Gariola", 20), wraplength=400, relief="solid")
    quant_label.bind('<Configure>', lambda e: quant_label.config(wraplength=quant_label.winfo_width()))
    quant_label.grid(row=0, column=0,sticky='nsew')
    
    expdate_label = Label(recipes_frame, text="Expiration Date: {}".format(food_obj["expiration"]), fg='white', bg=PURPLE_BUTTON_COLOR, borderwidth=2,
                          font=("Gariola", 20), wraplength=400, relief="solid")
    expdate_label.bind('<Configure>', lambda e: expdate_label.config(wraplength=expdate_label.winfo_width()))
    expdate_label.grid(row=1, column=0,sticky='nsew')
    purchdate_label = Label(recipes_frame, text="Purchase Date: {}".format(food_obj["purchase"]), fg='white', bg=PURPLE_BUTTON_COLOR, borderwidth=2,
                          font=("Gariola", 20), wraplength=400, relief="solid")
    purchdate_label.bind('<Configure>', lambda e: purchdate_label.config(wraplength=purchdate_label.winfo_width()))
    purchdate_label.grid(row=1, column=1,sticky='nsew')

    substitutes_label = Label(recipes_frame, text="Substitutions: {}".format(", ".join(subs) if subs else "None"), fg='white', bg=PURPLE_BUTTON_COLOR, borderwidth=2,
                          font=("Gariola", 20), wraplength=800, relief="solid")
    substitutes_label.bind('<Configure>', lambda e: substitutes_label.config(wraplength=substitutes_label.winfo_width()))
    substitutes_label.grid(row=0, column=1,sticky='nsew')
    
    nodes.append(border_frame)

    
def generate_random_weekplan():
    import copy
    all_recipes = DAO_OBJ.get_scored_recipes(USER)
    # Remove all recipes of score 0 as we dont want those to be recommended
    remove_recipes = []
    for recipe in all_recipes:
        if recipe["score"] == 0:
            remove_recipes.append(recipe)
    for recipe in remove_recipes:
        all_recipes.remove(recipe)

    recipe_plan = []
    # duplicate recipes as little as possible, go through all before repeating
    recipes_left = None
    for i in range(7):
        if not recipes_left:
            recipes_left = copy.deepcopy(all_recipes)
        next_choice = random.choice(recipes_left)
        next_choice["completed"] = False
        recipes_left.remove(next_choice)
        recipe_plan.append(next_choice)

    return recipe_plan


def create_weekplan_page(going_back=False):
    reset_screen()
    title_lbl.config(text = "Weekly Meal Plan")
    if not going_back:
        BACK_STATE.append("week_plan")
    outer_frame = Frame(bg=BACKGROUND_COLOR)

    outer_frame.place(relx=.5, rely= .2, relheight=.8, relwidth=1, anchor="n")
    outer_frame.grid_rowconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(1, weight=1)
    outer_frame.grid_columnconfigure(2, weight=1)
    outer_frame.grid_columnconfigure(3, weight=1)
    outer_frame.grid_columnconfigure(4, weight=1)
    outer_frame.grid_columnconfigure(5, weight=1)
    outer_frame.grid_columnconfigure(6, weight=1)
    
    global WEEK_MEAL_PLAN
    if not WEEK_MEAL_PLAN:
        WEEK_MEAL_PLAN = generate_random_weekplan()

    border_size = 8
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for i in range(7):
        entry_frame = Frame(outer_frame, bg='#06510C')
        inner_day_frame = Frame(entry_frame, bg=GREY_BG_COLOR)
        
        inner_day_frame.pack(expand=True, fill='both', padx=border_size, pady=border_size)
        entry_frame.grid(row=0, column=i, padx=10, pady=20, sticky='nsew')
        
        inner_day_frame.grid_columnconfigure(0, weight=1)
        inner_day_frame.grid_rowconfigure(0, weight=1)
        inner_day_frame.grid_rowconfigure(1, weight=1)
        inner_day_frame.grid_rowconfigure(2, weight=1)
        inner_day_frame.grid_rowconfigure(3, weight=1)
        # Now adding the actual recipe info
        day_label = Label(inner_day_frame, text=days[i], fg='black', borderwidth=2, bg=PURPLE_BUTTON_COLOR,
                          font=("Gariola", 14), wraplength=120, relief="solid").grid(row=0, column=0,sticky='nsew')
        recipe_label = Label(inner_day_frame, text="Recipe: {}".format(WEEK_MEAL_PLAN[i]["name"]), fg='black', borderwidth=2,
                          font=("Gariola", 14), wraplength=120, relief="solid").grid(row=1, column=0,sticky='nsew')
        time_label = Label(inner_day_frame, text="Time: {} hrs".format(WEEK_MEAL_PLAN[i]["time"]), fg='black', borderwidth=2,
                          font=("Gariola", 14), wraplength=120, relief="solid").grid(row=2, column=0,sticky='nsew')
        completed_label = Label(inner_day_frame, text="Completed: [{}]".format(u"\u2713" if WEEK_MEAL_PLAN[i]["completed"] else " "), fg='black', borderwidth=2,
                          font=("Gariola", 14), wraplength=120, relief="solid").grid(row=3, column=0,sticky='nsew')
        
        # Add on click
        bind_frame_and_children(inner_day_frame, lambda e, index=i: create_dayplan_page(days[index], WEEK_MEAL_PLAN[index]))
        
    nodes.append(outer_frame)


def switch_meal_completed(label, recipe):
    if "[ ]" in label.cget("text"):
        label.config(text="Completed [{}]".format(u"\u2713"))
        recipe["completed"] = True
        complete_recipe(recipe["name"])
    # Dont let it switch back
    # else:
    #     label.config(text="Completed [ ]")


def create_dayplan_page(day, recipe, going_back=False):
    reset_screen()
    title_lbl.config(text = "{} Meal Plan".format(day))
    if not going_back:
        BACK_STATE.append("day_plan_" + day)
    
    border_frame, recipes_frame = create_inner_box()
    
    recipes_frame.grid_rowconfigure(0, weight=1)
    recipes_frame.grid_rowconfigure(1, weight=1)
    recipes_frame.grid_rowconfigure(2, weight=1)
    recipes_frame.grid_columnconfigure(0, weight=1)
    recipes_frame.grid_columnconfigure(1, weight=1)
    
    recipe_btn=Button(recipes_frame, text="Recipe", fg='white', bg=PURPLE_BUTTON_COLOR, bd=7, font = ("Gariola", 14),
                            relief="ridge", command=lambda: create_recipe_page(recipe["name"]))
    recipe_btn.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=50, pady=20)
    time_label = Label(recipes_frame, text="Time: 1 hr and some minutes", fg='white', borderwidth=2, bg=PURPLE_BUTTON_COLOR,
                          font=("Gariola", 14), wraplength=120, relief="solid").grid(padx=75, pady=15, row=0, column=0,sticky='nsew', columnspan=2)
    completed_label = Label(recipes_frame, text="Completed [ ]", fg='white', borderwidth=2, bg=PURPLE_BUTTON_COLOR,
                          font=("Gariola", 14), wraplength=250, relief="solid")
    completed_label.grid(row=2, column=0,sticky='nsew')
    
    recipe_btn=Button(recipes_frame, text="Complete Meal", fg='white', bg=PURPLE_BUTTON_COLOR, bd=7, font = ("Gariola", 14),
                            relief="ridge", command=lambda: switch_meal_completed(completed_label, recipe))
    recipe_btn.grid(row=2, column=1, sticky='nsew')
    
    nodes.append(border_frame)

    
def add_preference(entry, pref_entry, text_area):
    new_food = entry.get()
    pref_num = pref_entry.get()
    if not new_food or not pref_num:
        tk.messagebox.showwarning(title="Missing Info", message="Missing either the food name, or preference level!")
    else:
         text_area.insert("end", "\u0333".join(new_food) + "\u0333: {}\n".format(pref_num))
         DAO_OBJ.set_score(USER, new_food, int(pref_num))

def create_user_pref_page(going_back=False):
    reset_screen()
    title_lbl.config(text = "User Preferences")
    if not going_back:
        BACK_STATE.append("user_prefs")
        
    user_prefs = {}
        
    border_color = Frame(background="black")
    text_area = tk.Text(border_color, border=0, bg="light grey", font=("Georgia", 20))
    
    # Instructions at the top
    text_area.insert("end", "\u0333".join("<Ingredient>") + "\u0333: <Preference 0-10>\n")
    text_area.insert("end", "================================\n\n")
    # Can print default user prefs here after loading them from DB
    # Insert each line separately for individual clicking
    # for item in temp_list:
    #     text_area.insert("end", "\u0333".join(item) + "\u0333: {}".format(temp_list[item]))
    #     text_area.insert("end", "\n")
    
    # Creating the black border
    border_size = 5
    text_area.pack(expand=True, fill='both', padx=border_size, pady=border_size)
    border_color.place(relx=.5, rely=.3, anchor='n', relheight=.6, relwidth=.8)
    
    # Add a scroll bar
    scroll_bar = tk.Scrollbar(text_area, command=text_area.yview)
    scroll_bar.pack(side=tk.RIGHT, fill='y')
    text_area.config(yscrollcommand=scroll_bar.set)
    
    # Add the entry box for adding items
    entry = ttk.Entry(font=("Georgia", 15))
    entry.place(relx=.45, rely=.3, relwidth=.35, relheight=.04, anchor="se")
    
    pref_entry = ttk.Combobox(root, state="readonly", 
                  values=(0,1,2,3,4,5,6,7,8,9,10))
    pref_entry.place(relx=.45, rely=.3, relwidth=.35, relheight=.04, anchor="sw")
    
    add_btn = Button(command=lambda: add_preference(entry, pref_entry, text_area), text="Add", font=("Georgia", 15), bg=DARK_BLUE_FRAME_BG, bd=2, fg="white", activebackground='#CED500')
    add_btn.place(relx=.8, rely=.3, relwidth=.1, relheight=.04, anchor="sw")
    
    # Need to log the nodes for deletion later
    nodes.append(pref_entry)
    nodes.append(add_btn)
    nodes.append(entry)
    nodes.append(border_color)
    
    
def create_main_screen():
    reset_screen()
    title_lbl.config(text = "Chef")
    
    # Place the mainscreen buttons
    MAIN_BUTTON_HEIGHT = .25
    MAIN_BUTTON_WIDTH = .25
    MAIN_BORDER_SIZE = 7
    MAIN_BUTTON_FONT = "gabriola 30"
    
    shopping_list_btn=Button(root, text="Shopping List", fg='black', bg='light grey', bd=MAIN_BORDER_SIZE, font = (MAIN_BUTTON_FONT),
                            relief="ridge", command=lambda: create_shopping_list())
    shopping_list_btn.place(relx=.3, rely=.3, relheight=MAIN_BUTTON_HEIGHT, relwidth=MAIN_BUTTON_WIDTH, anchor = 'n')

    week_plan_btn=Button(root, text="Week Meal Plan", fg='black', bg='light grey', bd=MAIN_BORDER_SIZE, font = (MAIN_BUTTON_FONT),
                         relief="ridge", command=create_weekplan_page)
    week_plan_btn.place(relx=.7, rely=.3, relheight=MAIN_BUTTON_HEIGHT, relwidth=MAIN_BUTTON_WIDTH, anchor = 'n')

    recipe_list_btn=Button(root, text="Recipe List", fg='black', bg='light grey', bd=MAIN_BORDER_SIZE, font = (MAIN_BUTTON_FONT),
                           relief="ridge", command=create_recipe_list)
    recipe_list_btn.place(relx=.3, rely=.6, relheight=MAIN_BUTTON_HEIGHT, relwidth=MAIN_BUTTON_WIDTH, anchor = 'n')

    food_inv_btn=Button(root, text="Food Inventory", fg='black', bg='light grey', bd=MAIN_BORDER_SIZE, font = (MAIN_BUTTON_FONT),
                        relief="ridge", command=create_food_inventory)
    food_inv_btn.place(relx=.7, rely=.6, relheight=MAIN_BUTTON_HEIGHT, relwidth=MAIN_BUTTON_WIDTH, anchor = 'n')
    
    # Add the user pref button to top right
    user_pref_btn=Button(text="User Preferences", fg='white', bg=DARK_BLUE_FRAME_BG, bd=7, font = ("Gariola", 18),
                            relief="solid", command=lambda: create_user_pref_page(), wraplength=300)
    user_pref_btn.place(relx=0.99, rely=0.03, relheight=.14, anchor="ne")
    nodes.append(user_pref_btn)
    
    for element in [food_inv_btn, recipe_list_btn, week_plan_btn, shopping_list_btn]:
        nodes.append(element)


root = tk.Tk()
root.title('Tkinter Window Demo')
root.resizable(height = 1, width = 1)
# root.state("zoomed")
# get the screen dimension
screen_width = int(root.winfo_screenwidth()/1.1)
screen_height = int(root.winfo_screenheight()/1.1)

nodes = []

# Change background color
root.configure(bg=BACKGROUND_COLOR)

# set the position of the window to the center of the screen
root.geometry(f'{screen_width}x{screen_height}+{0}+{0}')

# Place the title label
title_lbl=Label(root, text="Chef", fg='#227C19', bg='#F7FF00',
                font=("gabriola", 60), relief="solid", borderwidth=3)
title_lbl.place(relx=.5, rely=0, relheight=.2, relwidth=1, anchor = 'n')

back_btn = Button(root, text="\u2190", font=("gabriola", 50), bg='#F7FF00', bd=0, activebackground='#CED500', command=go_back)
back_btn.place(relx=0.01, rely=0.01, relheight=.18)

create_main_screen()


root.mainloop()
