# defines functions for converting the output of the Lexer
# into the input of the RuleBox

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