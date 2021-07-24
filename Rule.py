# defines the Rule class
# a container for Patterns and RuleOutputs
# defines the HoldRule class
# to allow for a Rule which does nothing
# except to signal the end of evaluation
# defines RuleBox to contain instances
# of Rule

from Ingredient import Ingredient
from RuleOutput import RuleOutput, NoneRuleOutputInstance
from Pattern import Pattern

from copy import copy

class Rule(object):
    def __init__(self,pattern,outputs):
        if not isinstance(pattern,Pattern):
            raise TypeError("Expected Pattern")
        if type(outputs) != list:
            raise TypeError("Expected list")
        if len(outputs) == 0:
            raise ValueError("Expected Nonempty list")
        if not all(map(lambda x: isinstance(x,RuleOutput),outputs)):
            raise TypeError("Expected list of RuleOutput")
        self.pattern = pattern
        self.outputs = outputs
    def matches(self,ig):
        # returns match_token
        return self.pattern.matches(ig)
    def specificity(self):
        return self.pattern.specificity
    def apply(self,ig,match_token):
        # match_token is that which was returned from
        # self.matches
        return list(map(lambda x: x.apply(ig,match_token),self.outputs))
    def priority(self):
        # self.outputs has nonzero length
        return self.outputs[0].priority()

class HoldRule(Rule):
    def __init__(self,pattern,priority):
        super().__init__(pattern,[NoneRuleOutputInstance])
        if type(priority) != int:
            raise TypeError("Expected int")
        self._priority = priority
    def priority(self):
        return self._priority

class RuleBox(object):
    def __init__(self):
        self.rules = []
    def add(self,rule):
        if not isinstance(rule,Rule):
            raise TypeError("Expected Rule")
        self.rules.append(rule)
    def _search(self,ig,mask):
        # if is Ingredient
        # mask is a set of ints
        # the indicies of which will be ignored
        best = None
        best_index = None
        best_match_token = None
        for i in range(len(self.rules)):
            if i in mask:
                continue
            rule = self.rules[i]
            if best is not None:
                if rule.priority() > best.priority():
                    continue
                elif rule.priority() == best.priority():
                    if rule.specificity() <= best.specificity():
                        continue
            # we are good to test
            match_token = rule.matches(ig)
            if (match_token[0] != 0):
                best = rule
                best_match_token = match_token
        return best, best_index, best_match_token
    def resolve(self,output_array,ig,mask=set()):
        if type(output_array) != list:
            raise TypeError("Expected list")
        if not isinstance(ig,Ingredient):
            raise TypeError("Expected Ingredient")
        while True:
            rule, index, match_token = self._search(ig,mask)
            if rule is None:
                # we are done
                return
            elif isinstance(rule,HoldRule):
                # we are done
                return
            results = rule.apply(ig,match_token)
            mask.add(index)
            if len(results) == 1:
                ig = results[0]
            else:
                for result in results:
                    self.resolve(output_array,result,mask=copy(mask))
                    return