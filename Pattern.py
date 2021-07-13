# defines patterns which can be checked against for rule application
# SinglePattern checks for a match in either the unit or the name
# DoublePattern checks for a match in both the unit and name

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