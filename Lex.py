# defines functions for lexing input
# PreLex transforms the input into a list of list of words
# each word being encoded by a string
# here we apply lexical value to those strings

end_of_noun = {
    "is", "are",
    "a", "an",
    "type", "types",
    "synonym", "synonyms",
    "of", "&"
}

def lex_noun(line,index):
    # line is a list of strings (words)
    # index is an int
    # lexes line, starting at index
    # returns the first index after the noun
    # and the interpretation of the noun
    # returns same index and None if a noun cannot be found at that point
    # the dictionary returned has the format
    # {"core":["vegetable","tomato","roma"],"props":["+","chopped","-","cooked"]}
    # etc...
    if index >= len(line):
        return index, None
    global end_of_noun
    if line[index] in end_of_noun:
        # this is not a noun
        return index, None
    # this is a noun, or a Syntax Error
    # noun may not contain @
    if line[index].find("@") != -1:
        raise Exception("Syntax Error: @ may not be present in a noun")
    noun_core = line[index].split(".")
    if any(map(lambda x: x in end_of_noun),noun_core):
        # this is a syntax error
        raise Exception("Syntax Error: noun contains keyword")
    props = []
    # keep adding props until we hit an end_of_noun,
    # the end of the string, or an unpaired +-
    index += 1
    while True:
        # if this is the end of the noun,
        # it is totally valid
        if index >= len(line):
            return index, {"core":noun_core,"props":props}
        if line[index] in end_of_noun:
            return index, {"core":noun_core,"props":props}
        # this is not the end
        # consume props until we reach something that
        # looks like the end
        # we expect + -
        if line[index] == "+" or line[index] == "-":
            props.append(line[index])
            index += 1
        else:
            # syntax error
            raise Exception("Syntax Error: expected + or -")
        if index >= len(line):
            raise Exception("Syntax Error: reached end of line after + or -")
        if line[index] in end_of_noun:
            raise Exception("Syntax Error: reached end of noun after + or -")
        # a prop may not contain . or @
        if line[index].find(".") != -1:
            raise Exception("Syntax Error: . may not be present in a prop")
        if line[index].find("@") != -1:
            raise Exception("Syntax Error: @ may not be present in a prop")
        # this is a correctly formed prop
        props.append(line[index])
        index += 1