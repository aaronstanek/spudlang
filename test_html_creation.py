from ResultsTree import ResultsTree
from Ingredient import Ingredient
from MyNumber import MyNumber

tree = ResultsTree()

tree.add_ingredient(Ingredient(
    MyNumber(5.6),["imperial_unit","cup"],["vegetable","tomato","roma"],{"chopped"}
))

htmldoc = tree.as_html_document()
with open("ResultsTree.html","w") as file:
    file.write(htmldoc)