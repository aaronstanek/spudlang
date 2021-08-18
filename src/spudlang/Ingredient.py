# this file defines the Ingredient class
# it can represent an item, its quantities

from .MyNumber import MyNumber
from .FormatCheck import listOfStrings, setOfStrings
from copy import copy

class Ingredient(object):
    def __init__(self,count,unit,name,props):
        if not isinstance(count,MyNumber):
            raise TypeError("count must be of type MyNumber")
        listOfStrings(unit)
        listOfStrings(name)
        setOfStrings(props)
        self.count = count
        self.unit = unit
        self.name = name
        self.props = props
    def duplicate(self):
        return Ingredient(
            self.count,self.unit[:],
            self.name[:],copy(self.props)
            )
    def strip(self):
        # remove all terms starting with _
        unit = list(filter(lambda x: x[0] != "_", self.unit))
        name = list(filter(lambda x: x[0] != "_", self.name))
        if len(unit) == 0 or len(name) == 0:
            return None
        props = set(filter(lambda x: x[0] != "_", self.props))
        return Ingredient(self.count,unit,name,props)