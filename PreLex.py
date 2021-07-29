# defines functions for parsing input code

from MyNumber import MyNumber

def convert_equivalent_codes(raw):
    # raw is an array of byte values
    # we convert 13 -> 10
    # we convert 9 -> 32
    return list(map(lambda x: 10 if x == 13 else (32 if x == 9 else x) , raw ))

def make_lines(raw):
    # raw is an array of byte values
    # no 13 or 9
    # split along 10 values
    # and convert into UTF-8 strings
    lines = []
    line = []
    for value in raw:
        if value == 10:
            lines.append(bytes(line).decode("utf-8"))
            line = []
        else:
            line.append(value)
    lines.append(bytes(line).decode("utf-8"))
    return lines

def is_empty(s):
    # s is a string
    # returns True if s has length zero
    # or is composed only of whitespace
    if len(s) == 0:
        return True
    return all(map(lambda x: x == " ", s))

def is_comment(s):
    # s is a string
    # returns True if s starts with # or /
    # returns False otherwise
    # we know that s is not empty
    words = s.split(" ")
    for word in words:
        if len(word) != 0:
            return word[0] == "#" or word[0] == "/"
    # if we end up here
    # then the input was an empty string
    raise Exception("bad program state")

def is_import(s):
    # s is a nonempty string
    # returns True if s is an import statement
    # returns False otherwise
    words = s.split(" ")
    for word in words:
        if len(word) != 0:
            return word == "@import"
    # if we end up here
    # then the input was an empty string
    raise Exception("bad program state")

def interpret_import(s):
    # s is an import statement
    # @import is the first nonempty bit
    import_index = s.find("@import")
    path_index = import_index + 7
    path = s[path_index:]
    # safe to remove initial and traling spaces
    # but not spaces in the middle
    while True:
        if len(path) == 0:
            break
        if path[0] == " ":
            path = path[1:]
            continue
        else:
            break
    while True:
        if len(path) == 0:
            break
        if path[-1] == " ":
            path = path[:-1]
            continue
        else:
            break
    return path

canonical_letters = {
    # some characters are padded
    "$": " $ ",
    "&": " & ",
    "+": " + ",
    "-": " - ",
    # some characters are not
    " ": " ",
    "@": "@",
    ".": ".",
    "_": "_"
}

def grow_canonical():
    global canonical_letters
    for i in range(48,58):
        # numerals
        c = chr(i)
        canonical_letters[c] = c
    for i in range(65,91):
        # capitals
        c = chr(i)
        canonical_letters[c] = c
        # lowercase
        c = chr(i+32)
        canonical_letters[c] = c

grow_canonical()

def validate_and_expand(s):
    # s is a string, a line of code
    # nonempty, not a comment, not an import
    # we will replace all valid characters
    # with their canonical representations
    # we will throw an Exception on invalid characters
    global canonical_letters
    output = []
    for c in s:
        if c in canonical_letters:
            output.append(canonical_letters[c])
        else:
            raise Exception("Invalid character charcode:"+str(ord(c))+" letter:"+c)
    return "".join(output)

def make_words(s):
    # s is a string
    # a line of code
    # it is nonempty
    # we will return a list of nonempty strings
    # containing the words in the line of code
    # of does not have any meaning
    # and will be excluded at this stage
    words = s.split(" ")
    return list(filter(lambda x: len(x) != 0 and x != "of", words))

synonym_key_words = {"synonym","synonyms"}
synonym_error_words = {"$","&"}
synonym_ignore_words = {"is","are","a","an"}

def parse_synonym_rule(s):
    # s is a list of nonempty strings
    # if s is a synonym rule
    # then the rule is returned
    # returns None otherwise
    global synonym_key_words
    synonyms = len(filter(lambda x: x in synonym_key_words, s))
    if synonyms == 0:
        return None
    if synonyms > 1:
        raise Exception("Syntax Error: Multiple instances of synonym in one line")
    # it must be a synonym statement
    # or an invalid statement
    global synonym_error_words
    if any(map(lambda x: x in synonym_error_words, s)):
        raise Exception("Synonym statements may not contain $ or &")
    global synonym_ignore_words
    s = list(map(lambda x: x not in synonym_ignore_words, s))
    for i in range(len(s)):
        if s[i] in synonym_key_words:
            break_index = i
            break
    # the loop above will yield a break_index
    # because we know that exactly one of the elements
    # of s is in synonym_key_words
    left = s[:break_index]
    right = s[break_index+1:]
    # left and right may only contain
    # ended here
    # need a way to group parts of a number together
    # need to group noun + adjective together