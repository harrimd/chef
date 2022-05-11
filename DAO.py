from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_URI = os.environ.get("DB_URI")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# Data Access Object
class DAO:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_inventory_item(self, person_name, item):
        with self.driver.session() as session:
            session.write_transaction(\
              self._add_inventory_item, person_name, item)
            print(f'One inventory item {item["name"]} added')

    @staticmethod
    def _add_inventory_item(tx, person_name, item):
        tx.run('MERGE (:Ingredient{name:$item["name"]})',\
          item=item)
        tx.run("""
                MATCH 
                  (p:Person{name:$person_name}), 
                  (i:Ingredient{name:$item["name"]})
                MERGE (p)-[:HAS{
                  quantity:$item["quantity"],
                  expiration:$item["expiration"],
                  purchase:$item["purchase"]
                }]->(i)
              """, person_name=person_name, item=item)

    def delete_inventory_item(self, person_name, item):
        with self.driver.session() as session:
            session.write_transaction(\
              self._delete_inventory_item, person_name, item)
            print(f'One inventory item {item} deleted')

    @staticmethod
    def _delete_inventory_item(tx, person_name, item):
        tx.run("""
          MATCH 
            (:Person{name:$person_name})
            -[r:HAS{purchase:$item["purchase"]}]
            ->(:Ingredient{name:$item["name"]})
          DELETE r
        """, person_name=person_name, item=item)

    def shopping_by_recipe(self, person_name, recipe_name):
        ingredients = self.find_ingredients_by_recipe(recipe_name)
        for i in ingredients:
          self.add_shopping_item(person_name, i)

    def add_shopping_item(self, person_name, ingredient_name):
        with self.driver.session() as session:
            session.write_transaction(\
              self._add_shopping_item, person_name, ingredient_name)
            print(f'One shopping item {ingredient_name} added')

    @staticmethod
    def _add_shopping_item(tx, person_name, ingredient_name):
        tx.run("MERGE (:Ingredient{name:$ingredient_name})",\
          ingredient_name=ingredient_name)
        tx.run("""
                MATCH 
                  (p:Person{name:$person_name}), 
                  (i:Ingredient{name:$ingredient_name})
                MERGE (p)-[:BUYS]->(i)
              """, person_name=person_name, ingredient_name=ingredient_name)

    def delete_shopping_item(self, person_name, ingredient_name):
        with self.driver.session() as session:
            session.write_transaction(\
              self._delete_shopping_item, person_name, ingredient_name)
            print(f'One shopping item {ingredient_name} deleted')

    @staticmethod
    def _delete_shopping_item(tx, person_name, ingredient_name):
        tx.run("""
          MATCH 
            (:Person{name:$person_name})
            -[r:BUYS]
            ->(:Ingredient{name:$ingredient_name})
          DELETE r
        """, person_name=person_name, ingredient_name=ingredient_name)

    def find_ready_recipes_by_person(self, name):
        with self.driver.session() as session:
            recipes = session.read_transaction(\
              self._find_ready_recipes_by_person, name)
            print(f'Find ready recipes of user {name}: {recipes}')
            return recipes

    @staticmethod
    def _find_ready_recipes_by_person(tx, name):
        # NO substitutes
        # query = ("""
        #   MATCH ((r:Recipe)-[:NEEDS]->(i:Ingredient)) 
        #   WITH r, collect(i) AS ingredients 
        #   WHERE all(x IN ingredients WHERE 
        #   (:Person {name:$name})-[:HAS]->(x)) 
        #   RETURN r
        # """)

        # ALLOW substitutes
        query = ("""
          MATCH ((r:Recipe)-[:NEEDS]->(i:Ingredient)) 
          WITH r, collect(i) AS ingredients 
          WHERE all(x IN ingredients WHERE 
            ((:Person {name:"Alan"})-[:HAS]->(x)) 
			      OR 
		        ((:Person {name:"Alan"})-[:HAS]->(:Ingredient)-[:SUBSTITUTES*]->(x)))
          RETURN r
        """)
        result = tx.run(query, name=name)
        return [dict(row.value().items()) for row in result]

    def get_meal_plan(self, name, date):
        with self.driver.session() as session:
            plan = session.read_transaction(\
              self._get_meal_plan, name, date)
            print(f'Get meal plan of {name} on {date}: {plan}')
            return plan

    @staticmethod
    def _get_meal_plan(tx, name, date):
        query = ("""
            MATCH (p:Person)-[pl:PLANS]->(r:Recipe) 
            WHERE p.name = $name AND pl.date = $date
            RETURN r.name, pl.completed
        """)
        result = tx.run(query, name=name, date=date)
        values = result.single().values()
        return {'recipe':values[0], 'completed':values[1]}

    def find_ingredients_by_recipe(self, name):
        with self.driver.session() as session:
            ingredients = session.read_transaction(\
              self._find_ingredients_by_recipe, name)
            print(f'Find ingredients of recipe {name}: {ingredients}')
            return ingredients

    @staticmethod
    def _find_ingredients_by_recipe(tx, name):
        query = ("""
            MATCH (r:Recipe)-[:NEEDS]->(i:Ingredient) 
            WHERE r.name = $name 
            RETURN i.name
        """)
        result = tx.run(query, name=name)
        # get all records as an array of dict objects
        return [row.values()[0] for row in result]

    def get_inventory(self, name):
        with self.driver.session() as session:
            ingredients = session.read_transaction(\
              self._get_inventory, name)
            print(f'Get inventory of user {name}: {ingredients}')
            return ingredients

    @staticmethod
    def _get_inventory(tx, name):
        query = ("""
            MATCH (p:Person)-[r:HAS]->(i:Ingredient) 
            WHERE p.name = $name 
            RETURN i.name, r.quantity, r.expiration, r.purchase
        """)
        result = tx.run(query, name=name)
        # get all records as an array of dict objects
        return [{'name':row.values()[0], 'quantity':row.values()[1], \
                 'expiration':row.values()[2], 'purchase':row.values()[3]\
                } for row in result]

    def get_shopping_list(self, name):
        with self.driver.session() as session:
            ingredients = session.read_transaction(\
              self._get_shopping_list, name)
            print(f'Get shopping list of user {name}: {ingredients}')
            return ingredients

    @staticmethod
    def _get_shopping_list(tx, name):
        query = ("MATCH (:Person{name:$name})-[:BUYS]->(i:Ingredient) RETURN i")
        result = tx.run(query, name=name)
        # get all records as an array of dict objects
        return [dict(row.value().items()) for row in result]

    def get_substitutes(self, name):
        with self.driver.session() as session:
            substitutes = session.read_transaction(self._get_substitutes, name)
            print(f'Get substitutes of {name}: {substitutes}')
            return substitutes

    @staticmethod
    def _get_substitutes(tx, name):
        query = (
            "MATCH (:Ingredient{name:$name})<-[r:SUBSTITUTES*]-(i:Ingredient) "
            "RETURN i.name"
        )
        result = tx.run(query, name=name)
        # get all records as an array of dict objects
        # return [row for row in result]
        return [row.values()[0] for row in result]

    def get_scored_ingredients(self, person_name):
        with self.driver.session() as session:
            ingredients = session.read_transaction(\
              self._get_scored_ingredients, person_name)
            print(f'Get scored ingredients: {ingredients}')
            return ingredients

    @staticmethod
    def _get_scored_ingredients(tx, person_name):
        query = ("""
          MATCH (i:Ingredient)
          OPTIONAL MATCH (i)<-[l:LIKES]-(:Person{name:$person_name}) 
          RETURN i {.*, score: sum(l.score) }
        """)
        result = tx.run(query, person_name=person_name)
        # get all records as an array of dict objects
        return [dict(row.value().items()) for row in result]

    def get_all_ingredients(self):
        with self.driver.session() as session:
            ingredients = session.read_transaction(self._get_all_ingredients)
            print(f'Get all ingredients: {ingredients}')
            return ingredients

    @staticmethod
    def _get_all_ingredients(tx):
        query = ("MATCH (i:Ingredient) RETURN i")
        result = tx.run(query)
        # get all records as an array of dict objects
        return [dict(row.value().items()) for row in result]

    def get_scored_recipes(self, person_name):
        with self.driver.session() as session:
            recipes = session.read_transaction(\
              self._get_scored_recipes, person_name)
            print(f'Get scored recipes: {recipes}')
            return recipes

    @staticmethod
    def _get_scored_recipes(tx, person_name):
        query = ("""
          MATCH (r:Recipe)-[:NEEDS]->(i:Ingredient)
          OPTIONAL MATCH (i)<-[l:LIKES]-(:Person{name:$person_name}) 
          RETURN r {.*, score: sum(l.score) }
        """)
        result = tx.run(query, person_name=person_name)
        return [dict(row.value().items()) for row in result]

    def get_all_recipes(self):
        with self.driver.session() as session:
            recipes = session.read_transaction(self._get_all_recipes)
            print(f'Get all recipes: {recipes}')
            return recipes

    @staticmethod
    def _get_all_recipes(tx):
        query = ("MATCH (r:Recipe) RETURN r")
        result = tx.run(query)
        return [dict(row.value().items()) for row in result]

    def get_recipe(self, name):
        with self.driver.session() as session:
            recipe = session.read_transaction(\
              self._get_recipe, name)
            print(f'Get recipe {name}: {recipe}')
            return recipe

    @staticmethod
    def _get_recipe(tx, name):
        query = ("""
            MATCH (r:Recipe) 
            WHERE r.name = $name 
            RETURN r
        """)
        result = tx.run(query, name=name)
        return dict(result.single().value())

    def get_person(self, name):
        with self.driver.session() as session:
            person = session.read_transaction(self._get_person, name)
            print(f'Get person: {person}')
            return person

    @staticmethod
    def _get_person(tx, name):
        query = ("MATCH (p:Person) WHERE p.name = $name RETURN p")
        result = tx.run(query, name=name)
        # return single record's properties
        return dict(result.single().value().items())

    def init_db(self):
        with self.driver.session() as session:
            session.write_transaction(self._init_db)
            print(f'DB inited')
    
    def set_score(self, person_name, ingredient, score):
          with self.driver.session() as session:
            session.write_transaction(\
              self._set_score, person_name, ingredient, score)
            print(f'Ingredient {ingredient} preference score set to {score}')
            
    @staticmethod
    def _set_score(tx, person, ingredient, score):
          tx.run('MERGE (:Ingredient{name:$ingredient})',\
            ingredient=ingredient)
          tx.run("""
              MATCH 
                (p:Person{name:$person}), 
                (i:Ingredient{name:$ingredient})
              MERGE (p)-[:LIKES{
                score:$score
              }]->(i)
              """, person=person, ingredient=ingredient, score=score)

    @staticmethod
    def _init_db(tx):
        # delete all
        tx.run('MATCH (n) DETACH DELETE n')
        # create nodes
        tx.run('CREATE (:Person{name:"Alan"})')
        tx.run("""
          CREATE 
            (:Recipe{
              name:"Sesame Chicken", 
              type:"Asian",
              time:0.5, 
              preparable:true,
              steps:["Step One", "Step Two", "Step Three"]
            })
        """)
        tx.run("""
          CREATE 
            (:Recipe{
              name:"Sesame Beef", 
              type:"American",
              time:0.25, 
              preparable:false,
              steps:["Step One", "Step Two"]
            })
        """)
        tx.run("""
          CREATE 
            (:Recipe{
              name:"Beef Stir", 
              type:"Asian",
              time:0.25, 
              preparable:false,
              steps:["Step One", "Step Two"]
            })
        """)
        tx.run("""
          CREATE 
            (:Recipe{
              name:"Fried Chicken", 
              type:"Mexican",
              time:0.25, 
              preparable:false,
              steps:["Step One", "Step Two"]
            })
        """)
        tx.run('CREATE (:Ingredient{name:"Sesame"})')
        tx.run('CREATE (:Ingredient{name:"Chicken"})')
        tx.run('CREATE (:Ingredient{name:"Beef"})')
        tx.run('CREATE (:Ingredient{name:"White Sesame"})')
        tx.run('CREATE (:Ingredient{name:"Black Sesame"})')
        tx.run('CREATE (:Ingredient{name:"Black Sesame Powder"})')
        tx.run('CREATE (:Ingredient{name:"Breadcrumbs"})')
        tx.run('CREATE (:Ingredient{name:"Panko"})')
        tx.run("""
            CREATE 
              (:Ingredient{
                name:"Produce",
                similarity:0
            })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Fruit",
                similarity:0.2
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Vegetable",
                similarity:0.2
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Root vegetable",
                similarity:0.7
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Cruciferous vegetable",
                similarity:0.6
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Leafy green",
                similarity:0.8
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Yam",
                similarity:1
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Broccoli",
                similarity:1
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Kale",
                similarity:1
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Spinach",
                similarity:1
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Dairy",
                similarity:0
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Dairy drink",
                similarity:0.7
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Milk",
                similarity:0.9
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Dairy-free milk",
                similarity:0.9
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Oat milk",
                similarity:1
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Soy milk",
                similarity:1
              })
        """)
        tx.run("""
            CREATE
              (:Ingredient{
                name:"Rice milk",
                similarity:1
              })
        """)
        # create relationships
        tx.run("""
          MATCH 
            (r:Recipe{name:"Sesame Chicken"}), 
            (i:Ingredient{name:"Sesame"}) 
          CREATE (r)-[:NEEDS]->(i)
        """)
        tx.run("""
          MATCH 
            (r:Recipe{name:"Sesame Chicken"}), 
            (i:Ingredient{name:"Chicken"}) 
          CREATE (r)-[:NEEDS]->(i)
        """)
        tx.run("""
          MATCH 
            (r:Recipe{name:"Sesame Beef"}), 
            (i:Ingredient{name:"Sesame"}) 
          CREATE (r)-[:NEEDS]->(i)
        """)
        tx.run("""
          MATCH 
            (r:Recipe{name:"Sesame Beef"}), 
            (i:Ingredient{name:"Beef"}) 
          CREATE (r)-[:NEEDS]->(i)
        """)
        tx.run("""
          MATCH 
            (r:Recipe{name:"Beef Stir"}), 
            (i:Ingredient{name:"Beef"}) 
          CREATE (r)-[:NEEDS]->(i)
        """)
        tx.run("""
          MATCH 
            (r:Recipe{name:"Fried Chicken"}), 
            (i:Ingredient{name:"Chicken"}) 
          CREATE (r)-[:NEEDS]->(i)
        """)
        tx.run("""
          MATCH
            (r:Recipe{name:"Fried Chicken"}),
            (i:Ingredient{name:"Panko"})
          CREATE (r)-[:NEEDS]->(i)
        """)
        # tx.run("""
        #   MATCH 
        #     (p:Person{name:"Alan"}), 
        #     (i:Ingredient{name:"Sesame"}) 
        #   CREATE (p)-[:LIKES{score:5}]->(i)
        # """)
        tx.run("""
          MATCH 
            (p:Person{name:"Alan"}), 
            (i:Ingredient{name:"Beef"}) 
          CREATE (p)-[:LIKES{score:7}]->(i)
        """)
        tx.run("""
          MATCH 
            (p:Person{name:"Alan"}), 
            (i:Ingredient{name:"Black Sesame Powder"}) 
          CREATE (p)-[:HAS{
            quantity:0.2, 
            expiration:"2022-01-15", 
            purchase:"2023-01-15"}]->(i)
        """)
        tx.run("""
          MATCH 
            (p:Person{name:"Alan"}), 
            (i:Ingredient{name:"Chicken"}) 
          CREATE (p)-[:HAS{
            quantity:1.5, 
            expiration:"2022-05-02", 
            purchase:"2022-04-25"}]->(i)
        """)
        tx.run("""
          MATCH 
            (p:Person{name:"Alan"}), 
            (i:Ingredient{name:"SoySauce"}) 
          CREATE (p)-[:BUYS]->(i)
        """)
        tx.run("""
          MATCH 
            (i1:Ingredient{name:"White Sesame"}),  
            (i2:Ingredient{name:"Sesame"}) 
          CREATE (i1)-[:SUBSTITUTES]->(i2)
        """)
        tx.run("""
          MATCH 
            (i1:Ingredient{name:"Black Sesame"}), 
            (i2:Ingredient{name:"Sesame"}) 
          CREATE (i1)-[:SUBSTITUTES]->(i2)
        """)
        tx.run("""
          MATCH 
            (i1:Ingredient{name:"Black Sesame Powder"}), 
            (i2:Ingredient{name:"Black Sesame"}) 
          CREATE (i1)-[:SUBSTITUTES]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Breadcrumbs"}),
            (i2:Ingredient{name:"Panko"})
          CREATE (i1)-[:SUBSTITUTES]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Panko"}),
            (i2:Ingredient{name:"Breadcrumbs"})
          CREATE (i1)-[:SUBSTITUTES]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Fruit"}),
            (i2:Ingredient{name:"Produce"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Vegetable"}),
            (i2:Ingredient{name:"Produce"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Root vegetable"}),
            (i2:Ingredient{name:"Vegetable"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Cruciferous vegetable"}),
            (i2:Ingredient{name:"Vegetable"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Leafy green"}),
            (i2:Ingredient{name:"Vegetable"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Yam"}),
            (i2:Ingredient{name:"Root vegetable"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Broccoli"}),
            (i2:Ingredient{name:"Cruciferous vegetable"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Kale"}),
            (i2:Ingredient{name:"Cruciferous vegetable"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Kale"}),
            (i2:Ingredient{name:"Leafy green"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Spinach"}),
            (i2:Ingredient{name:"Leafy green"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Dairy drink"}),
            (i2:Ingredient{name:"Dairy"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Milk"}),
            (i2:Ingredient{name:"Dairy drink"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Oat milk"}),
            (i2:Ingredient{name:"Dairy-free milk"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Soy milk"}),
            (i2:Ingredient{name:"Dairy-free milk"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Rice milk"}),
            (i2:Ingredient{name:"Dairy-free milk"})
          CREATE (i1)-[:IS_A]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Dairy-free milk"}),
            (i2:Ingredient{name:"Milk"})
          CREATE (i1)-[:SUBSTITUTES{general:0.9,baking:0.1}]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Oat milk"}),
            (i2:Ingredient{name:"Milk"})
          CREATE (i1)-[:SUBSTITUTES{baking:0.4}]->(i2)
        """)
        tx.run("""
          MATCH
            (i1:Ingredient{name:"Soy milk"}),
            (i2:Ingredient{name:"Milk"})
          CREATE (i1)-[:SUBSTITUTES{baking:0.7}]->(i2)
        """)
        tx.run("""
          MATCH 
            (p:Person{name:"Alan"}), 
            (i:Ingredient{name:"Dairy"}) 
          CREATE (p)-[:LIKES{score:-1}]->(i)
        """)
        
        tx.run("""
          MATCH 
            (p:Person{name:"Alan"}), 
            (i:Ingredient{name:"Soy milk"}) 
          CREATE (p)-[:LIKES{score:0.7}]->(i)
        """)
        tx.run("""
          MATCH 
            (p:Person{name:"Alan"}), 
            (i:Ingredient{name:"Rice milk"}) 
          CREATE (p)-[:LIKES{score:0.4}]->(i)
        """)
        tx.run("""
          MATCH 
            (p:Person{name:"Alan"}), 
            (r:Recipe{name:"Sesame Chicken"}) 
          CREATE (p)-[:PLANS{date:"Monday", completed:false}]->(r)
        """)

if __name__ == "__main__":
    # FIXME pass those as ENV before checkin
    uri = DB_URI
    user = DB_USER
    password = DB_PASS
    dao = DAO(uri, user, password)

    # FIXME may ONLY need to run this once
    # Reset DB with test data
    dao.init_db()

    # tests

    # user pref page
    # dao.get_all_ingredients()
    dao.get_scored_ingredients("Alan")

    # recipe list page
    # dao.get_all_recipes()
    dao.get_scored_recipes("Alan")

    # set preference score
    dao.set_score("Alan", "Beef", 1)

    # recipe info page
    dao.get_recipe("Sesame Beef")
    dao.find_ingredients_by_recipe("Sesame Beef")
    dao.shopping_by_recipe("Alan", "Sesame Beef")
    dao.get_shopping_list("Alan")

    # food inventory page
    dao.get_inventory("Alan")
    dao.get_substitutes("Sesame")
    # multiple items of same ingredient in the inventory
    dao.add_inventory_item("Alan", {
      "name": "Chicken",
      "quantity":3, 
      "expiration":"2022-05-11", 
      "purchase":"2022-05-03"
    })
    # need item name and purchase date to delete inventory
    # dao.delete_inventory_item("Alan", {"name":"Beef", "purchase":"2022-05-03"})

    # shopping list page
    # dao.get_shopping_list("Alan")
    # dao.delete_shopping_item("Alan", "Beef")

    # get recipes based inventory
    dao.find_ready_recipes_by_person("Alan")
    dao.add_inventory_item("Alan", {
      "name": "Beef",
      "quantity":2, 
      "expiration":"2022-05-11", 
      "purchase":"2022-05-03"
    })
    dao.get_inventory("Alan")
    dao.find_ready_recipes_by_person("Alan")

    # weekly meal plan page
    dao.get_meal_plan("Alan", "Monday")

    dao.close()