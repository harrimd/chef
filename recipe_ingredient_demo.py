import inventory
from inventory import Size
import conversions
from recipe_book import *
from enum import Enum
import json

def main():
    """
    This block shows how to add items to the current inventory
    """
    current_inventory = inventory.Inventory()
    # You can add appliances {Name, Quantity}
    current_inventory.addAppliance("Oven", 2)
    current_inventory.addAppliance("Microwave", 1)
    current_inventory.addAppliance("Stove", 1)

    # You can add tools {Name, Quantity, Size}
    current_inventory.addTool("Pan", 1, Size.Small)
    current_inventory.addTool("Saucepan", 1, Size.Medium)
    current_inventory.addTool("Pot", 1, Size.Large)
    current_inventory.addTool("Saucepan", 1, Size.Small)

    # You can add ingredients {Name, Quantity, Metric_Type}
    # See conversions for list of supported types
    current_inventory.addIngredient("Dry Spaghetti", 20, 'ounces', "")
    current_inventory.addIngredient("Tomatoe Sauce", 1, 'liters', "")
    current_inventory.addIngredient("Meatballs", 10, '', "")
    current_inventory.addIngredient("Kale", 1, 'ounces', "")
    current_inventory.addIngredient("Parmesan Cheese", 10, 'ounces', "")

    # You can also remove ingredients
    current_inventory.removeIngredient("Kale", 1, 'ounces')

    # And print the inventory to terminal for debugging
    current_inventory.printInventory()

    # You can use and release appliances
    current_inventory.useAppliance("Oven", 2)
    current_inventory.useAppliance("Stove", 1)
    current_inventory.releaseAppliance("Oven", 1)

    # Check out this recipe function to see how a recipe is created
    recipe = getSampleRecipe()

    # You can also see if your inventory has the required items for a recipe
    print("Can I make Spagetti and Meatballs? ", current_inventory.hasRequiredInventory(recipe.inventory))

    # This is how recipes can be added to a recipe book
    recipe_book = RecipeBook()
    recipe_book.addRecipe(recipe)

    # A list of make-able recipes is returned with this function
    available_list = recipe_book.getAvailablityScores(current_inventory)
    print(available_list)
    # A list of reccommended recipes is returned with this function
    recommended_list = recipe_book.recommendRecipes(current_inventory)

    for recipe in recommended_list:
        print(recipe.name, "\n")
        # Claims items in inventory for a recipe
        current_inventory.claimInventory(recipe.inventory)
        current_inventory.printInventory()
        # Unclaims items in inventory for a recipe
        current_inventory.unClaimInventory(recipe.inventory)

    # We can save the recipes here
    recipe_book.saveRecipeBook('sampleRecipe.json')

    new_recipe_book = RecipeBook()
    # We can load the recipes here
    new_recipe_book.loadRecipeBook('sampleRecipe.json')
    for recipe_name in new_recipe_book.recipe_dict.keys():
        new_recipe_book.recipe_dict[recipe_name].printRecipe()

def getSampleRecipe():
    """
    This function creates a sample recipe
    """
    name = "Spaghetti and Meatballs"

    # Here is the intruction set for the recipe, each value can be updated or set in the initialization
    instr_set = InstructionSet(0, 0, [], [])
    instr_set.updateCooktime(30)
    instr_set.updateYields(4)
    instr_set.updatePreplist(["Boil salted water in a Pot on the Stove"])
    instr_set.updateSteplist(["Heat sauce and meatballs in a Pan", "Put pasta in boiling water", "After 8 mins of cooking, add the strained pasta to the heated sauce and meatballs"])

    # Each recipe has its own inventory, this makes seeing if the owner_inventory contains the ingredients easier
    invent = inventory.Inventory()
    invent.addAppliance("Stove", 1)
    invent.addTool("Pot", 1, Size.Medium)
    invent.addTool("Saucepan", 1, Size.Medium)
    invent.addIngredient("Dry Spaghetti", 10, 'ounces', "")
    invent.addIngredient("Tomatoe Sauce", 1, 'cups', "")
    invent.addIngredient("Meatballs", 10, '', "")

    id = RecipeID("Pasta Dish", "Entree", "Italian", None)

    return Recipe(name, instr_set, invent, id)


if __name__ == "__main__":
    main()
