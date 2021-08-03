# second attempt at writing a lexer
# use objects to hold lex results
# in place of dicts

from _typeshed import OpenTextModeUpdating
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
        # jsut like the input to PropertiesRuleOutput
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