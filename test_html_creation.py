from ResultsTree import ResultsTree
from Ingredient import Ingredient
from MyNumber import MyNumber

tree = ResultsTree()

tree.add_ingredient(Ingredient(
    MyNumber(5.6),["_imperial_unit","cup"],["_vegetable","tomato","roma"],{"chopped","_glazed","eaten"}
))

htmldoc = tree.as_html_document()
with open("ResultsTree.html","w") as file:
    file.write(htmldoc)