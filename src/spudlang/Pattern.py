# defines patterns which can be checked against for rule application
# SinglePattern checks for a match in either the unit or the name
# returns tuple (0,x) (1,x) (2,x)
# 0 means no match
# 1 means match in unit
# 2 means match in name
# x is index of the match in the sample
# DoublePattern checks for a match in both the unit and name

from .FormatCheck import listOfStrings, dictStrBool
from .Ingredient import Ingredient

class Pattern(object):
    def __init__(self):
        raise Exception("creating an instance of Pattern base class is forbidden")
    @staticmethod
    def _compare(rule,sample):
        # rule and sample are both lists of strings
        # want to know if sample matches rule
        # for a match, rule must be a subset of sample
        # returns the index of sample where rule begins
        # or returns None if no match
        for sample_index in range(len(sample)-len(rule)+1):
            matches = True
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
    def __init__(self,rule,props):
        if (rule is None) and (len(props) == 0):
            raise ValueError("must enter at least one criterion")
        if rule is not None:
            listOfStrings(rule)
        dictStrBool(props)
        self.rule = rule
        self.props = props
        self.specificity = len(props)
        if rule is not None:
            self.specificity += len(rule)
    def matches(self,ig):
        if not isinstance(ig,Ingredient):
            raise TypeError("Expected ig to be of type Ingredient")
        if len(self.props) == 0:
            res = self._compare(self.rule,ig.name)
            if res is not None:
                return (2,res)
            res = self._compare(self.rule,ig.unit)
            if res is not None:
                return (1,res)    
        else:
            # we need to check props
            # this means that we can
            # only match against the name
            if self.rule is None:
                res = -1
            else:
                res = self._compare(self.rule,ig.name)
            if res is not None:
                if self._check_props(self.props,ig.props):
                    return (2,res)
        return (0,None)

class DoublePattern(Pattern):
    def __init__(self,rule_unit,rule_name,props):
        # if rule_unit or rule_name are none, we interpret them as wildcards
        if (rule_unit is None) and (rule_name is None) and (len(props) == 0):
            raise ValueError("must enter at least one criterion")
        if rule_unit is not None:
            listOfStrings(rule_unit)
        if rule_name is not None:
            listOfStrings(rule_name)
        dictStrBool(props)
        self.rule_unit = rule_unit
        self.rule_name = rule_name
        self.props = props
        self.specificity = len(props)
        if rule_unit is not None:
            self.specificity += len(rule_unit)
        if rule_name is not None:
            self.specificity += len(rule_name)
    def matches(self,ig):
        if not isinstance(ig,Ingredient):
            raise TypeError("Expected ig to be of type Ingredient")
        if self.rule_unit is None:
            res_unit = -1
        else:
            res_unit = self._compare(self.rule_unit,ig.unit)
            if res_unit is None:
                return (0,None,None)
        if self.rule_name is None:
            res_name = -1
        else:
            res_name = self._compare(self.rule_name,ig.name)
            if res_name is None:
                return (0,None,None)
        if self._check_props(self.props,ig.props):
            return (1,res_unit,res_name)
        else:
            return (0,None,None)