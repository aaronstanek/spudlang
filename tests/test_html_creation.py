from ResultsTree import ResultsTree
from Ingredient import Ingredient
from MyNumber import MyNumber

tree = ResultsTree()

tree.add_ingredient(Ingredient(
    MyNumber(5.6),["_imperial_unit","cup"],["_vegetable","tomato","roma"],{"chopped","_glazed","eaten"}
))

tree.add_ingredient(Ingredient(
    MyNumber(0.5),["_imperial_unit","cup"],["_vegetable","tomato","roma"],set()
))

tree.add_ingredient(Ingredient(
    MyNumber((5,2)),["_imperial_unit","cup"],["_vegetable","tomato","cherry"],set()
))

tree.add_ingredient(Ingredient(
    MyNumber(1.5),["_imperial_unit","cup"],["_vegetable","tomato","roma"],set()
))

tree.add_ingredient(Ingredient(
    MyNumber((6,1)),["_imperial_unit","cup"],["rice"],set()
))

tree.add_ingredient(Ingredient(
    MyNumber((6,1)),["_imperial_unit","cup"],["rice","jasmine"],set()
))

htmldoc = tree.as_html_document()
with open("ResultsTree.html","w") as file:
    file.write(htmldoc)