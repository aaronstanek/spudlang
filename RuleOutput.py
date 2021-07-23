# defines a RuleOutput class
# and its subclasses
# these perform singular operators on Ingredient objects

from MyNumber import MyNumber
from Ingredient import Ingredient
from FormatCheck import listOfStrings, setOfStrings, listOfTupleStringBools

class RuleOutput(object):
    def __init__(self):
        raise Exception("creating an instance of RuleOutput base class is forbidden")
    @staticmethod
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

class NoneRuleOutput(RuleOutput):
    def __init__(self):
        pass
    @staticmethod
    def apply(ig,match_token):
        return ig

NoneRuleOutputInstance = NoneRuleOutput()

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

class SingleConvertingRuleOutput(RenamingRuleOutput):
    def __init__(self,ratio,output_name):
        super().__init__(output_name)
        if type(ratio) != MyNumber:
            raise TypeError("Expected MyNumber")
        self.ratio = ratio
    def apply(self,ig,match_token):
        output = super().apply(ig,match_token).duplicate()
        output.count = output.count * self.ratio
        return output

class PropertiesRuleOutput(RuleOutput):
    def __init__(self,base,edits):
        if not isinstance(base,RuleOutput):
            raise TypeError("Expected child class of RuleOutput")
        listOfTupleStringBools(edits)
        self.base = base
        self.edits = edits
    def apply(self,ig,match_token):
        output = self.base.apply(ig,match_token).duplicate()
        for edit in self.edits:
            # edit is (str,bool)
            if edit[1]:
                output.props.add(edit[0])
            else:
                if edit[0] in output.props:
                    output.props.remove(edit[0])
        return output

class DecRuleOutput(RuleOutput):
    def __init__(self):
        pass
    @staticmethod
    def apply(ig,match_token):
        output = ig.duplicate()
        output.count = output.count.as_float()
        return output

DecRuleOutputInstance = DecRuleOutput()

class FracRuleOutput(RuleOutput):
    def __init__(self):
        pass
    @staticmethod
    def apply(ig,match_token):
        output = ig.duplicate()
        output.count = output.count.as_fraction(10)
        return output
    
FracRuleOutputInstance = FracRuleOutput()