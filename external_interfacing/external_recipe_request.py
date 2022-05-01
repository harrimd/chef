from googlesearch import search
from recipe_scrapers import scrape_me

def get_recipe(query):
    query += " recipe"
    for url in search(query, tld="co.in", num=10, stop= 10, pause=2):
        scraper = scrape_me(url, wild_mode=True)
        if scraper.ingredients():
            recipe = {
                'title': scraper.title(),
                'time': scraper.total_time(),
                'yeilds': scraper.yields(),
                'ingredients': scraper.ingredients(),
                'instructions': scraper.instructions(),
                'url': url
            }
            return recipe

#print(get_recipe('Meatloaf'))
