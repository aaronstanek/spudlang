# defines functions for parsing input code

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
            return word[0] == "#" or word[0] == "/":
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