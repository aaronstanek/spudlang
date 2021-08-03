# second attempt at writing a lexer
# use objects to hold lex results
# in place of dicts

from MyNumber import MyNumber

class NumberLexer(object):
    def __init__(self,number):
        # number is a MyNumber object
        # or None
        self.wildcard = (number is None)
        self.number = number
    @staticmethod
    def lex(line,index):
        # line is a list of strings (words)
        # index is an int
        # returns the first number at index
        # or None if no number
        # also returns updated index
        if index >= len(line):
            return index, None
        if line[index] == "$":
            return index+1, NumberLexer(None)
        try:
            # first explore if this is a two part fraction
            value = MyNumber.from_string(line[index]+" "+line[index+1])
            # if that did not produce an error,
            # then we are all set
            return index+2, NumberLexer(value)
        except:
            # that didn't work
            pass
        try:
            # try just one part
            value = MyNumber.from_string(line[index])
            # if that worked, then we still have a number
            return index+1, NumberLexer(value)
        except:
            # we don't have a number
            pass
        return index, None

keywords = {
    "is", "are",
    "a", "an",
    "type", "types",
    "synonym", "synonyms",
    "of", "&"
}

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

class NounCoreLexer(object):
    def __init__(self,noun_core):
        # noun_core is either None
        # or a list of strings each being
        # the component of a noun_core
        self.wildcard = (noun_core is None)
        self.noun_core = noun_core
    def _scan_for_invalid_characters(self):
        # returns True if there are not invalid chars
        # throws if there is an invalid char
        # returns False if there is an invalid char
        # but this may not be intended to be a noun
        for component in self.noun_core:
            for char_index in range(len(component)):
                char = component[char_index]
                if not is_valid_noun_char(char,char_index==0):
                    if len(self.noun_core) > 1:
                        # the user clearly intended this to be a noun
                        raise Exception("Syntax Error: invalid character in noun: "+str(self.noun_core))
                    else:
                        # it is unclear if the user intended this to be a noun
                        # try to lex it in other ways
                        return False
        return True
    def _scan_for_empty_segments(self):
        # returns None
        # throws if there are any empty segments
        if any(lambda x: len(x) == 0, self.noun_core):
            # if there is an empty segment anywhere
            # then we can be sure that it is a Syntax Issue
            raise Exception("Syntax Error: empty segment in noun: "+str(self.noun_core))
    def _scan_for_keywords(self):
        # returns True if there are no keywords
        # throws if there are
        # returns False if there are, but this might actually
        # be a valid keyword
        global keywords
        if any(lambda x: x in keywords, self.noun_core):
            # it contains a keyword
            if len(self.noun_core) > 1:
                # clearly intended to be a noun
                raise Exception("Syntax Error: keyword in noun: "+str(self.noun_core))
            else:
                # it's just a keyword
                return False
        return True
    @staticmethod
    def lex(line,index):
        # line is a list of strings (words)
        # index is an int
        # only considers if line[index]
        # could be a noun core
        # returns either a NounCoreLexer object
        # or None
        if index >= len(line):
            return index, None
        if line[index] == "$":
            return index+1, NounCoreLexer(None)
        output = NounCoreLexer(line[index].split("."))
        if not output._scan_for_invalid_characters():
            # it's not a valid noun
            # and it's unclear if it should be interpeted
            # as a noun
            return index, None
        output._scan_for_empty_segments() # returns None
        if not output._scan_for_keywords():
            # it's not a valid noun
            # but it may be a valid keyword
            return index, None
        # it has length > 0
        # it does not contain any empty segments
        # it does not contain any numbers, keywords,
        # or invalid characters
        # it's probably good to go
        return index+1, output

class PropsLexer(object):
    def __init__(self):
        # self.props is list(tuple(str,bool))
        # just like the input to PropertiesRuleOutput
        self.props = []
    @staticmethod
    def lex(line,index):
        # line is a list of strings (words)
        # index is an int
        # we expect + word pairs
        # returns PropsLexer or None
        output = PropsLexer()
        while True:
            if index >= len(line):
                # we have exhaused all
                # that there is to lex here
                if len(output.props):
                    return index, output
                else:
                    return index, None
            if line[index] == "+":
                value = True
            elif line[index] == "-":
                value = False
            else:
                # this is not a prop
                if len(output.props):
                    return index, output
                else:
                    return index, None
            # value if defined
            index += 1
            if index >= len(line):
                # we can't end a line with + or -
                raise Exception("Syntax Error: line cannot end with "+line[index-1]+" in : "+str(line))
            # line[index] is defined
            # check for invalid characters
            for char_index in len(line[index]):
                char = line[index][char_index]
                if not is_valid_noun_char(char,char_index==0):
                    # there was a + or -
                    # the user intended this to be a prop
                    raise Exception("Syntax Error: invalid character in prop: "+str(line))
            # all the caracters are valid
            global keywords
            if line[index] in keywords:
                # the user intended this to be a prop
                # not a keyword
                raise Exception("Syntax Error: expected prop, got keyword, in: "+str(line))
            output.props.append( (line[index],value) )
            index += 1

class NounLexer(object):
    def __init__(self):
        self.count = None # NumberLexer or None
        self.unit = None # NounCoreLexer or None
        self.name = None # NounCoreLexer or None
        self.props = None # PropsLexer or None
        # exact same names as Ingredient
    def must_not_be_defined(self,field):
        return (getattr(self,field) is None)
    def must_be_defined(self,field):
        return (getattr(self,field) is not None)
    def must_not_be_wildcard(self,field):
        # applies to self.count,
        # self.unit and self.name
        if getattr(self,field) is None:
            return True
        else:
            return not getattr(self,field).wildcard
    @staticmethod
    def lex(line,index):
        # line is a list of strings (words)
        # index is an int
        # lexes line, starting at index
        # returns the first index after the noun
        # and the interpretation of the noun
        # returns same index and None if a noun cannot be found at that point
        # the dictionary returned has the format
        if index >= len(line):
            return index, None
        fallback_index = index
        output = NounLexer()
        # first see if there is a number
        index, output.count = NumberLexer.lex(line,index)
        # we don't actually have to know if it returned
        # to continue
        index, noun_core_1 = NounCoreLexer.lex(line,index)
        if noun_core_1 is None:
            # this cannot be a noun of any kind
            # but it might be something else
            return fallback_index, None
        index, noun_core_2 = NounCoreLexer.lex(line,index)
        # we know that noun_core_1 is not None
        if noun_core_2 is None:
            # there is only a value, and no unit
            output.name = noun_core_1
        else:
            # both noun_core_1 and
            # noun_core_2 are defined
            # the first is a unit
            # the second is a name
            output.unit = noun_core_1
            output.name = noun_core_2
        index, output.props = PropsLexer.lex(line,index)
        # we don't actually have to know if it returned
        # to continue
        return index, output

class NounSequenceLexer(object):
    def __init__(self):
        self.sequence = [] # contains NounLexer
    @staticmethod
    def lex(line,index):
        # line is a list of strings (words)
        # index is an int
        # lexes line, starting at index
        # returns the first index after the noun sequence
        # and an array of the nouns (can be empty)
        # returns same index and None if a noun cannot be found at that point
        output = NounSequenceLexer()
        expect_noun = False
        while True:
            if index >= len(line):
                # nothing more to lex
                if expect_noun:
                    raise Exception("Syntax Error: expected noun after $: "+str(line))
                if len(output.sequence) == 0:
                    # there was never anything to lex
                    return index, None
                else:
                    # there was a noun at the end of the line
                    return index, output
            # line[index] is defined
            index, noun = NounLexer(line,index)
            if noun is None:
                # there is no noun here
                if expect_noun:
                    raise Exception("Syntax Error: expected noun after $: "+str(line))
                if len(output.sequence) == 0:
                    return index, None
                else:
                    return index, output
            output.sequence.append(noun)
            # this might be the end of the line
            if index >= len(line):
                return index, output
            # there is more line
            # if the next token is not $
            # then this is the end of the sequence
            if line[index] != "$":
                return index, output
            # there is more to the sequence
            index += 1
            expect_noun = True

class VerbLexer(object):
    def __init__(self):
        self.verb = [] # contains str
    @staticmethod
    def lex(line,index):
        # lexes a verb starting at index in line
        # index is an int
        # line is list of string (words)
        # returns the index after the verb
        if index >= len(line):
            # nothing to lex
            return index, None
        output = VerbLexer()
        if line[index] in {"is","are"}:
            output.verb.append("is")
            index += 1
        else:
            # not a verb
            # but may be something else valid
            return index, None
        if index >= len(line):
            # we just got an is
            # we were expecting more
            raise Exception("Syntax Error: reached end of line after is: "+str(line))
        if line[index] == "a":
            # a is entirely optional
            # but it will require more verb after it
            has_a = True
            index += 1
            if index >= len(line):
                raise Exception("Syntax Error: reached end of line after a: "+str(line))
        else:
            has_a = False
        if line[index] in {"type","types"}:
            # we have more verb
            output.verb.append("type")
            index += 1
        elif line[index] in {"synonym","synonyms"}:
            # we have more verb
            output.verb.append("synonym")
            index += 1
        else:
            # we do not have more verb
            if has_a:
                # we were expecting more verb
                raise Exception("Syntax Error: expected type or synonym after a: "+str(line))
            else:
                # it's ok for the verb to end here
                return index, output
        if index >= len(line):
            raise Exception("Syntax Error: line ends after verb: "+str(line))
        if line[index] == "of":
            # optional
            index += 1
            if index >= len(line):
                raise Exception("Syntax Error: line ends after verb: "+str(line))
        return line, output