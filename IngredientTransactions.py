import os
import logging
import Connection
from neo4j.exceptions import ServiceUnavailable

def create_ingredientCategory(category_name):
    conn = Connection(os.getenv("DB_URI"), os.getenv("DB_USER"), os.getenv("DB_PASS"))
    with conn.driver.session as session:
        res = session.write_transaction(
            _create_and_return_ingredientCategory, category_name)
        for row in res:
            print("Created ingredient category: {ic}".format(ic=row['ic']))
            
def _create_and_return_ingredientCategory(tx, cn):
    query = (
        "CREATE (c1:IngredientCategory { id: $cn })"
        "RETURN c1"
    )
    result = tx.run(query, cn)
    try:
        return [{"c1": row["c1"]["id"]}
                for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise