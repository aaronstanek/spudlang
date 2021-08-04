# second attempt at writing a parser

from Lex2 import StandardLineLexer, AtCommandLexer
import RuleOutput

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