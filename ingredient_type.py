from typing import List, Dict, Tuple

class IngredientType:
    '''
    Base class for a type of ingredient.

    Similarity is a float between 0.00 and 1.00 (no more than 2 decimal places) indicating conservatively
    how alike the most different descendant IngredientTypes are. If there are no children, the value
    should be 1.00. Similarity is used to calculate the substitutability of one IngredientType for another,
    as well as to infer preferences.

    A substitutability value is also a float between 0.00 and 1.00 (no more than 2 decimal places).
    As a unidirectional relation between two IngredientTypes, it represents the appropriateness of
    substituting one ingredient for another ingredient, choosing the combination of least substitutable
    descendant IngredientTypes (if applicable) in order to make this a conservative measure. In simpler terms,
    it answers the following question: "What's the worst that it could work out if I used this
    ingredient/an ingredient in this category when the recipe says to use that ingredient/an ingredient
    in that category?" Substitutability is calculated from similarity scores and parent-child relations
    occasionally supplemented with custom "override" substitutability relations.
    '''

    def __init__(self, id: str, similarity: float, parents: List['IngredientType'],
                 substitutions: Dict[Tuple['IngredientType', str], float] = {}):
        self.id = id
        self.similarity = similarity
        self.parents = parents
        self.substitutions = substitutions

    def __str__(self):
        return self.getId()

    def getId(self):
        return self.id

    def getSimilarity(self):
        return self.similarity

    def getParents(self):
        return self.parents

    def getSubstitutions(self):
        return self.substitutions

    def getAncestors(self) -> List['IngredientType']:
        '''
        Returns a list containing all IngredientTypes that can be reached by recursively following
        the parent relation.
        '''

        parent_list = self.getParents()
        return_list = []

        for parent in parent_list:
            return_list.append(parent)
            return_list += parent.getAncestors()

        return return_list

    # I'm not convinced this algorithm is fully robust for some weird override substitutions
    # (e.g., if you start adding overrides between parents and children), but it should be correct
    # for pretty much any reasonable substitution
    def calcSubstitutability(self, substitutee: 'IngredientType', context: str = None) -> float:
        '''
        Calculates a score from 1.0 (the same ingredient) to 0.0 (not at all substitutable), rounded
        to two decimal places, indicating how well this ingredient substitutes for the substitutee ingredient.
        This may change depending on the context (e.g., baking).

        We assume that similarity scores never increase as you traverse from children to parent IngredientTypes.
        This makes intuitive sense, as similarity scores are meant to decrease as maximum variation among
        ingredients of an IngredientType increases, and children are strictly subsets of their parents.
        '''

        substitutability = self.calcSubstitutabilityHelper(substitutee, context, substitutee.getAncestors())
        return round(substitutability, 2)

    def calcSubstitutabilityHelper(self, substitutee: 'IngredientType', context: str,
                                   substitutee_ancestors: List['IngredientType']) -> float:
        max_sub = 0.0

        # if the substitution is the same as the substitutee, then it is fully substitutable
        if self == substitutee:
            return 1.0

        # check override substitutions
        for (override_sub, override_context) in self.getSubstitutions():
            if override_context == context:
                # if the override substitution refers to the substitutee or one of its ancestors, then just use the override substitutability value
                if override_sub == substitutee or override_sub in substitutee_ancestors:
                    return self.getSubstitutions()[(override_sub, override_context)]
                # if the override substitution refers to a child of the substitutee, then multiply the override substitutability value by the similarity score of the substitutee
                elif substitutee in override_sub.getAncestors():
                    return self.getSubstitutions()[(override_sub, override_context)] * substitutee.getSimilarity()

        # if the substitution is one of the substitutee's ancestors, then its substitutability is
        # the similarity within that category
        if self in substitutee_ancestors:
            return self.getSimilarity()

        # if we haven't made a connection yet, then recurse to the parents of the current substitution
        for parent in self.getParents():
            temp_sub = parent.calcSubstitutabilityHelper(substitutee, context, substitutee_ancestors)
            if temp_sub > max_sub:
                max_sub = temp_sub

        return max_sub

produce = IngredientType("produce", 0, [])
fruit = IngredientType("fruit", 0.2, [produce])
veg = IngredientType("veg", 0.2, [produce])
root = IngredientType("root", 0.7, [veg])
cruciferous = IngredientType("cruciferous", 0.8, [veg])
leafy = IngredientType("leafy", 0.9, [veg])
yam = IngredientType("yam", 1, [root])
rutabaga = IngredientType("rutabaga", 1, [root, cruciferous])
kale = IngredientType("kale", 1, [cruciferous, leafy])
spinach = IngredientType("spinach", 1, [leafy])
citrus = IngredientType("citrus", 0.7, [fruit])
orange = IngredientType("orange", 1, [citrus])
lemon = IngredientType("lemon", 1, [citrus])

assert fruit.calcSubstitutability(veg) == 0, fruit.calcSubstitutability(veg)
assert root.calcSubstitutability(leafy) == 0.2, root.calcSubstitutability(leafy)
assert yam.calcSubstitutability(yam) == 1, yam.calcSubstitutability(yam)
assert yam.calcSubstitutability(root) == 1, yam.calcSubstitutability(root)
assert root.calcSubstitutability(yam) == 0.7, yam.calcSubstitutability(root)
assert yam.calcSubstitutability(rutabaga) == 0.7
assert rutabaga.calcSubstitutability(kale) == 0.8
assert kale.calcSubstitutability(spinach) == 0.9
assert spinach.calcSubstitutability(rutabaga) == 0.2
assert yam.calcSubstitutability(kale) == 0.2
assert orange.calcSubstitutability(lemon) == 0.7
assert orange.calcSubstitutability(kale) == 0

dairy = IngredientType("dairy", 0, [])
dairy_drink = IngredientType("dairy drink", 0.7, [dairy])
milk = IngredientType("milk", 0.95, [dairy_drink])
whole_milk = IngredientType("whole milk", 1, [milk])
yogurt = IngredientType("yogurt", 1, [dairy])
dairy_free_milk = IngredientType("dairy-free milk", 0.9, [], {(milk, None): 0.9, (milk, "baking"): 0.1})
soy_milk = IngredientType("soy milk", 1, [dairy_free_milk], {(milk, "baking"): 0.7})
oat_milk = IngredientType("oat milk", 1, [dairy_free_milk], {(milk, "baking"): 0.4})
rice_milk = IngredientType("rice milk", 1, [dairy_free_milk])
#
assert dairy_free_milk.calcSubstitutability(whole_milk) == 0.9 # FIX milk weight
assert dairy_free_milk.calcSubstitutability(milk) == 0.9
assert dairy_free_milk.calcSubstitutability(dairy_drink) == 0.63, dairy_free_milk.calcSubstitutability(dairy_drink)
assert dairy_free_milk.calcSubstitutability(dairy) == 0
assert soy_milk.calcSubstitutability(whole_milk) == 0.9
assert soy_milk.calcSubstitutability(milk) == 0.9
assert soy_milk.calcSubstitutability(dairy_drink) == 0.63
assert soy_milk.calcSubstitutability(dairy) == 0
assert rice_milk.calcSubstitutability(milk, "baking") == 0.1, rice_milk.calcSubstitutability(milk, "baking")
assert soy_milk.calcSubstitutability(milk, "baking") == 0.7, soy_milk.calcSubstitutability(milk, "baking")
assert oat_milk.calcSubstitutability(milk, "baking") == 0.4
assert rice_milk.calcSubstitutability(whole_milk, "baking") == 0.1, rice_milk.calcSubstitutability(whole_milk, "baking")
assert soy_milk.calcSubstitutability(whole_milk, "baking") == 0.7, soy_milk.calcSubstitutability(whole_milk, "baking")
assert oat_milk.calcSubstitutability(whole_milk, "baking") == 0.4
assert rice_milk.calcSubstitutability(dairy_drink, "baking") == 0.07
assert soy_milk.calcSubstitutability(dairy_drink, "baking") == 0.49
assert oat_milk.calcSubstitutability(dairy_drink, "baking") == 0.28
assert rice_milk.calcSubstitutability(yogurt) == 0
