from enum import Enum
import conversions

class Inventory:
    '''
    Base class for a users inventory.
    '''

    def __init__(self):
        """
        Initializes 3 dictionaries {appliance, tool, ingredient}
        """
        self.appliance_dict = {}
        self.tool_dict = {}
        self.ingredient_dict = {}

    def addAppliance(self, name: str, quantity: int):
        """
        Adds an appliance to the appliance list OR updates quantity of appliances
        """
        if name not in self.appliance_dict.keys():
            self.appliance_dict[name] = Appliance(name, quantity)
        else:
            self.appliance_dict[name].addQuantity(quantity)

    def addTool(self, name: str, quantity: int, size: int):
        """
        Adds a tool to the tool list OR updates quantity of tools
        """
        # key_name is used to seperate sizes of tools in the dictionary
        key_name = size.name + " " + name
        if key_name not in self.tool_dict.keys():
            self.tool_dict[key_name] = Tool(name, quantity, size)
        else:
            self.tool_dict[key_name].addQuantity(quantity)

    def addIngredient(self, name: str, quantity: int, metric: str, modifier: str):
        """
        Adds an ingredient to the ingredient list OR updates quantity or metric of ingredient
        """
        # Create ingredient to sanatize quantity and metric
        ingredient = Ingredient(name, quantity, metric, modifier)
        if name not in self.ingredient_dict.keys():
            self.ingredient_dict[name] = ingredient
        elif self.ingredient_dict[name].metric == metric:
            self.ingredient_dict[name].addQuantity(quantity)
        else:
            converted_quantity = conversions.convertNum(quantity, metric, self.metric)
            self.ingredient_dict[name].addQuantity(converted_quantity)

    def hasAppliance(self, name: str):
        """
        Determines if Appliance is in inventory
        """
        return name in self.appliance_dict.keys()

    def hasTool(self, name: str):
        """
        Determines if Appliance is in inventory
        """
        return name in self.tool_dict.keys()

    def hasIngredient(self, name: str):
        """
        Determines if Appliance is in inventory
        """
        return name in self.ingredient_dict.keys()

    def removeAppliance(self, name: str, quantity: int):
        """
        Removes an appliance from the list OR updates the quantity of appliances
        """
        # key_name is used to seperate sizes of tools in the dictionary
        if name not in self.appliance_dict.keys():
            raise Exception('Cannot remove Appliance that does not exist')
        else:
            self.appliance_dict[name].removeQuantity(quantity)
            if self.appliance_dict[name].quantity <= 0:
                del self.appliance_dict[name]

    def removeTool(self, name: str, quantity: int, size: int):
        """
        Removes a tool from the tool list OR updates quantity of tools
        """
        key_name = size.name + " " + name
        if key_name not in self.tool_dict.keys():
            raise Exception('Cannot remove Tool that does not exist')
        else:
            self.tool_dict[key_name].removeQuantity(quantity)
            if self.tool_dict[key_name].quantity <= 0:
                del self.tool_dict[name]

    def removeIngredient(self, name: str, quantity: int, metric: str):
        """
        Removes an ingredient from the list OR updates the quantity of ingredients
        """
        # Create ingredient to sanatize quantity and metric
        if name not in self.ingredient_dict.keys():
            raise Exception('Cannot remove Ingredient that does not exist')
        elif self.ingredient_dict[name].metric == metric:
            self.ingredient_dict[name].removeQuantity(quantity)
            if self.ingredient_dict[name].quantity <= 0:
                del self.ingredient_dict[name]
        else:
            converted_quantity = conversions.convertNum(quantity, metric, self.metric)
            self.ingredient_dict[name].removeQuantity(converted_quantity)
            if self.ingredient_dict[name].quantity  <= 0:
                del self.ingredient_dict[name]

    def useAppliance(self, name: str, in_use_status: int):
        """
        Marks a number of appliances as in use
        """
        if name not in self.appliance_dict.keys():
            raise Exception('Cannot use Appliance that does not exist')
        else:
            add_status = self.appliance_dict[name].status + in_use_status
            self.appliance_dict[name].changeInUseStatus(add_status)

    def releaseAppliance(self, name: str, in_use_status: int):
        """
        Releases a number of appliances from being in use
        """
        if name not in self.appliance_dict.keys():
            raise Exception('Cannot release Appliance that does not exist')
        else:
            sub_status = self.appliance_dict[name].status - in_use_status
            self.appliance_dict[name].changeInUseStatus(sub_status)

    def hasRequiredInventory(self, inventory_query):
        """
        Sees if the inventory query is in current inventory
        Just currently deals with ingredients
        """
        for key in inventory_query.ingredient_dict.keys():
            if key in self.ingredient_dict.keys():
                quantity = inventory_query.ingredient_dict[key].quantity
                metric = inventory_query.ingredient_dict[key].metric
                if not self.ingredient_dict[key].enoughForRecipe(quantity, metric):
                    return False
            else:
                return False
        return True

    def requiredInventoryScore(self, inventory_query):
        """
        Gives percentage of ingredients available for Inventory
        """
        available = 0
        total = 0
        for key in inventory_query.ingredient_dict.keys():
            if key in self.ingredient_dict.keys():
                quantity = inventory_query.ingredient_dict[key].quantity
                metric = inventory_query.ingredient_dict[key].metric
                if self.ingredient_dict[key].enoughForRecipe(quantity, metric):
                    available += 1
            total += 1
        return available/total


    def claimInventory(self, inventory_claim):
        """
        Claims inventory for a recipe as requested.
        """
        if self.hasRequiredInventory(inventory_claim) == False:
            return False
        for key in inventory_claim.ingredient_dict.keys():
            quantity = inventory_claim.ingredient_dict[key].quantity
            metric = inventory_claim.ingredient_dict[key].metric
            self.ingredient_dict[key].claimItem(quantity, metric)
        return True

    def unClaimInventory(self, inventory_claim):
        """
        Unclaims inventory for a unused recipe.
        """
        for key in inventory_claim.ingredient_dict.keys():
            quantity = inventory_claim.ingredient_dict[key].quantity
            metric = inventory_claim.ingredient_dict[key].metric
            self.ingredient_dict[key].unClaimItem(quantity, metric)

    def loadInventory(self, filename):
        """
        Loads an Invetory from a file
        """
        print("TODO")

    def saveInventory(self, filename):
        """
        Saves an Inventory to a file
        """
        print("TODO")

    def toString(self):
        """
        Converts the inventory into a string: {Appliances, Tools, Ingredients}
        """
        invent_string = "######## Appliance List ########\n"
        for appliance in sorted(self.appliance_dict.keys()):
            invent_string += self.appliance_dict[appliance].toString() + "\n"
        invent_string += "######## Tool List ########\n"
        for tool in sorted(self.tool_dict.keys()):
            invent_string += self.tool_dict[tool].toString() + "\n"
        invent_string += "######## Ingredient List ########\n"
        for ingredient in sorted(self.ingredient_dict.keys()):
            invent_string += self.ingredient_dict[ingredient].toString() + "\n"
        return invent_string

    def printInventory(self):
        """
        Prints the current inventory: {Appliances, Tools, Ingredients}
        """
        print(self.toString())


class Item(object):
    '''
    Base class for a inventory item.
    '''
    def __init__(self, name: str, quantity: int):
        """
        Initializes a Item object
        Args:
            Name (String): Name of the Item
            Quantity (int): Quantity of an Item
        """
        if quantity < 0:
            raise Exception('Quantity is negative value')
        self.name = name
        self.quantity = quantity

    def updateName(self, name):
        self.name = name

    def updateQuantity(self, quantity):
        self.quantity = quantity

    def addQuantity(self, quantity):
        self.quantity += quantity

    def removeQuantity(self, quantity):
        self.quantity -= quantity

    def toString(self):
        id = "Item: " + self.name
        return f"{id:<30} Quantity: {self.quantity}"

    def printItem(self):
        print(self.toString())

class Appliance(Item):
    '''
    Appliance is a inventory item.
    '''
    def __init__(self, name: str, quantity: int):
        """
        Initializes a Appliance object
        Args:
            Name (String): Name of the Item
            Quantity (int): Quantity of an Item
        """
        super().__init__(name, quantity)
        self.status = 0

    def changeInUseStatus(self, in_use_no: int):
        """
        Changes the number of this Item In Use
        """
        if in_use_no > self.quantity:
            raise Exception("No more of this Appliance available")
        if in_use_no < 0:
            self.status = 0
        else:
            self.status = in_use_no

    def getStatus(self):
        """
        Gets the current status
        """
        if(self.status > 0):
            if(self.quantity > 1):
                return str(self.status) + "/" + str(self.quantity) + " In Use"
            else:
                return "In Use"
        else:
            return "Not In Use"

    def toString(self):
        id = "Appliance: " + self.name
        return f"{id:<30} Quantity: {self.quantity}" + "\t" + self.getStatus()

    def printItem(self):
        print(self.toString())

class Size(Enum):
    '''
    Size of the tools.
    '''
    Small = 1
    Medium = 2
    Large = 3

class Tool(Item):
    '''
    Tool is a inventory item.
    '''
    def __init__(self, name: str, quantity: int, size: int):
        """
        Initializes a Appliance object
        Args:
            Name (String): Name of the Item
            Quantity (int): Quantity of an Item
            Size (Enum-int): Size of the Item
        """
        super().__init__(name, quantity)
        self.size = size

    def changeSize(self, size):
        self.size = size

    def toString(self):
        id = "Tool: " + "(" + self.size.name + ") " + self.name
        return f"{id:<30} Quantity: {self.quantity}"

    def printItem(self):
        print(self.toString())

class Metric(Enum):
    '''
    Size of the tools.
    '''
    ounce = 1
    cup = 2
    tbsp = 3
    tsp = 4
    inch = 5


class Ingredient(Item):
    '''
    Ingredient is a inventory item.
    '''
    def __init__(self, name: str, quantity: int, metric: str, modifier:str):
        """
        Initializes a Appliance object
        Args:
            Name (String): Name of the Item
            Quantity (int): Quantity of an Item
            Metric (String): Metric type
            Modifier (String): A modifier to ingredient
        """

        super().__init__(name, quantity)
        self.metric = metric
        self.modifier = modifier

    def updateMetric(self, metric: int):
        self.metric = metric

    def updateModifier(self, modifier: int):
        self.modifier = modifier

    def enoughForRecipe(self, quantity: int, metric: str):
        if self.metric == metric and self.quantity >= quantity:
            return True
        converted_quantity = conversions.convertNum(quantity, metric, self.metric)
        if self.quantity >= converted_quantity:
            return True
        return False

    def claimItem(self, quantity: int, metric: str):
        if self.metric == metric:
            self.removeQuantity(quantity)
        else:
            converted_quantity = conversions.convertNum(quantity, metric, self.metric)
            self.removeQuantity(converted_quantity)

    def unClaimItem(self, quantity: int, metric: str):
        if self.metric == metric:
            self.addQuantity(quantity)
        else:
            converted_quantity = conversions.convertNum(quantity, metric, self.metric)
            self.addQuantity(converted_quantity)

    def toString(self):
        id = "Ingredient: " + self.name
        if self.modifier != None:
            id += " " + self.modifier
        return f"{id:<40} Quantity: {self.quantity}" + "\tMetric: " + self.metric

    def printItem(self):
        print(self.toString())
