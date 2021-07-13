# this file defines the Ingredient class
# it can represent an item, its quantities

from MyNumber import MyNumber
from FormatCheck import listOfStrings

class Ingredient(object):
    def __init__(self,count,unit,name):
        if type(count) != MyNumber:
            raise TypeError("count must be of type MyNumber")
        listOfStrings(unit)
        listOfStrings(name)
        self.count = count
        self.unit = unit
        self.name = name