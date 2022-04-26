from enum import Enum

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
        Adds an ingredient to the ingredient list OR updates quantity or ounces of ingredient
        """
        # Create ingredient to sanatize quantity and ounces
        ingredient = Ingredient(name, quantity, metric, modifier)
        if name not in self.ingredient_dict.keys():
            self.ingredient_dict[name] = ingredient

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
            self.appliance_dict[name].subtractQuantity(quantity)
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
            self.tool_dict[key_name].subtractQuantity(quantity)
            if self.tool_dict[key_name].quantity <= 0:
                del self.tool_dict[name]

    def removeIngredient(self, name: str, quantity: int, ounces: int):
        """
        Removes an ingredient from the list OR updates the quantity of ingredients
        """
        # Create ingredient to sanatize quantity and ounces
        ingredient = Ingredient(name, quantity, ounces)
        if name not in self.ingredient_dict.keys():
            raise Exception('Cannot remove Ingredient that does not exist')
        # Ingredients can either have quantity or ounces. This will update quantity or ounces
        elif self.ingredient_dict[name].ounces == 0:
            self.ingredient_dict[name].subtractQuantity(quantity)
            if self.ingredient_dict[name].quantity <= 0:
                del self.ingredient_dict[name]
        else:
            self.ingredient_dict[name].subtractOunces(ounces)
            if self.ingredient_dict[name].ounces <= 0:
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

    def toString(self):
        id = "Ingredient: " + self.name
        return f"{id:<30} Quantity: {self.quantity}" + "\tMetric: " + self.metric + "\tMOD " + self.modifier

    def printItem(self):
        print(self.toString())



# invent = Inventory()
# invent.addAppliance("Oven", 2)
# invent.addAppliance("Microwave", 1)
# invent.addAppliance("Stove", 1)
#
# invent.useAppliance("Oven", 2)
# invent.useAppliance("Stove", 1)
# invent.releaseAppliance("Oven", 1)
#
# invent.addTool("Pan", 1, Size.Small)
# invent.addTool("Saucepan", 1, Size.Medium)
# invent.addTool("Pot", 1, Size.Large)
# invent.addTool("Saucepan", 1, Size.Small)
#
# invent.addIngredient("Dry Spaghetti", 1, 10)
# invent.addIngredient("Tomatoe Sauce", 1, 5)
# invent.addIngredient("Meatballs", 10, 0)
# invent.addIngredient("Kale", 1, 6)
# invent.removeIngredient("Kale", 1, 6)
#invent.printInventory()
