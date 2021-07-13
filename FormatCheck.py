# defines functions for checking format of inputs

def listOfStrings(x):
    # returns if x is a nonempty list
    # of nonempty strings
    # returns throws an exception otherwise
    if type(x) != list:
        raise Exception("Expected list")
    if len(x) == 0:
        raise ValueError("Expected nonempty list")
    if not all(map(lambda y: (len(y) > 0) if (type(y) == str) else False , x)):
        raise TypeError("Expected elements of list to be nonempty strings")