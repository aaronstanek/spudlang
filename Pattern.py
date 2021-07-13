# defines patterns which can be checked against for rule application
# SinglePattern checks for a match in either the unit or the name
# returns tuple (0,x) (1,x) (2,x)
# 0 means no match
# 1 means match in unit
# 2 means match in name
# x is index of the match in the sample
# DoublePattern checks for a match in both the unit and name

from FormatCheck import listOfStrings
from Ingredient import Ingredient

class Pattern(object):
    @staticmethod
    def _compare(rule,sample):
        # rule and sample are both lists of strings
        # want to know if sample matches rule
        # for a match, rule must be a subset of sample
        # returns the index of sample where rule begins
        # or returns None if no match
        for sample_index in range(len(sample)-len(rule)+1):
            matches = False
            for rule_index in range(len(rule)):
                if rule[rule_index] != sample[sample_index+rule_index]:
                    matches = False
                    break
            if matches:
                return sample_index
        return None

class SinglePattern(Pattern):
    def __init__(self,rule):
        listOfStrings(rule)
        self.rule = rule
    def matches(self,ig):
        if type(ig) != Ingredient:
            raise TypeError("Expected ig to be of type Ingredient")
        res = self._compare(self.rule,ig.name)
        if res is not None:
            return (2,res)
        res = self._compare(self.rule,ig.unit)
        if res is not None:
            return (1,res)
        else:
            return (0,None)