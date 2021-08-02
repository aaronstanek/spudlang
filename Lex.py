# defines functions for lexing input
# PreLex transforms the input into a list of list of words
# each word being encoded by a string
# here we apply lexical value to those strings

from MyNumber import MyNumber

keywords = {
    "is", "are",
    "a", "an",
    "type", "types",
    "synonym", "synonyms",
    "of", "&"
}

def lex_number(line,index):
    # line is a list of strings (words)
    # index is an int
    # returns the first number at index
    # or None if no number
    # also returns updated index
    if index >= len(line):
        return index, None
    if line[index] == "$":
        return index+1, "$"
    try:
        # first explore if this is a two part fraction
        value = MyNumber.from_string(line[index]+" "+line[index+1])
        # if that did not produce an error,
        # then we are all set
        return index+2, value
    except:
        # that didn't work
        pass
    try:
        # try just one part
        value = MyNumber.from_string(line[index])
        # if that worked, then we still have a number
        return index+1, value
    except:
        # we don't have a number
        pass
    return index, None

def is_valid_noun_char(char,is_first):
    # returns true iff the char can exist in a noun
    # returns false iff the char cannot exist in the noun
    # if is_first is True, then it check if char
    # can be the first letter of a noun
    num = ord(char)
    if num == 95:
        # _
        return True
    elif num >= 65 and num <= 90:
        # uppercase
        return True
    elif num >= 97 and num <= 122:
        # lowercase
        return True
    if is_first:
        return False
    # not first
    if num >= 48 and num <= 57:
        # numeral
        return True
    # not a recognized character
    return False

def lex_noun_core(line,index):
    # line is a list of strings (words)
    # index is an int
    # only considers if line[index]
    # could be a noun core
    # if so, it returns the core
    if index >= len(line):
        return index, None
    if line[index] == "$":
        return index+1, ["$"]
    noun_core = line[index].split(".")
    # check for valid characters
    for noun_core_element in noun_core:
        for char_index in range(len(noun_core_element)):
            if not is_valid_noun_char(noun_core_element[char_index],char_index==0):
                # we found an invalid character
                if len(noun_core) > 1:
                    # this can only be a malformed noun
                    # or a misplaced number
                    raise Exception(
                        "Syntax Error: noun contained invalid character: " + str(noun_core_element)
                        )
                else:
                    # this might be a keyword or something else
                    return index, None
    # no invalid characters
    # check if it contains any empty segments
    if any(map(lambda x: len(x) == 0, noun_core)):
        # this can only be a malformed noun
        raise Exception("Syntax Error: noun contained empty segment")
    # check if it contains any keywords
    global keywords
    if any(map(lambda x: x in keywords, noun_core)):
        # this is not allowed
        if len(noun_core) > 1:
            raise Exception("Syntax Error: noun contains keyword")
        else:
            # this is a keyword
            return index, None
    # we should be good at this point
    return index+1, noun_core

def lex_noun_props(line,index):
    # line is a list of strings (words)
    # index is an int
    # we expect + word pairs
    props = []
    global keywords
    while True:
        # it's ok if we hit the end of the line
        # at this point
        if index >= len(line):
            return index, props
        if line[index] == "+" or line[index] == "-":
            # this must be a prop
            props.append(line[index])
            index += 1
        else:
            # this is not a prop
            return index, props
        # bad if we are at the end of the string now
        if index >= len(line):
            raise Exception("Syntax Error: line terminates after "+props[-1])
        # check for invalid chars
        for char_index in range(len(line[index])):
            if not is_valid_noun_char(line[index][char_index],char_index==0):
                # this is not a valid prop
                # but we expected a valid prop
                raise Exception("Syntax Error: invalid character in prop")
        # all valid characters
        # check if it is a keyword
        if line[index] in keywords:
            # we expected a prop
            # not a keyword
            raise Exception("Syntax Error: expected prop, got keyword")
        # we should be good to go
        props.append(line[index])
        index += 1

def lex_noun(line,index):
    # line is a list of strings (words)
    # index is an int
    # lexes line, starting at index
    # returns the first index after the noun
    # and the interpretation of the noun
    # returns same index and None if a noun cannot be found at that point
    # the dictionary returned has the format
    # {"number":number,"core":["vegetable","tomato","roma"],"props":["+","chopped","-","cooked"]}
    # etc...
    if index >= len(line):
        return index, None
    initial_index = index
    # first check for a number
    index, number = lex_number(line,index)
    # number is either a MyNumber object
    # or None
    index, noun_core_1 = lex_noun_core(line,index)
    if noun_core_1 is None:
        # this cannot be a noun
        return initial_index, None
    # there noun_core_1 might be the name of the noun
    # or it might be units
    index, noun_core_2 = lex_noun_core(line,index)
    if noun_core_2 is None:
        # the first thing was not a unit
        unit = None
        noun_core = noun_core_1
    else:
        # the first thing was a units
        # the second was the noun core
        unit = noun_core_1
        noun_core = noun_core_2
    # this is a noun
    index, props = lex_noun_props(line,index)
    output = {
        "number": number,
        "unit": unit,
        "core": noun_core,
        "props": props
    }
    return index, output

def lex_noun_sequence(line,index):
    # line is a list of strings (words)
    # index is an int
    # lexes line, starting at index
    # returns the first index after the noun sequence
    # and an array of the nouns (can be empty)
    # returns same index and None if a noun cannot be found at that point
    nouns = []
    while True:
        index, noun = lex_noun(line,index)
        if noun is None:
            # if this is the first noun
            # then that's ok
            # but if this is a later noun
            # then we expected there to be a noun here
            if len(nouns) == 0:
                return index, nouns
            else:
                raise Exception("Syntax Error: expected noun after &")
        else:
            nouns.append(noun)
        if index >= len(line):
            # nothing more to lex
            return index, nouns
        elif line[index] != "&":
            # reached the end of the noun sequence
            return index, nouns
        else:
            # we are still in the noun sequence
            index += 1
            # we should be at the first index
            # of the next noun

def lex_verb(line,index):
    # lexes a verb starting at index in line
    # index is an int
    # line is list of string (words)
    # returns the index after the verb
    verb = []
    if index >= len(line):
        # nothing to lex
        return index, None
    if line[index] == "is" or line[index] == "are":
        verb.append("is")
        index += 1
    else:
        # not a verb
        return index, None
    if index >= len(line):
        raise Exception("Syntax Error: line ended unexpectedly")
    expect_modifier = False
    if line[index] == "a" or line[index] == "an":
        expect_modifier = True
        index += 1
        if index >= len(line):
            raise Exception("Syntax Error: line ended unexpectedly")
    if line[index] == "type" or line[index] == "types":
        verb.append("type")
        index += 1
    elif line[index] == "synonym" or line[index] == "synonyms":
        verb.append("synonym")
        index += 1
    elif expect_modifier:
        # we expected a modifier, but there wasn't one
        raise Exception("Syntax Error: expected modifier after a/an")
    else:
        # we didn't expect a modifier
        # and we didn't get one
        # the verb has ended
        return index, verb
    if index >= len(line):
        raise Exception("Syntax Error: line ended unexpectedly")
    if line[index] == "of":
        index += 1
        if index >= len(line):
            raise Exception("Syntax Error: line ended unexpectedly")
    return index, verb

def lex_standard(line):
    # expect noun_seq (verb noun_seq)
    index = 0
    index, left = lex_noun_sequence(line,index)
    # if there is no noun, then this is not a standard line
    if len(left) == 0:
        return None
    index, verb = lex_verb(line,index)
    if verb is None:
        # this better be the end of the line
        if index < len(line):
            raise Exception("Syntax Error: verb expected after noun")
        else:
            return {
                "type": "ingredient",
                "left": left
            }
    # we have a valid noun and a valid verb
    # and we expect that there's stuff after the verb
    index, right = lex_noun_sequence(line, index)
    if right is None:
        # we expected there to be something here
        raise Exception("Syntax Error: expected another noun(s) after verb")
    # we should be all good
    output = {
        "type": "normal_rule",
        "left": left,
        "verb": verb,
        "right": right
    }
    return output

at_commands = {
    "@hold", "@holdunit",
    "@dec", "@frac"
}

def lex_at(line):
    # expect @something
    global at_commands
    if line[0] in at_commands:
        command = line[0][1:] + "_rule"
        index, left = lex_noun_sequence(line,0)
        if left is None:
            raise Exception("Syntax Error: expected noun after "+line[0])
        if index < len(line):
            raise Exception("Syntax Error: line ended unexpectedly")
        output = {
            "type": command,
            "left": left
        }
        return output
    if line[0] == "@end":
        if len(line) > 1:
            raise Exception("Syntax Error: @end does not take arguments")
        return {"type": "end_span"}
    if line[0] == "@begin":
        if len(line) < 2:
            raise Exception("Syntax Error: expected span name after @begin")
        if line[1] == "multiply":
            # we expect there to be a number after this
            index, number = lex_number(line,2)
            if number is None:
                raise Exception("Syntax Error: expected number after @begin multiply")
            if index < len(line):
                raise Exception("Syntax Error: line ended unexpectedly: "+str(line))
            output = {
                "type": "begin_span",
                "name": "multiply",
                "value": number
            }
            return output
        raise Exception("Syntax Error: unkown span name after @begin")
    return None

def lex_all(line):
    output = lex_standard(line)
    if output is not None:
        return output
    output = lex_at(line)
    if output is not None:
        return output
    raise Exception("Syntax Error: unable to lex line with contents: "+str(line))