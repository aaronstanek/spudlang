# defines the Rule class
# a container for Patterns and RuleOutputs

from RuleOutput import RuleOutput
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
        return self.outputs.priority()