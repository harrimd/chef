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
        self.recipe_dict = {}

    def addRecipe(self, recipe):
        if recipe.name in self.recipe_dict.keys():
            raise Exception("Recipe exists in Recipebook")
        else:
            self.recipe_dict[recipe.name] = recipe

    def removeRecipe(self, name):
        if name not in self.recipe_dict.keys():
            raise Exception("Recipe does not exist in Recipebook")
        else:
            del self.recipe_dict[name]

    def getRecipe(self, name):
        for key in self.recipe_dict.keys():
            if key == name:
                return self.recipe_dict[key]
        return None

    def recommendRecipes(self, current_inventory):
        """
        Returns a list of recommended recipes for the user's inventory
        @WENTAO Populate this function with prefered recommending system
        """
        recommends = []
        availablity_scores = self.getAvailablityScores(current_inventory)
        for recipe_name in availablity_scores.keys():
            if availablity_scores[recipe_name] == 1.0:
                recommends.append(self.getRecipe(recipe_name))
        return recommends

    def getAvailablityScores(self, current_invent):
        """
        Returns lists of all recipes that a user can make with there given inventory
        """
        availablity_scores = {}
        for key in self.recipe_dict.keys():
            required_invent = self.recipe_dict[key].inventory
            has_recipe = current_invent.hasRequiredInventory(required_invent)
            if has_recipe:
                availablity_scores[key] = 1.0
            else:
                invent_score = current_invent.requiredInventoryScore(required_invent)
                availablity_scores[key] = invent_score
        return availablity_scores

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

    def __init__(self, name: str, instructions, inventory, id):
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

class RecipeID(object):
    '''
    Base class for an Recipe Identification
    '''
    def __init__(self, classification: str, category: str, origin, url: str):
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
        self.url = url

    def toString(self):
        id_string = ""
        if self.classification != None:
            id_string += "Classification: " + self.classification + "\n"
        if self.category != None:
            id_string += "Category: " + self.category + "\n"
        if self.origin != None:
            id_string += "Origin: " + self.origin + "\n"
        if self.url != None:
            id_string += "URL: " + self.url + "\n"
        return id_string
