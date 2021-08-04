# second attempt at writing a parser

from Lex2 import StandardLineLexer, AtCommandLexer
import Pattern
import RuleOutput
import Rule

def resolve_begin_end(lines):
    # lines is a list of lex result objects
    # we will resolve all of the begin/end segments
    # so far only @begin multiply is allowed
    # we we can just assume that
    factors = []
    for line in lines:
        if isinstance(line,StandardLineLexer):
            for factor_num in range(len(factors)-1,-1,-1):
                line.multiply(factors[factor_num])
        elif isinstance(line,AtCommandLexer):
            if line.verb == ["@begin","multiply"]:
                factors.append(line.left.number)
            elif line.verb == ["@end"]:
                if len(factors) == 0:
                    raise Exception("Parse Error: @end without corresponding @begin")
                else:
                    factors.pop()
        else:
            raise Exception("Internal Error")
    if len(factors) != 0:
        raise Exception("Parse Error: @begin without corresponding @end")

def create_props_dict(props_tuple_array):
    output = {}
    for i in range(len(props_tuple_array)-1,-1,-1):
        key = props_tuple_array[i][0]
        value = props_tuple_array[i][1]
        output[key] = value
    return output

def parse_pattern(noun):
    # noun is a NounLexer object
    # we will return the pattern associated with it
    if noun.props is None:
        props_dict = {}
    else:
        props_dict = create_props_dict(noun.props.props)
    if noun.unit is None:
        # Single Pattern
        return Pattern.SinglePattern(noun.name.noun_core,props_dict)
    else:
        # Double Pattern
        return Pattern.DoublePattern(noun.unit.noun_core,noun.name.noun_core,props_dict)

def parse_properties_edit(base,noun):
    # rule is a RuleOutput of some kind
    # noun is a NounLexer object
    # we will if the noun does not have any
    # property edits, then we will return the base
    # if it does have property edits, then we will
    # return a PropertiesRuleOutput
    if noun.props is None:
        return base
    else:
        return RuleOutput.PropertiesRuleOutput(base,noun.props.props)

def parse_renaming_rule(left,right):
    # left and right are NounSequenceLexer objects
    # they have the correct format (SinglePattern)
    # no wildcards
    # returns a list of Rule objects
    right_outputs = list(map(
        lambda right_noun: parse_properties_edit(
            RuleOutput.RenamingRuleOutput(right_noun.name.noun_core),
                right_noun),
        right))
    # list of RenamingRuleOutput
    # or PropertiesRuleOutput
    return list(map(
        lambda left_noun: Rule.Rule(parse_pattern(left_noun),right_outputs),
        left
    ))