import tkinter as tk
from tkinter import *
from tkinter import ttk
import random

# Keep track of which page we are on for going backwards
# main, recipe, recipe_list, shopping_list
BACK_STATE = []

# Default colors for some things
PURPLE_BUTTON_COLOR = '#9C8DFF'
DARK_BLUE_FRAME_BG = "#174169"
BACKGROUND_COLOR = '#2D9CB5'
GREY_BG_COLOR = "#9A9999"

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
    # get the index of the mouse click
    index = event.widget.index("@%s,%s" % (event.x, event.y))

    # get the indices of all "adj" tags
    tag_indices = list(event.widget.tag_ranges('tag'))

    # iterate them pairwise (start and end index)
    for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
        # check if the tag matches the mouse click index
        if event.widget.compare(start, '<=', index) and event.widget.compare(index, '<', end):
            # Switch between crossed out or not
            if event.widget.get(start) != u'\u0336':
                new_line = ''.join([u'\u0336{}'.format(c) for c in event.widget.get(start, end)]) + u'\u0336'
            else:
                new_line = event.widget.get(start, end).replace(u'\u0336', "")
            event.widget.replace(start, end, new_line, "tag")

            
def add_item(event):
    global text_area
    try:
        new_item = event.widget.get()
        if new_item:
            # Add to the on-screen list
            text_area.insert("end", " \u2022 {}".format(new_item), "tag")
            text_area.insert("end", "\n")
            
            event.widget.delete(0, "end")
            # TODO: Update the backend list
    except Exception as e:
        print("error somehow adding item??")
        print(e)
            

def create_shopping_list(going_back=False):
    reset_screen()
    title_lbl.config(text = "Shopping List")
    if not going_back:
        BACK_STATE.append("shopping_list")
    
    temp_list = ["orange", "grapes", "chicken", "beef", "eggs"]
    global text_area
    global nodes
    
    border_color = Frame(background="black")
    text_area = tk.Text(border_color, border=0, bg="light grey", font=("Georgia", 20))
    text_area.bind("<B1-Motion>", lambda e: "break")
    text_area.bind("<Double-Button-1>", lambda e: "break")
    text_area.bind("<Key>", lambda e: "break")

    # Setting the clicking stuff
    text_area.tag_config("tag")
    text_area.tag_bind("tag", "<Button-1>", shopping_list_item_click)
    
    # Insert each line separately for individual clicking
    for item in temp_list:
        text_area.insert("end", " \u2022 {}".format(item), "tag")
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
    
    # Need to log the nodes for deletion later
    nodes.append(entry)
    nodes.append(border_color)


def create_recipe_list(page=0, going_back=False, pass_through=None):
    # First time into this page, so need to draw everything
    if not pass_through:
        reset_screen()
        border_frame, recipes_frame = create_inner_box()
    # Check lower bound on page
    if page < 0:
        page = 0
    title_lbl.config(text = "Recipe List Page {}".format(page))
    if not going_back:
        BACK_STATE.append("recipe_list")
    
    # just a default list of recipes
    recipes = [
        {"name": "Quesadilla",
         "type": "Mexican",
         "time": 1.0,
          "preparable": True},
        {"name": "Cashew Chicken",
         "type": "Asian",
         "time": 2.0,
          "preparable": False},
        {"name": "Cheeseburger",
         "type": "American",
         "time": .5,
          "preparable": True},
        {"name": "Chili",
         "type": "-",
         "time": 1.5,
          "preparable": True}
    ]

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
            label_names = ["Name", "Type", "Time"]
            # Adding the first three labels on the left side
            for j in range(0, 3):
                new_label = Label(entry_frame, text=label_names[j], fg='white', bg=label_color, borderwidth=3,
                              font=("Gariola", 20), wraplength=200)
                new_label.place(relx=.1 + .18 * j, rely=.1, relheight=.8, relwidth=.16, anchor='n')
                new_recipe_set[label_names[j].lower()] = new_label
            # Now add the preparable label on the right
            prepare_label = Label(entry_frame, text="Preparable", fg='white', bg=label_color, borderwidth=3,
                              font=("Gariola", 20), wraplength=200)
            prepare_label.place(relx=.9, rely=.1, relheight=.8, relwidth=.16, anchor='n')
            # Check mark = u"\u2713"
            new_recipe_set["preparable"] = prepare_label

            # Only click to recipe pages on non-1st row entries
            if i:
                bind_frame_and_children(entry_frame, create_recipe_page)

            recipe_blocks.append(new_recipe_set)

    # Was pass through so just get the elements out
    else:
        recipe_blocks = pass_through["recipe_blocks"]
    
    # Now setting the different entries
    for i in range(4):
        recipe_blocks[i+1]['name'].config(text=recipes[i]['name']  + str(page))
        recipe_blocks[i+1]['type'].config(text=recipes[i]['type'])
        recipe_blocks[i+1]['time'].config(text=str(recipes[i]['time']) + " hr(s)")
        recipe_blocks[i+1]['preparable'].config(text=u"\u2713" if recipes[i]['preparable'] else "X")
    
    # Add the arrows
    l_arrow, r_arrow = create_left_right_arrows()
    # Pass through the UI elements so we dont need to redraw for no reason
    pass_through = {"recipe_blocks": recipe_blocks, "l_arrow": l_arrow, "r_arrow":r_arrow}
    l_arrow.config(command=lambda: create_recipe_list(page=page-1, going_back=True, pass_through=pass_through))
    r_arrow.config(command=lambda: create_recipe_list(page=page+1, going_back=True, pass_through=pass_through))

    # Log the border_frame for deletion later
    nodes.append(border_frame)


def create_recipe_page(event, going_back=False):
    reset_screen()
    title_lbl.config(text = "Recipe Info Page")
    if not going_back:
        BACK_STATE.append("recipe_page")
    
    border_size = 8
    # Outside frame to make a border
    border_frame = Frame(bg="black")
    
    # Placing the labels for the recipe info
    grid_frame = Frame(border_frame, bg=DARK_BLUE_FRAME_BG, bd=5)
    grid_frame.pack(expand=True, fill='both', padx=border_size, pady=border_size)
    border_frame.place(relx=.5, rely= .21, relheight=.78, relwidth=.98, anchor="n")
    
    grid_frame.grid_rowconfigure(0, weight=1)
    grid_frame.grid_rowconfigure(1, weight=2)
    grid_frame.grid_rowconfigure(2, weight=1)
    grid_frame.grid_rowconfigure(3, weight=4)
    grid_frame.grid_columnconfigure(0, weight=1)
    grid_frame.grid_columnconfigure(1, weight=1)
    
#     recipe_label=Label(grid_frame, text="Recipe Name", fg='#227C19', bg='#F7FF00',
#                     font=("gabriola", 40), relief="solid", borderwidth=3).grid(columnspan=2, row=0, column=0,sticky='ew', pady=10, padx=150, ipady=20)
    type_label=Label(grid_frame, text="Type: <Food Type>", fg='white', bg=PURPLE_BUTTON_COLOR,
                    font=("gabriola", 40), relief="solid", borderwidth=3).grid(row=0, column=0,sticky='ew', padx=50, pady=10, ipady=30)
    time_label=Label(grid_frame, text="Time: X hrs", fg='white', bg=PURPLE_BUTTON_COLOR,
                    font=("gabriola", 40), relief="solid", borderwidth=3).grid(row=0, column=1,sticky='ew', padx=50, pady=10, ipady=30)
    nothing_label=Label(grid_frame, text="", fg='white', bg=PURPLE_BUTTON_COLOR,
                    font=("gabriola", 40), relief="solid", borderwidth=3).grid(columnspan=2, row=1, column=0, sticky='ew', ipady=40, pady=10)
    ingredients_label=Label(grid_frame, text="Ingredients", fg='white', bg=PURPLE_BUTTON_COLOR,
                    font=("gabriola", 40), relief="solid", borderwidth=3).grid(row=2, column=0,sticky='ew', padx=screen_width/10, ipady=35)
    steps_label=Label(grid_frame, text="Steps", fg='white', bg=PURPLE_BUTTON_COLOR,
                    font=("gabriola", 40), relief="solid", borderwidth=3).grid(row=2, column=1,sticky='ew', padx=screen_width/10, ipady=35)
    
    ingredients_text = tk.Text(grid_frame, border=3, fg='white', bg=PURPLE_BUTTON_COLOR, font=("Georgia", 20)).grid(row=3, column=0,sticky='sew', padx=10, pady=10)
    steps_text = tk.Text(grid_frame, border=3, fg='white', bg=PURPLE_BUTTON_COLOR, font=("Georgia", 20)).grid(row=3, column=1,sticky='sew', padx=10, pady=10)
    
    # Add a button to the top right for adding ingredients to shopping list
    shop_recipe_btn=Button(text="Shop Missing Ingredients", fg='white', bg=DARK_BLUE_FRAME_BG, bd=7, font = ("Gariola", 18),
                            relief="solid", command=lambda: print("To be added later..."), wraplength=300)
    shop_recipe_btn.place(relx=0.99, rely=0.03, relheight=.14, anchor="ne")
    nodes.append(shop_recipe_btn)
    
    # Log the border_frame for deletion later
    nodes.append(border_frame)


def create_food_inventory(page=0, going_back=False, pass_through=None):
    # Only reset screen if need to draw for the first time
    if not pass_through:
        reset_screen()
        border_frame, inventory_frame = create_inner_box()
    # Check lower bound on page
    if page < 0:
        page = 0
    title_lbl.config(text = "Food Inventory Page {}".format(page))
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
            label_names = ["Name", "Quantity", "Location", "Expiration Date", "Purchase Date"]
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

            # Only click to recipe pages on non-1st row entries
            if i:
                bind_frame_and_children(entry_frame, create_food_page)

            food_blocks.append(new_food_set)
    # Just grab the passed UI elements if they exist
    else:
        food_blocks = pass_through["food_blocks"]
    
    # Now setting the different entries
    for i in range(4):
        food_blocks[i+1]['name'].config(text="Name"  + str(page))
        food_blocks[i+1]['quantity'].config(text="Quantity")
        food_blocks[i+1]['location'].config(text="Location")
        food_blocks[i+1]['expiration date'].config(text='expiration date')
        food_blocks[i+1]['purchase date'].config(text='purchase date')
    
    l_arrow, r_arrow = create_left_right_arrows()
    
    # Pass through the UI elements so we dont need to redraw for no reason
    pass_through = {"food_blocks": food_blocks, "l_arrow": l_arrow, "r_arrow":r_arrow}
    
    l_arrow.config(command=lambda: create_food_inventory(page=page-1, going_back=True, pass_through=pass_through))
    r_arrow.config(command=lambda: create_food_inventory(page=page+1, going_back=True, pass_through=pass_through))
    
    nodes.append(border_frame)

    
def create_food_page(event):
    reset_screen()
    title_lbl.config(text = "Food Page")
    BACK_STATE.append("food_page")
    
    border_frame, recipes_frame = create_inner_box()
    
    border_size = 8
    
    recipes_frame.grid_rowconfigure(0, weight=1)
    recipes_frame.grid_rowconfigure(1, weight=1)
    recipes_frame.grid_rowconfigure(2, weight=2)
    recipes_frame.grid_columnconfigure(0, weight=1)
    recipes_frame.grid_columnconfigure(1, weight=1)
    
    quant_label = Label(recipes_frame, text="Quantity: <#>", fg='white', bg=PURPLE_BUTTON_COLOR, borderwidth=2, 
                          font=("Gariola", 20), wraplength=400, relief="solid")
    quant_label.bind('<Configure>', lambda e: quant_label.config(wraplength=quant_label.winfo_width()))
    quant_label.grid(row=0, column=0,sticky='nsew')
    
    loc_label = Label(recipes_frame, text="Location: <loc>", fg='white', bg=PURPLE_BUTTON_COLOR, borderwidth=2,
                          font=("Gariola", 20), wraplength=400, relief="solid")
    loc_label.bind('<Configure>', lambda e: loc_label.config(wraplength=loc_label.winfo_width()))
    loc_label.grid(row=0, column=1,sticky='nsew')
    
    expdate_label = Label(recipes_frame, text="Expiration Date: <##/##/##>", fg='white', bg=PURPLE_BUTTON_COLOR, borderwidth=2,
                          font=("Gariola", 20), wraplength=400, relief="solid")
    expdate_label.bind('<Configure>', lambda e: expdate_label.config(wraplength=expdate_label.winfo_width()))
    expdate_label.grid(row=1, column=0,sticky='nsew')
    purchdate_label = Label(recipes_frame, text="Purchase Date: <##/##/##>", fg='white', bg=PURPLE_BUTTON_COLOR, borderwidth=2,
                          font=("Gariola", 20), wraplength=400, relief="solid")
    purchdate_label.bind('<Configure>', lambda e: purchdate_label.config(wraplength=purchdate_label.winfo_width()))
    purchdate_label.grid(row=1, column=1,sticky='nsew')

    substitutes_label = Label(recipes_frame, text="Substitutions: XXX,YYY,ZZZ,...", fg='white', bg=PURPLE_BUTTON_COLOR, borderwidth=2,
                          font=("Gariola", 20), wraplength=800, relief="solid")
    substitutes_label.bind('<Configure>', lambda e: substitutes_label.config(wraplength=substitutes_label.winfo_width()))
    substitutes_label.grid(row=2, column=0,columnspan=2,sticky='nsew')
    
    nodes.append(border_frame)

    
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
        recipe_label = Label(inner_day_frame, text="Recipe: <XXX>", fg='black', borderwidth=2,
                          font=("Gariola", 14), wraplength=120, relief="solid").grid(row=1, column=0,sticky='nsew')
        time_label = Label(inner_day_frame, text="Time: 1 hr and some minutes", fg='black', borderwidth=2,
                          font=("Gariola", 14), wraplength=120, relief="solid").grid(row=2, column=0,sticky='nsew')
        completed_label = Label(inner_day_frame, text="Completed: [X]", fg='black', borderwidth=2,
                          font=("Gariola", 14), wraplength=120, relief="solid").grid(row=3, column=0,sticky='nsew')
        
        # Add on click
        bind_frame_and_children(inner_day_frame, lambda e, index=i: create_dayplan_page(days[index]))
        
    nodes.append(outer_frame)


def switch_meal_completed(label):
    if "[ ]" in label.cget("text"):
        label.config(text="Completed [X]")
    else:
        label.config(text="Completed [ ]")


def create_dayplan_page(day, going_back=False):
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
                            relief="ridge", command=lambda: create_recipe_page(None))
    recipe_btn.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=50, pady=20)
    time_label = Label(recipes_frame, text="Time: 1 hr and some minutes", fg='white', borderwidth=2, bg=PURPLE_BUTTON_COLOR,
                          font=("Gariola", 14), wraplength=120, relief="solid").grid(padx=75, pady=15, row=0, column=0,sticky='nsew', columnspan=2)
    completed_label = Label(recipes_frame, text="Completed [ ]", fg='white', borderwidth=2, bg=PURPLE_BUTTON_COLOR,
                          font=("Gariola", 14), wraplength=250, relief="solid")
    completed_label.grid(row=2, column=0,sticky='nsew')
    
    recipe_btn=Button(recipes_frame, text="Complete/Uncomplete Meal", fg='white', bg=PURPLE_BUTTON_COLOR, bd=7, font = ("Gariola", 14),
                            relief="ridge", command=lambda: switch_meal_completed(completed_label))
    recipe_btn.grid(row=2, column=1, sticky='nsew')
    
    nodes.append(border_frame)


def create_user_pref_page():
    reset_screen()
    title_lbl.config(text = "User Preferences")
    if not going_back:
        BACK_STATE.append("user_prefs")
    
    
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
root.state("zoomed")
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
