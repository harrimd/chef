from typing import List, Dict, Tuple

class IngredientType:
    '''
    Base class for a type of ingredient.
    '''

    def __init__(self, id: int, similarity: float, parents: List['IngredientType'],
                 substitutions: Dict[Tuple['IngredientType', str], float] = {}):
        self.id = id
        self.similarity = similarity
        self.parents = parents
        self.substitutions = substitutions

    def getId(self):
        return self.id

    def getSimilarity(self):
        return self.similarity

    def getParents(self):
        return self.parents

    def getSubstitutions(self):
        return self.substitutions

    def getSelfAndAncestors(self) -> List['IngredientType']:
        '''
        Returns a list containing this IngredientType and all IngredientTypes that can be reached by
        recursively following the parent relation.
        '''

        parent_list = self.getParents()
        return_list = []

        for parent in parent_list:
            return_list += parent.getSelfAndAncestors()

        return_list.append(self)

        return return_list

    def calcSubstitutability(self, sub_for: 'IngredientType', context: str = None) -> int:
        '''
        Calculates a score from 1.0 (the same ingredient) to 0.0 (not at all substitutable) indicating
        how well this ingredient substitutes for the sub_for ingredient. This may change depending on
        the context (e.g., baking).
        '''

        return self.calcSubstitutabilityHelper(sub_for, context, sub_for.getSelfAndAncestors())

    def calcSubstitutabilityHelper(self, sub_for: 'IngredientType', context: str,
                                   sub_for_self_and_ancestors: List['IngredientType']) -> int:
        max_sub = 0

        if self in sub_for_self_and_ancestors:
            return self.similarity

        for (override_sub, override_context) in self.substitutions:
            if override_context == context:
                if override_sub == sub_for:
                    return self.similarity * self.substitutions[(override_sub, override_context)] * sub_for.similarity
                if override_sub in sub_for_self_and_ancestors: # should these be handled differently?
                    return self.similarity * self.substitutions[(override_sub, override_context)] * override_sub.calcSustitutabilityHelper(sub_for, context, sub_for_self_and_ancestors)
        # missing case for if the override is to a child of sub_for?

        for parent in self.parents:
            temp_sub = parent.calcSubstitutabilityHelper(sub_for, context, sub_for_self_and_ancestors)
            if temp_sub > max_sub:
                max_sub = temp_sub

        return max_sub


produce = IngredientType(0, 0, [])
fruit = IngredientType(1, 0.2, [produce])
veg = IngredientType(2, 0.2, [produce])
root = IngredientType(3, 0.7, [veg])
cruciferous = IngredientType(4, 0.8, [veg])
leafy = IngredientType(5, 0.9, [veg])
yam = IngredientType(6, 1, [root])
rutabaga = IngredientType(7, 1, [root, cruciferous])
kale = IngredientType(8, 1, [cruciferous, leafy])
spinach = IngredientType(9, 1, [leafy])
citrus = IngredientType(10, 0.7, [fruit])
orange = IngredientType(11, 1, [citrus])
lemon = IngredientType(12, 1, [citrus])

assert fruit.calcSubstitutability(veg) == 0, fruit.calcSubstitutability(veg)
assert root.calcSubstitutability(leafy) == 0.2, root.calcSubstitutability(leafy)
assert yam.calcSubstitutability(yam) == 1, yam.calcSubstitutability(yam)
assert yam.calcSubstitutability(root) == 0.7, yam.calcSubstitutability(root)
assert yam.calcSubstitutability(rutabaga) == 0.7
assert rutabaga.calcSubstitutability(kale) == 0.8
assert kale.calcSubstitutability(spinach) == 0.9
assert spinach.calcSubstitutability(rutabaga) == 0.2
assert yam.calcSubstitutability(kale) == 0.2
assert orange.calcSubstitutability(lemon) == 0.7
assert orange.calcSubstitutability(kale) == 0

dairy = IngredientType(100, 0, [])
dairy_drink = IngredientType(101, 0.7, [dairy])
milk = IngredientType(102, 1, [dairy_drink])
yogurt = IngredientType(103, 1, [dairy])
dairy_free_milk = IngredientType(104, 0.9, [], {(milk, None): 0.9, (milk, "baking"): 0.1})
soy_milk = IngredientType(106, 1, [dairy_free_milk], {(milk, "baking"): 0.7})
oat_milk = IngredientType(105, 1, [dairy_free_milk], {(milk, "baking"): 0.4})
rice_milk = IngredientType(107, 1, [dairy_free_milk])

assert dairy_free_milk.calcSubstitutability(milk) == 0.81
# assert dairy_free_milk.calcSubstitutability(dairy_drink) == 0.567, dairy_free_milk.calcSubstitutability(dairy_drink)
# assert dairy_free_milk.calcSubstitutability(dairy) == 0
assert soy_milk.calcSubstitutability(milk) == 0.81
# assert soy_milk.calcSubstitutability(dairy_drink) == 0.567
# assert soy_milk.calcSubstitutability(dairy) == 0
# add cases for non-baking context
# assert rice_milk.calcSubstitutability(milk, "baking") == 0.09, rice_milk.calcSubstitutability(milk)
# assert soy_milk.calcSubstitutability(milk, "baking") == 0.63
# assert oat_milk.calcSubstitutability(milk, "baking") == 0.36
# assert rice_milk.calcSubstitutability(dairy_drink, "baking") == 0.063
# assert soy_milk.calcSubstitutability(dairy_drink, "baking") == 0.441
# assert oat_milk.calcSubstitutability(dairy_drink, "baking") == 0.252
assert rice_milk.calcSubstitutability(yogurt) == 0
