# defines a RuleOutput class
# and its subclasses
# these perform singular operators on Ingredient objects

from Ingredient import Ingredient
from FormatCheck import listOfStrings

class RuleOutput(object):
    def __init__(self):
        raise Exception("creating an instance of RuleOutput base class is forbidden")
    def check_conformity(ig,match_token,match_token_length):
        # check that an input to apply makes sense
        if type(ig) != Ingredient:
            raise TypeError("Expected ig to be an Ingredient")
        if type(match_token) != tuple:
            raise TypeError("Expected tuple")
        if type(match_token_length) != int:
            raise TypeError("Expected int")
        if len(match_token) != match_token_length:
            raise ValueError("Expected tuple of length "+str(match_token_length))
        if not all(map(lambda x: type(x) == int, match_token)):
            raise TypeError("Expected tuple filled with ints")

class RenamingRuleOutput(RuleOutput):
    def __init__(self,output_name):
        listOfStrings(output_name)
        self.output_name = output_name
    def apply(self,ig,match_token):
        # match token must come from SinglePattern
        self.check_conformity(ig,match_token,2)
        output = ig.duplicate()
        if match_token[0] == 1:
            # editing unit
            output.unit = output.unit[:max(0,match_token[1])] + self.output_name
        else:
            #editing name
            output.name = output.name[:max(0,match_token[1])] + self.output_name
        return output

class PrefixingRuleOutput(RuleOutput):
    def __init__(self,prefix):
        listOfStrings(prefix)
        self.prefix = prefix
    def apply(self,ig,match_token):
        # match token must come from SinglePattern
        self.check_conformity(ig,match_token,2)
        if match_token[1] != 0:
            # if the input already has a prefix,
            # we shouldn't change it
            return ig
        output = ig.duplicate()
        if match_token[0] == 1:
            # editing unit
            # we know that match_token[1] == 0
            output.unit = self.prefix + output.unit
        else:
            # editing name
            output.name = self.prefix + output.name
        return output