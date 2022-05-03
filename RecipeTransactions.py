import os
import Connection

def create_recipe(self, recipe):
    conn = Connection(os.getenv("DB_URI"), os.getenv("DB_USER"), os.getenv("DB_PASS"))
    with conn.driver.session as session:
        res = session.write_transaction(
            self._create_and_return_recipe, recipe)
        for row in res:
            print("Created new recipe: {recipe}".format(recipe=row['recipe']))

# Execpts recipe in JSON form
@staticmethod
def _create_and_return_recipe(tx, recipe):
    query = (
        "CREATE (r1:Recipe { name: $recipe.name })"
    )