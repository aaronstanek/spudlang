# defines functions for converting the output of the Lexer
# into the input of the RuleBox

from MyNumber import MyNumber
from Ingredient import Ingredient

def resolve_spans(lines):
    # currently the only span is the
    # multiply
    # so we will just assume that the lexer gives us multiply spans
    output = []
    factors = []
    for line in lines:
        if line["type"] == "begin_span":
            factors.append(line["value"])
        elif line["type"] == "end_span":
            if len(factors) == 0:
                raise Exception("@end without corresponding @begin")
            else:
                factors.pop()
        elif len(factors) == 0 or line["type"] != "ingredient":
            output.append(line)
        else:
            # it's an ingredient
            # in a multiply span
            for i in range(len(line["left"])):
                if line["left"][i]["number"] is None:
                    continue
                for j in range(len(factors)-1,-1,-1):
                    line["left"][i]["number"] = line["left"][i]["number"] * factors[j]
            output.append(line)
    if len(factors) != 0:
        raise Exception("@begin without corresponding @end")
    return output

def parse_ingredient(line):
    left = line["left"]
    if len(left) != 1:
        raise Exception("Syntax Error: expected exactly one ingredient per line")
    number = left[0]["number"]
    unit = left[0]["unit"]
    noun_core = left[0]["core"]
    props = left[0]["props"]
    if unit is None and number is not None:
        unit = ["count"]
    elif number is None and unit is not None:
        raise Exception("Syntax Error: unit without quantity")
    elif unit is None and number is None:
        number = MyNumber((1,0))
        unit = ["mealsworth"]
    active_props = set()
    for p in props:
        if p == "+":
            pass
        elif p == "-":
            raise Exception("Syntax Error: - not allowed in ingredient declaration")
        else:
            active_props.add(p)
    return Ingredient(number,unit,noun_core,active_props)
    

def parse(line):
    if line["type"] == "ingredient":
        return parse_ingredient(line)
    elif line["type"] == "normal_rule":
        pass
    elif line["type"] == "hold_rule":
        pass
    elif line["type"] == "holdunit_rule":
        pass
    elif line["type"] == "dec_rule":
        pass
    elif line["type"] == "frac_rule":
        pass
    else:
        raise Exception("Internal Error: unknown line type")