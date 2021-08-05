# second attempt at writing a parser

from Ingredient import Ingredient
from MyNumber import MyNumber
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

def parse_prefixing_rule(left,right):
    # left and right are NounSequenceLexer objects
    # they have the correct format (SinglePattern)
    # no wildcards
    # returns a list of Rule objects
    right_outputs = list(map(
        lambda right_noun: parse_properties_edit(
            RuleOutput.PrefixingRuleOutput(right_noun.name.noun_core),
            right_noun),
        right))
    # list of RenamingRuleOutput
    # or PropertiesRuleOutput
    return list(map(
        lambda left_noun: Rule.Rule(parse_pattern(left_noun),right_outputs),
        left
    ))

def parse_inserting_rule(left,right):
    # left and right are NounSequenceLexer objects
    # they have the correct format (SinglePattern)
    # no wildcards
    # returns a list of Rule objects
    rules = []
    for left_noun in left:
        pattern_size = len(left_noun.name.noun_core)
        right_outputs = list(map(
            lambda right_noun: RuleOutput.InsertingRuleOutput(
                pattern_size,right_noun.name.noun_core),
            right))
        rules.append(Rule.Rule(parse_pattern(left.noun),right_outputs))
    return rules

def parse_single_conversion(left,right):
    # left and right are NounSequenceLexer objects
    # they have the correct format (SinglePattern)
    # no wildcards
    # returns a list of Rule objects
    rules = []
    for left_noun in left:
        right_outputs = []
        for right_noun in right:
            ratio = left_noun.count.number.multiplicative_inverse() * right_noun.count.number
            right_outputs.append(RuleOutput.SingleConvertingRuleOutput(
                ratio,
                right_noun.name.noun_core
            ))
        rules.append(
            Rule.Rule(
                parse_pattern(left_noun),
                right_outputs
            )
        )
    return rules

def parse_double_conversion(left,right):
    # left and right are NounSequenceLexer objects
    # they have the correct format (SinglePattern)
    # there may be wildcards
    # returns a list of Rule objects
    rules = []
    for left_noun in left:
        right_outputs = []
        for right_noun in right:
            if right_noun.count.wildcard:
                ratio = MyNumber((1,1))
            else:
                ratio = left_noun.count.number.multiplicative_inverse() * right_noun.count.number
            right_outputs.append(RuleOutput.DoubleConvertingRuleOutput(
                ratio,
                right_noun.unit.noun_core,
                right_noun.name.noun_core
            ))
        rules.append(
            Rule.Rule(
                parse_pattern(left_noun),
                right_outputs
            )
        )
    return rules

def parse_standard_rule_helper(line,count_pattern,unit_pattern,name_pattern):
    # line is a StandardLineLexer
    # other arguments are lists of integers
    # where the values of the integers conform to NounFormat
    for f in [line.left.format,line.right.format]:
        if f.get("count") not in count_pattern:
            return False
        if f.get("unit") not in unit_pattern:
            return False
        if f.get("name") not in name_pattern:
            return False
    return True

def parse_standard_rule(line):
    # line is a StandardLineLexer
    # we know that verb is not None
    # we know that the line has consistent format
    verb = line.verb.verb
    if verb == ["is"]:
        if parse_standard_rule_helper(line,[0],[0],[1]):
            # it's a renaming rule
            return parse_renaming_rule(line.left,line.right)
        if parse_standard_rule_helper(line,[1],[0],[1]):
            # it's a single converting rule
            return parse_single_conversion(line.left,line.right)
        if parse_standard_rule_helper(line,[1,2],[1,2],[1,2]):
            # it's a double converting rule
            return parse_double_conversion(line.left,line.right)
    elif verb == ["is","type"]:
        if parse_standard_rule_helper(line,[0],[0],[1]):
            # it's a prefixing rule
            return parse_prefixing_rule(line.left,line.right)
    elif verb == ["is","synonym"]:
        if parse_standard_rule_helper(line,[0],[0],[1]):
            # it's a inserting rule
            return parse_inserting_rule(line.left,line.right)
    raise Exception("Parser Error: Unable to parse standard rule")

def parse_standard_ingredient(line):
    # line is a StandardLineLexer
    # we know that verb is None
    # we know that left is defined
    output = []
    for noun in line.left.sequence:
        if noun.count is None:
            if noun.unit is None:
                count = MyNumber((1,1))
                unit = ["mealsworth"]
            elif noun.unit.wildcard:
                raise Exception("Parser Error: Wildcards forbidden in ingredient declaration.")
            else:
                raise Exception("Parser Error: Unit without quantity is forbidden in ingredient declaration")
        elif noun.count.wildcard:
            raise Exception("Parser Error: Wildcards forbidden in ingredient declaration.")
        else:
            count = noun.count.number
            if noun.unit is None:
                unit = ["count"]
            elif noun.unit.wildcard:
                raise Exception("Parser Error: Wildcards forbidden in ingredient declaration.")
            else:
                unit = noun.unit.noun_core
        name = noun.name.noun_core
        props = set()
        if noun.props is not None:
            for prop_tuple in noun.props.props:
                if prop_tuple[1] == False:
                    raise Exception("Parser Error: Prop removal in ingredient declaration is forbidden.")
                props.add(prop_tuple[0])
        output.append(Ingredient(count,unit,name,props))
    return output

def parse_hold(left):
    # left is a valid noun sequence
    return list(map(
        lambda left_noun: Rule.HoldRule(parse_pattern(left_noun),0),
        left))

def parse_holdunit(left):
    # left is a valid noun sequence
    return list(map(
        lambda left_noun: Rule.HoldRule(parse_pattern(left_noun),4),
        left))

def parse_dec(left):
    # left is a valid noun sequence
    return list(map(
        lambda left_noun: Rule.Rule(
            parse_pattern(left_noun),
            RuleOutput.DecRuleOutputInstance
            ),
        left))

def parse_frac(left):
    # left is a valid noun sequence
    return list(map(
        lambda left_noun: Rule.Rule(
            parse_pattern(left_noun),
            RuleOutput.FracRuleOutputInstance
            ),
        left))

def parse_at_command(line):
    # we know that line is an AtCommandLexer object
    # it must have a defined verb
    if line.verb == ["@hold"]:
        return parse_hold(line)
    elif line.verb == ["@holdunit"]:
        return parse_holdunit(line)
    elif line.verb == ["@dec"]:
        return parse_dec(line)
    elif line.verb == ["@frac"]:
        return parse_frac(line)
    elif line.verb == ["@begin","multiply"]:
        return []
    elif line.verb == ["@end"]:
        return []
    else:
        raise Exception("Internal Error")

def parse_line(line):
    # line is a StandardLineLexer object
    # of a AtCommandLexer
    # all this function does is to direct
    # the line to the appropriate parser
    # returns an array of Rule
    # or an array of Ingredient
    if isinstance(line,StandardLineLexer):
        if line.verb is None:
            return parse_standard_ingredient(line)
        else:
            return parse_standard_rule(line)
    elif isinstance(line,AtCommandLexer):
        return parse_at_command(line)
    else:
        raise Exception("Internal Error")

def parse_all_lines(lines):
    # lines is a list of StandardLineLexer objects
    # and AtCommandLexer objects
    # returns ingredients array
    # and rules array
    ingredients = []
    rules = []
    for line in lines:
        results = parse_line(line)
        for result in results:
            if isinstance(result,Ingredient):
                ingredients.append(result)
            elif isinstance(result,Rule.Rule):
                rules.append(result)
            else:
                raise Exception("Internal Error")
    return ingredients, rules