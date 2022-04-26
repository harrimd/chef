import inventory
from inventory import Size
from enum import Enum
import json

class RecipeBook:
    '''
    Base class for a RecipeBook.
    '''

    def __init__(self):
        """
        Initializes a recipe dictionary
        """
        self.recipes_dict = {}

    def addRecipe(self, recipe):
        if recipe.name in recipes_dict:
            raise Exception("Recipe exists in Recipebook")
        else:
            self.recipes_dict[recipe.name] = recipe

    def removeRecipe(self, name):
        if name not in recipes_dict:
            raise Exception("Recipe does not exist in Recipebook")
        else:
            del self.recipes_dict[name]

    def loadRecipeBook(self, filename):
        """
        Loads a recipebook from a file
        """
        print("TODO")

    def saveRecipeBook(self, filename):
        """
        Saves a recipebook to a file
        """
        print("TODO")

class Recipe(object):
    '''
    Base class for a Recipe.
    '''

    def __init__(self, name: str, instructions, inventory, id, url):
        """
        Initializes a recipe
        Args:
            Name (String): Name of the Recipe
            Instructions (InstructionSet): Instructions for a recipe
            Inventory (Inventory): Required inventory for a recipe
            ID (Recipe_ID): The identification for a recipe
            URL (String): The original recipe URL
        """
        self.name = name
        self.instructions = instructions
        self.inventory = inventory
        self.id = id
        self.url = url

    def updateName(self, name):
        self.name = name

    def updateInstructions(self, instructions):
        self.instructions = instructions

    def updateInventory(self, inventory):
        self.inventory = inventory

    def updateID(self, id):
        self.id = id

    def updateURL(self, url):
        self.url = url

    def toString(self):
        recipe_string = "Recipe: " + self.name + "\n"
        recipe_string += self.id.toString() + "\n"
        recipe_string += self.inventory.toString() + "\n"
        recipe_string += self.instructions.toString() + "\n"
        return recipe_string

    def printRecipe(self):
        print(self.toString())

class InstructionSet(object):
    '''
    Base class for an InstructionSet
    '''
    def __init__(self, cooktime: int, yields: int, preplist, steplist):
        """
        Initializes an InstructionSet
        Args:
            Cooktime (TODO:int?): The cooktime of the InstructionSet
            Preplist (List: Str): List of Prep Steps
            StepList (List: Str): List of Instruction Steps
        """
        self.cooktime = cooktime
        self.yields = yields
        self.preplist = preplist
        self.steplist = steplist

    def updateCooktime(self, cooktime):
        self.cooktime = cooktime

    def updateYields(self, yields):
        self.yields = yields

    def updatePreplist(self, preplist):
        self.preplist = preplist

    def updateSteplist(self, steplist):
        self.steplist = steplist

    def toString(self):
        instr_string = "Cooktime " + str(self.cooktime) + "\n"
        instr_string += "Yields " + str(self.yields) + "\n"
        if self.preplist != None:
            instr_string += "Prep: \n"
            count = 1
            for prepstep in self.preplist:
                instr_string += "\t" + str(count) + ") \t" + prepstep + "\n"
                count += 1
        instr_string += "Directions: \n"
        count = 1
        for step in self.steplist:
            instr_string += "\t" + str(count) + ") \t" + step + "\n"
            count += 1
        return instr_string

class Recipe_ID(object):
    '''
    Base class for an Recipe Identification
    '''
    def __init__(self, classification: str, category: str, origin):
        """
        Initializes a Recipe_ID
        Args:
            Classification (String?): The Class of the Recipe
            Category (String?): The Category of Recipe
            Origin (String?): The Origin of the Recipe
        """
        self.classification = classification
        self.category = category
        self.origin = origin

    def toString(self):
        id_string = ""
        if self.classification != None:
            id_string += "Classification: " + self.classification + "\n"
        if self.category != None:
            id_string += "Category: " + self.category + "\n"
        if self.origin != None:
            id_string += "Origin: " + self.origin + "\n"
        return id_string


# invent = inventory.Inventory()
# invent.addAppliance("Stove", 1)
# invent.addTool("Pot", 1, Size.Medium)
# invent.addTool("Saucepan", 1, Size.Medium)
# invent.addIngredient("Dry Spaghetti", 1, 10)
# invent.addIngredient("Tomatoe Sauce", 1, 5)
# invent.addIngredient("Meatballs", 10, 0)
#
# instr_set = InstructionSet(0, [], [])
# instr_set.updateCooktime(30)
# instr_set.updatePreplist(["Boil salted water in a Pot on the Stove"])
# instr_set.updateSteplist(["Heat sauce and meatballs in a Pan", "Put pasta in boiling water", "After 8 mins of cooking, add the strained pasta to the heated sauce and meatballs"])
#
# recipe = Recipe("Spaghetti and Meatballs",
#                 instr_set,
#                 invent,
#                 Recipe_ID("Pasta Dish", "Entree", "Italian"))
#print(recipe.toString())
