# defines a RuleOutput class
# and its subclasses
# these perform singular operators on Ingredient objects

from Ingredient import Ingredient
from FormatCheck import listOfStrings

class RuleOutput(object):
    def __init__(self):
        raise Exception("creating an instance of RuleOutput base class is forbidden")

class RenamingRuleOutput(RuleOutput):
    def __init__(self,output_name):
        listOfStrings(output_name)
        self.output_name = output_name
    def apply(self,ig,match_token):
        # match token must come from SinglePattern
        if type(ig) != Ingredient:
            raise TypeError("Expected ig to be an Ingredient")
        if type(match_token) != tuple:
            raise TypeError("Expected tuple")
        if len(match_token) != 2:
            raise ValueError("Expected tuple of length 2")
        if not all(map(lambda x: type(x) == int, match_token)):
            raise TypeError("Expected tuple filled with ints")
        output = ig.duplicate()
        if match_token[0] == 1:
            # editing unit
            output.unit = output.unit[:max(0,match_token[1])] + self.output_name
        else:
            #editing name
            output.name = output.name[:max(0,match_token[1])] + self.output_name
        return output