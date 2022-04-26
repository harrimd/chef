
from recipe_scrapers import scrape_me
#import recipe_book
import re
import threading, time, random
import json
from socket import gethostbyname, gaierror

base_url = 'https://www.allrecipes.com/recipe/'
dump_file = 'recipes.json'

regex = '([A-Za-z]+)\)* ([^\n]+)'
ingredient_dict = []
metric_dict = []
mutex = threading.Lock()
f = open('recipes.txt', 'a')

def add_to_metric_dict(metric):
    global metric_dict
    if metric not in metric_dict:
        mutex.acquire()
        metric_dict.append(metric)
        mutex.release()

def add_to_ingredient_dict(ingr):
    global ingredient_dict
    if ingr not in ingredient_dict:
        mutex.acquire()
        ingredient_dict.append(ingr)
        mutex.release()

def write_to_file(scraper, url):
    recipe = {
        'title': scraper.title(),
        'time': scraper.total_time(),
        'yeilds': scraper.yields(),
        'ingredients': scraper.ingredients(),
        'instructions': scraper.instructions(),
        'url': url
    }
    json_recipe = json.dumps(recipe, indent = 0)
    mutex.acquire()
    f.write(json_recipe)
    mutex.release()


def worker(url, i):
    global regex
    #print("start")
    try:
        scraper = scrape_me(url + str(i))
    except Exception as e:
        print(url + str(i) + " does not exist")
    if scraper.ingredients():
        write_to_file(scraper, url + str(i))
    #print("end")
    #ingredients = scraper.ingredients()
    #for ingredient in ingredients:
        #m = re.search(regex, ingredient)
        #if m != None:
            #add_to_metric_dict(m.group(0))
        #if m.group(1) != None:
            #add_to_ingredient_dict(m.group(1))

try:
    for i in range(600, 1000): #286476):
        threads = []
        print(i, end='\r')
        for j in range(0,100):
            t = threading.Thread(target=worker, args=(base_url,10000+i*100+j))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
except KeyboardInterrupt:
    print("Stopped")
    print(metric_dict)
    print("########")
    print(ingredient_dict)
print(metric_dict)
print("########")
print(ingredient_dict)
    # instr_set = InstructionSet(0, [], [])
    # instr_set.updateCooktime(scraper.total_time())
    # instr_set.updateSteplist(scraper.instructions().split("."))
    #
    # recipe = Recipe(scraper.title(), Recipe_ID("", "", ""))
    #
    #
    # scraper.yields()
    # scraper.ingredients()
    #
    # scraper.image()
    # scraper.host()
    # scraper.links()
    # scraper.nutrients()  # if available
    #
    # invent = inventory.Inventory()
    # invent.addIngredient("Dry Spaghetti", 1, 10)
    # invent.addIngredient("Tomatoe Sauce", 1, 5)
    # invent.addIngredient("Meatballs", 10, 0)
