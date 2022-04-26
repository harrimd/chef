from conversions import *

import json

infile = open("recipes_uniq.json", "r")
outfile = open("ingredients.json", "w")

ingredients = []
count = 0
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
                    if ingredient not in ingredients:
                        ingredients.append(ingredient)
                    break
outfile.write(json.dumps(ingredients))
