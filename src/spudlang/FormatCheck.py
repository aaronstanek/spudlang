# defines functions for checking format of inputs

def listOfStrings(x):
    # returns if x is a nonempty list
    # of nonempty strings
    # returns throws an exception otherwise
    if type(x) != list:
        raise TypeError("Expected list")
    if len(x) == 0:
        raise ValueError("Expected nonempty list")
    if not all(map(lambda y: (len(y) > 0) if (type(y) == str) else False , x)):
        raise TypeError("Expected elements of list to be nonempty strings")

def listOfTupleStringBools(x):
    if type(x) != list:
        raise TypeError("Expected list")
    for elem in x:
        if type(elem) != tuple:
            raise TypeError("Expected tuple")
        if len(elem) != 2:
            raise ValueError("Expected tuple of length 2")
        if type(elem[0]) != str:
            raise TypeError("Expected string")
        if type(elem[1]) != bool:
            raise TypeError("Expected bool")

def setOfStrings(x):
    # returns if x is a set of strings
    # throws and expection otherwise
    if type(x) != set:
        raise TypeError("Expected set")
    if not all(map(lambda y: (len(y) > 0) if (type(y) == str) else False , x)):
        raise TypeError("Expected elements of set to be nonempty strings")

def dictStrBool(x):
    # returns if x is dict(str->bool)
    # throws exception otherwise
    if type(x) != dict:
        raise TypeError("Expected dict")
    for key in x:
        if type(key) != str:
            raise ValueError("Expected dict with str keys")
        value = x[key]
        if type(value) != bool:
            raise TypeError("Expected dict with str keys and bool values")