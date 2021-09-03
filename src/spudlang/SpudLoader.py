# defines the SpudLoader class
# to load and parse source files

import os
import hashlib
from copy import copy
import antlr4
from antlr4.error.ErrorListener import ErrorListener
from .Pattern import SinglePattern, DoublePattern
from .Rule import Rule, HoldRule
from .RuleOutput import DecRuleOutputInstance, FracRuleOutputInstance
from .SpudLexer import SpudLexer
from .SpudParser import SpudParser

from .MyNumber import MyNumber
from .Ingredient import Ingredient

class MyErrorListener(ErrorListener):
    # from https://stackoverflow.com/questions/32224980/python-2-7-antlr4-make-antlr-throw-exceptions-on-invalid-input
    def __init__(self,filename):
        super(MyErrorListener, self).__init__()
        self.filename = filename
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise Exception("Syntax Error in file: "+str(self.filename)+" on line: "+str(line)+" in column: "+str(column)+" with message: "+str(msg))
    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        pass
    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        pass
    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        pass

class SpudLoader(object):
    def __init__(self):
        self.ingredients = []
        self.rules = []
        self.seen = set() # sha256 hashes of files
    @staticmethod
    def load_file_raw(path):
        if path[-5:] != ".spud":
            path = path + ".spud"
        if os.path.isfile(path):
            with open(path,"rb") as file:
                return file.read()
        else:
            raise Exception("Unable to locate file: "+path)
    def get_tree(self,abs_path):
        # abs_path is a string with the absolute file path to load
        # returns either the syntax tree for the source file
        # or None
        raw = self.load_file_raw(abs_path)
        file_hash = hashlib.sha256(raw).digest()
        if file_hash in self.seen:
            # we have seen this file before
            return None
        else:
            # we have not seen this file before
            # register it so that we do not
            # need to process it again
            self.seen.add(file_hash)
        # first convert the input to a string
        # and then to a stream
        raw_string = raw.decode("UTF-8")
        stream = antlr4.InputStream(raw_string)
        # stream contains the input
        lexer = SpudLexer(stream)
        token_stream = antlr4.CommonTokenStream(lexer)
        # token_stream contains a stream of tokens
        # from the input
        parser = SpudParser(token_stream)
        parser.addErrorListener( MyErrorListener(abs_path) )
        tree = parser.spud()
        # tree is the entire syntax tree for the input
        return tree
    @staticmethod
    def extract_imports(output,tree):
        if isinstance(tree,SpudParser.AtimportContext):
            # we found one
            output.append(tree.getText())
        elif isinstance(tree,(SpudParser.SpudContext,
                SpudParser.LineContext,
                SpudParser.LineatContext,
                SpudParser.AtsectionContext)):
            if tree.children is None:
                return
            for child in tree.children:
                SpudLoader.extract_imports(output,child)
    @staticmethod
    def convert_to_absolute_pathnames(base_dir,path):
        if os.path.isabs(path):
            return path
        else:
            output = os.path.join(base_dir,path)
            output = os.path.abspath(output)
            return output
    @staticmethod
    def resolve_import_path(base_dir,statement):
        # we know that @import exists in the statement
        index = statement.find("@import")
        # chop off the @import
        statement = statement[index+7:]
        # chop off all leading spaces
        while True:
            if len(statement) < 1:
                break
            if statement[0] == " " or statement[0] == "\t":
                statement = statement[1:]
            else:
                break
        # chop off all training spaces
        while True:
            if len(statement) < 1:
                break
            if statement[-1] == " " or statement[-1] == "\t":
                statement = statement[:-1]
            else:
                break
        return SpudLoader.convert_to_absolute_pathnames(base_dir,statement)
    def _handle_all_prop_elements(self,tree,context):
        # tree is SpudParser.Propspluselem
        # or SpudParser.Propselem
        # or SpudParser.Propswildelem
        for child in tree.children:
            # all terminal nodes
            text = child.getText()
            if child.getSymbol().type == SpudParser.Namesegment:
                return (sign,text)
            elif text == "$":
                return (sign,text)
            elif text == "+":
                sign = True
            elif text == "-":
                sign = False
    def _handle_all_props(self,tree,context):
        # tree is SpudParser.Propsplus
        # or SpudParser.Props
        # or SpudParser.Propswild
        if tree.children is None:
            return []
        props = []
        for child in tree.children:
            props.append(self._handle_all_prop_elements)
        return props
    def _handle_all_names(self,tree,context):
        # tree is SpudParser.Basicname
        # or SpudParser.Powname
        name = []
        if isinstance(tree,SpudParser.PownameContext):
            for child in tree.children:
                if isinstance(child,antlr4.tree.Tree.TerminalNodeImpl):
                    # this can only be !
                    name.append("!")
                else:
                    # this can only be SpudParser.Basicname
                    name += self._handle_all_names(child,context)
        else:
            # all children are terminal nodes
            for child in tree.children:
                if child.getSymbol().type == SpudParser.Namesegment:
                    name.append(child.getText())
        return name
    def _handle_name_and_props(self,tree,context):
        # tree is:
        # SpudParser.Basicnameplusprops
        # SpudParser.Pownamewithprops
        # SpudParser.Wildcardwithprops
        # SpudParser.Basicnamewithpropswild
        # SpudParser.Wildcardwithpropswild
        # SpudParser.Powwildwithprops
        # SpudParser.Basicwildwithprops
        if isinstance(tree,(SpudParser.PowwildwithpropsContext,SpudParser.BasicwildwithpropsContext)):
            return self._handle_name_and_props(tree.children[0])
        if isinstance(tree.children[0],antlr4.tree.Tree.TerminalNodeImpl):
            # can only be $
            name = None
        else:
            name = self._handle_all_names(tree.children[0],context)
        props = self._handle_all_props(tree.children[1],context)
        return name, props
    def _handle_lineingredient(self,tree,context):
        # tree is SpudParser.Lineingredient
        number = None
        unit = None
        for child in tree.children:
            if isinstance(child,SpudParser.NumberContext):
                number = MyNumber.from_tree(child)
            elif isinstance(child,SpudParser.BasicnameContext):
                # units
                unit = self._handle_all_names(child,context)
            elif isinstance(child,SpudParser.BasicnamepluspropsContext):
                # name and props
                name, props_raw = self._handle_name_and_props(child,context)
                props = set()
                for prop in props_raw:
                    props.add(prop[0])
        if number is None:
            # unit is also None
            number = MyNumber((1,0))
            unit = ["mealsworth"]
        elif unit is None:
            # unit is None
            # but number is defined
            unit = ["count"]
        if "multiply" in context:
            number = number * context["multiply"]
        self.ingredients.append( Ingredient(number,unit,name,props) )
    def _handle_linestandardrule(self,tree,context):
        raise NotImplementedError()
    def _handle_atsub1(self,tree,context):
        # tree is SpudPArser.Atsub1Context
        for child in tree.children:
            if isinstance(child,SpudParser.PownamewithpropsContext):
                name, props = self._handle_name_and_props(child,context)
                return DoublePattern(None,name,props)
    def _handle_atsub2(self,tree,context):
        # tree is SpudParser.Atsub2Context
        name = None
        props = set()
        for child in tree.children:
            if isinstance(child,SpudParser.PownameContext):
                unit = self._handle_all_names(child,context)
            elif isinstance(child,SpudParser.PowwildwithpropsContext):
                name, props = self._handle_name_and_props(child,context)
        return DoublePattern(unit,name,props)
    def _handle_atsub(self,tree,context):
        # tree is SpudParser.AtsubContext
        for child in tree.children:
            if isinstance(child,SpudParser.Atsub1Context):
                return self._handle_atsub1(child,context)
            if isinstance(child,SpudParser.Atsub2Context):
                return self._handle_atsub2(child,context)
    def _handle_athold(self,tree,context):
        # tree is SpudParser.AtholdContext
        for child in tree.children:
            if isinstance(child,SpudParser.AtsubContext):
                pattern = self._handle_atsub(child,context)
                self.rules.append(HoldRule(pattern,0))
                # holds have priority 0
    def _handle_atholdunit(self,tree,context):
        # tree is SpudParser.AtholdunitContext
        for child in tree.children:
            if isinstance(child,SpudParser.AtsubContext):
                pattern = self._handle_atsub(child,context)
                self.rules.append(HoldRule(pattern,4))
                # holdunits have priority 4
    def _handle_atdec(self,tree,context):
        # tree is SpudParser.AtdecContext
        for child in tree.children:
            if isinstance(child,SpudParser.AtsubContext):
                pattern = self._handle_atsub(child,context)
                self.rules.append(Rule(pattern,[DecRuleOutputInstance]))
    def _handle_atfrac(self,tree,context):
        # tree is SpudParser.AtfracContext
        for child in tree.children:
            if isinstance(child,SpudParser.AtsubContext):
                pattern = self._handle_atsub(child,context)
                self.rules.append(Rule(pattern,[FracRuleOutputInstance]))
    def _handle_atbegin(self,tree,context):
        # tree is SpudParser.AtbeginContext
        # return a new context with the correct value of multiply
        for child in tree.children:
            if isinstance(child,SpudParser.number):
                value = MyNumber.from_tree(child)
                new_context = copy.copy(value)
                if "multiply" in new_context:
                    value = new_context["multiply"] * value
                new_context["multiply"] = value
                return new_context
        raise Exception("Internal Error")
    def _handle_atsection(self,tree,context):
        # tree is SpudParser.AtsectionContext
        for child in tree.children:
            # ignore atend
            if isinstance(child,SpudParser.AtbeginContext):
                context = self._handle_atbegin(child,context)
            elif isinstance(child,SpudParser.LineContext):
                self._handle_line(child,context)
    def _handle_lineat(self,tree,context):
        # tree is SpudParser.LineatContext
        for child in tree.children:
            if isinstance(child,SpudParser.AtholdContext):
                self._handle_athold(child,context)
            elif isinstance(child,SpudParser.AtholdunitContext):
                self._handle_atholdunit(child,context)
            elif isinstance(child,SpudParser.AtdecContext):
                self._handle_atdec(child,context)
            elif isinstance(child,SpudParser.AtfracContext):
                self._handle_atfrac(child,context)
            elif isinstance(child,SpudParser.AtsectionContext):
                self._handle_atsection(child,context)
    def _handle_line(self,tree,context):
        # tree is a SpudParser.LineContext
        if tree.children is None:
            return
        for child in tree.children:
            if isinstance(child,SpudParser.LineingredientContext):
                self._handle_lineingredient(child,context)
            elif isinstance(child,SpudParser.LinestandardruleContext):
                self._handle_linestandardrule(child,context)
            elif isinstance(child,SpudParser.LineatContext):
                self._handle_lineat(child,context)
    def _handle_spud(self,tree):
        # tree is a SpudParser.SpudContext
        if tree.children is None:
            return
        for child in tree.children:
            if isinstance(child,SpudParser.LineContext):
                self._handle_line(child,{})
    def recursive_load_parse(self,abs_path):
        # abs_path is a string with the absolute file path to load
        tree = self.get_tree(abs_path)
        if tree is None:
            return
        imports = []
        self.extract_imports(imports,tree)
        for statement in imports:
            self.recursive_load_parse(self.resolve_import_path(
                os.path.dirname(abs_path),
                statement
            ))
        self._handle_spud(tree)

x = SpudLoader()
x.recursive_load_parse("../tests/test_dir/main.spud")