# defines the ResultsTree class
# used for storing the output of the program
# and for saving the results as an html document

from .Ingredient import Ingredient

class ResultsTree(object):
    def __init__(self):
        self.terms = []
        self.subtrees = {}
    def add_ingredient(self,ig):
        if ig is None:
            return
        if not isinstance(ig,Ingredient):
            raise TypeError("Expected ingredient")
        put_in_terms = False
        if len(ig.name) == 1:
            if ig.name[0] == "==here==":
                put_in_terms = True
        if put_in_terms:
            # we will put it in the terms
            # try to add it to an exist term if possible
            for i in range(len(self.terms)):
                term = self.terms[i]
                if term.unit == ig.unit and term.props == ig.props:
                    # we have a match
                    self.terms[i] = Ingredient(
                        term.count + ig.count,
                        term.unit,
                        term.name,
                        term.props
                    )
                    return
            # no match in the terms
            # add a new term
            self.terms.append(ig)
        else:
            # we will put it in the subtrees
            if ig.name[0] in self.subtrees:
                # we can hand it off to the subtree for processing
                st = self.subtrees[ig.name[0]]
            else:
                # the subtree does not exist yet
                # we need to make it
                st = ResultsTree()
                self.subtrees[ig.name[0]] = st
            new_ig = ig.duplicate()
            if len(new_ig.name) == 1:
                new_ig.name = ["==here=="]
            else:
                new_ig.name = new_ig.name[1:]
            st.add_ingredient(new_ig)
    def as_html(self,node_name):
        # node_name is the string key
        # used to identify this object
        # in the parent tree's dictionary
        output = ["<li>",node_name,"<ul>"]
        for term in self.terms:
            output.append("<li>")
            output.append(str(term.count))
            for unit in term.unit:
                output.append(" ")
                output.append(unit)
            props = list(term.props)
            props.sort()
            for prop in props:
                output.append(" ")
                output.append(prop)
            output.append("</li>")
        subtree_names = list(self.subtrees)
        subtree_names.sort()
        for subtree_name in subtree_names:
            subtree = self.subtrees[subtree_name]
            output.append(subtree.as_html(subtree_name))
        output.append("</ul>")
        output.append("</li>")
        return "".join(output)
    def as_html_document(self):
        output = [
            "<!DOCTYPE html>","<html>","<head>",
            "<meta charset=\"utf-8\" />",
            "</head>","<body>","<ul>"
            ]
        output.append(self.as_html("groceries"))
        output.append("</ul>")
        output.append("</body>")
        output.append("</html>")
        return "".join(output)
