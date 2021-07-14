# this file defines the Ingredient class
# it can represent an item, its quantities

from MyNumber import MyNumber
from FormatCheck import listOfStrings, setOfStrings

class Ingredient(object):
    def __init__(self,count,unit,name,props):
        if type(count) != MyNumber:
            raise TypeError("count must be of type MyNumber")
        listOfStrings(unit)
        listOfStrings(name)
        setOfStrings(props)
        self.count = count
        self.unit = unit
        self.name = name
        self.props = props