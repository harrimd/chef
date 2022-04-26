from conversions import *
from inventory import *
from recipe_book import *
from recipe_request import *

printable_fracts = {'\u00BE': 0.75, '3/4': 0.75, '\u2154': 0.6667, '2/3': 0.6667,
'\u00BD': 0.5, '1/2': 0.5, '\u2153': 0.3334, '1/3': 0.3334, '\u00BC': 0.25,
'1/4': 0.25, '\u215B' : 0.125, '1/8': 0.125, '1/16': 0.0625, '1/32': 0.03125, '1/64': 0.015625}
def replace(number):
    if(number in printable_fracts.keys()):
        return float(printable_fracts[number])
    return float(number)

def get_quantity(quantity_string):
    spleet = quantity_string.split()
    if(len(spleet) > 1):
        return replace(spleet[0]) * replace(spleet[1].strip("("))
    return replace(quantity_string)


def add_ingredients(invent, ingredients_unparsed):
    for ingredient_unparsed in ingredients_unparsed:
            parsing = ingredient_unparsed.split()
            for word in parsing:
                if is_in_index(word):
                    halves = ingredient_unparsed.split(word)
                    quantity = get_quantity(halves[0].strip())

                    metric_name = get_index(word)
                    ingredient = halves[1].strip()

                    invent.addIngredient(ingredient, quantity, metric_name)
                    # print("Quantity: ", quantity)
                    # print("Metric: ", metric_name)
                    # print("Ingredient: ", ingredient)
                    break
    return invent

def add_instructions(instr_set, instructions):
    spleet = instructions.split('.')
    preps = []
    steps = []
    First = True
    for single in spleet:
        stripped = single.strip()
        if ('degrees' in stripped or '\u00B0' in stripped) and First == True:
            preps.append(stripped)
        elif(stripped != ''):
            steps.append(stripped)
        First = False

    instr_set.updatePreplist(preps)
    instr_set.updateSteplist(steps)
    return instr_set

def format_recipe(json_entry):
    title = json_entry['title']
    invent = inventory.Inventory()
    ingredients_unparsed = json_entry['ingredients']
    invent = add_ingredients(invent, ingredients_unparsed)
    #add_tools
    #add_appliances
    time = json_entry['time']
    yields = json_entry['yeilds']
    instructions = json_entry['instructions']

    instr_set = InstructionSet(time, yields, [], [])
    instr_set = add_instructions(instr_set, instructions)

    url = json_entry['url']
    recipe = Recipe(title, instr_set, invent, Recipe_ID("", "", ""), url) #TODO Recipe_ID
    return recipe

json_entry = {"title": "Cathedral Window Holiday Bars","time": 0,"yeilds": "2 serving(s)","ingredients": ["1 cup butter","1 cup packed brown sugar","2 eggs","2 cups all-purpose flour","\u00bd teaspoon salt","8 (1 ounce) squares German sweet chocolate","\u00bd cup butter","2 cups confectioners' sugar","2 eggs","1 (10.5 ounce) package rainbow colored miniature marshmallows","1 cup chopped pecans"],"instructions": "Preheat oven to 350 degrees F (180 degrees C).\nMix 1 cup butter, 1 cup brown sugar and 2 eggs. Stir in 2 cups flour and 1/2 teaspoon salt. Press in ungreased 9 x 13 pan.\nBake for 25 minutes. Let cool.\nHeat chocolate and 1/2 cup butter over low heat, stirring constantly until melted. Remove from heat.\nStir in 2 cups powdered sugar and 2 eggs. Beat until smooth. Stir in marshmallows and pecans. Spread mixture over cookie-base. Refrigerate 2 hours. Cut into bars.","url": "https://www.allrecipes.com/recipe/10054"}
json_entry = get_recipe('Meatloaf')
print(format_recipe(json_entry).toString())
