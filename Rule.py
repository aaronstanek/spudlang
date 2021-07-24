# defines the Rule class
# a container for Patterns and RuleOutputs
# defines the HoldRule class
# to allow for a Rule which does nothing
# except to signal the end of evaluation

from RuleOutput import RuleOutput, NoneRuleOutputInstance
from Pattern import Pattern

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