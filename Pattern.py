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
    @staticmethod
    def _check_props(rule,sample):
        # rule is a dict(str->bool)
        # sample is a set(str)
        # we want to make sure that all the
        # elements marked as True appear in the sample
        # and none of those marked False appear
        # returns True for a match, False otherwise
        for prop in rule:
            if rule[prop]:
                # it must exist in the set to match
                if prop not in sample:
                    return False
            else:
                # it cannot exist in the set to match
                if prop in sample:
                    return False
        return True

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

class DoublePattern(Pattern):
    def __init__(self,rule_unit,rule_name):
        listOfStrings(rule_unit)
        listOfStrings(rule_name)
        self.rule_unit = rule_unit
        self.rule_name = rule_name
    def matches(self,ig):
        if type(ig) != Ingredient:
            raise TypeError("Expected ig to be of type Ingredient")
        res_unit = self._compare(self.rule_unit,ig.unit)
        if res_unit is None:
            return (0,None,None)
        res_name = self._compare(self.rule_name,ig.name)
        if res_name is None:
            return (0,None,None)
        else:
            return (1,res_unit,res_name)