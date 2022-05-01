from conversions import *
import re
import json

infile = open("recipes.json", "r")
outfile = open("ingredients.json", "w")

ingredients = []
count = 0

def get_modifiers(ingredient):
    split_ingredient = ""
    modifier = ""

    parens = re.match("([^\(]+)(\([^\)]+\))?([^\(\)]+)?", ingredient)
    if parens != None and parens.groups()[1] != None:
        split_ingredient += parens.groups()[0]
        modifier += parens.groups()[1].strip()
        if parens.groups()[2] != None:
            split_ingredient += parens.groups()[2]
    else:
        split_ingredient = ingredient

    spleet = split_ingredient.split(",_")
    if len(spleet) > 1:
        modifier +=  spleet[1]
        split_ingredient += spleet[0]
    return modifier.strip(), split_ingredient.strip()

for line in infile.readlines():
    json_entry = json.loads(line)
    ingredients_unparsed = json_entry['ingredients']
    for ingredient_unparsed in ingredients_unparsed:
            parsing = ingredient_unparsed.split()
            for word in parsing:
                if is_in_index(word):
                    print(count, end='\r')
                    count += 1
                    halves = ingredient_unparsed.split(word)
                    ingredient = halves[1].strip().lower()
                    modifier, f_ingredient = get_modifiers(ingredient)
                    undered_ingred = re.sub('[:/ .,;\-\(\)0-9\u00ae\u00f1]+', '_', f_ingredient)
                    if undered_ingred == "":
                        break
                    if undered_ingred not in ingredients:
                        ingredients.append(undered_ingred)
                    break
outfile.write(json.dumps(ingredients))
