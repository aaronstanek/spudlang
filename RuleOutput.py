# defines a RuleOutput class
# and its subclasses
# these perform singular operators on Ingredient objects

from Ingredient import Ingredient
from FormatCheck import listOfStrings
from copy import deepcopy

class RuleOutput(object):
    def __init__(self):
        raise Exception("creating an instance of RuleOutput base class is forbidden")

class RenamingRuleOutput(RuleOutput):
    def __init__(self,output_name):
        listOfStrings(output_name)
        self.output_name = output_name
    def apply(self,ig,on_units):
        if type(ig) != Ingredient:
            raise TypeError("Expected ig to be an Ingredient")
        output = deepcopy(ig)
        if on_units:
            output.units = deepcopy(self.output_name)
        else:
            output.name = deepcopy(self.output_name)
        return output