# this file defines the Ingredient class
# it can represent an item, its quantities

from typing import Type
from MyNumber import MyNumber

class Ingredient(object):
    def __init__(self,count,unit,name):
        if type(count) != MyNumber:
            raise TypeError("count must be of type MyNumber")
        for things in [(unit,"unit"),(name,"name")]:
            if type(things[0]) != list:
                raise TypeError(things[1]+" must be a list")
            if not all(map(lambda x: (len(x) > 0) if (type(x) == str) else False , things[0])):
                raise TypeError("elements of "+things[1]+" must be nonempty strings")
        self.count = count
        self.unit = unit
        self.name = name