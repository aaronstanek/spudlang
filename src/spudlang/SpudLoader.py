# defines the SpudLoader class
# to load and parse source files

import os
import hashlib
from copy import copy
from .SourceVersionCheck import source_version_check
import antlr4
from antlr4.error.ErrorListener import ErrorListener
from .Pattern import SinglePattern, DoublePattern
from .Rule import Rule, HoldRule
from .RuleOutput import (
    RenamingRuleOutput, PrefixingRuleOutput, InsertingRuleOutput,
    SingleConvertingRuleOutput, DoubleConvertingRuleOutput,
    DecRuleOutputInstance, FracRuleOutputInstance, PropertiesRuleOutput)
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
    def load_file_raw(path,force):
        # force indicates if we need to read from the hard drive
        # force is a bool. True means load outside the normal import system
        # if True, we are loading a spud file
        # if False, we are loading a spudh file
        if force:
            expect = ".spud"
            alt = ".spudh"
        else:
            expect = ".spudh"
            alt = ".spud"
        if path[-len(expect):] != expect:
            if path[-len(alt):] != alt:
                path = path + expect
            else:
                if force:
                    raise Exception("Tried to run file " + path + " as type .spud")
                else:
                    raise Exception("Tried to import file " + path + " as type .spudh")
        # we now have the correct file type
        if os.path.isfile(path):
            with open(path,"rb") as file:
                return file.read()
        elif os.path.isfile(path[:-len(expect)] + alt):
            raise Exception("Unable to locate file: "+path+" Please check file type.")
        else:
            raise Exception("Unable to locate file: "+path)
    def get_tree(self,abs_path,force):
        # abs_path is a string with the absolute file path to load
        # force is a bool. True means load outside the normal import system
        # returns either the syntax tree for the source file
        # or None
        raw = self.load_file_raw(abs_path,force)
        if not force:
            file_hash = hashlib.sha256(raw).digest()
            if file_hash in self.seen:
                # we have seen this file before
                return None
            else:
                # we have not seen this file before
                # register it so that we do not
                # need to process it again
                self.seen.add(file_hash)
        # check the source version to make sure
        # that it's compatible with this grammar
        try:
            version_compat = source_version_check(raw)
        except:
            raise Exception("Malformed version information in file: "+abs_path)
        if not version_compat[0]:
            raise Exception("Incompatible source version in file: "+abs_path+". Error Message: "+version_compat[1])
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
                return (text,sign)
            elif text == "$":
                return (text,sign)
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
            props.append(self._handle_all_prop_elements(child,context))
        return props
    @staticmethod
    def _props_conversion(props_in):
        # props_in is list(tuple(str,bool))
        # we will output the same information
        # in dict(str->bool)
        props_out = {}
        for element in props_in:
            props_out[element[0]] = element[1]
        return props_out
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
            return self._handle_name_and_props(tree.children[0],context)
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
            number = MyNumber.one
            unit = ["mealsworth"]
        elif unit is None:
            # unit is None
            # but number is defined
            unit = ["count"]
        if "multiply" in context:
            number = number * context["multiply"]
        self.ingredients.append( Ingredient(number,unit,name,props) )
    def _handle_rule_side_simple(self,tree,context):
        # tree is SpudParser.RuleleftsimpleContext
        # or SpudParser.RulerightsimpleContext
        # or SpudParser.Rulerightsimplewild
        # returns list of (name,props) tuples
        output = []
        for child in tree.children:
            if isinstance(child,(
                    SpudParser.PownamewithpropsContext,
                    SpudParser.BasicnamewithpropswildContext,
                    SpudParser.BasicwildwithpropsContext)):
                output.append(self._handle_name_and_props(child,context))
        return output
    def _handle_line_renaming_prefixing(self,tree,context,output_type):
        # tree is SpudParser.LinerenamingContext
        # or SpudParser.LineprefixingContext
        # output_type is either RenamingRuleOutput or PrefixingRuleOutput
        for child in tree.children:
            if isinstance(child,SpudParser.RuleleftsimpleContext):
                left = self._handle_rule_side_simple(child,context)
            elif isinstance(child,SpudParser.RulerightsimplewildContext):
                right = self._handle_rule_side_simple(child,context)
        for i in range(len(right)):
            ro = output_type(right[i][0])
            if len(right[i][1]) != 0:
                ro = PropertiesRuleOutput(ro,right[i][1])
            right[i] = ro
        for i in range(len(left)):
            pattern = SinglePattern(left[i][0],self._props_conversion(left[i][1]))
            self.rules.append(Rule(pattern,right))
    def _handle_lineinserting(self,tree,context):
        # tree is SpudParser.LineinsertingContext
        for child in tree.children:
            if isinstance(child,SpudParser.RuleleftsimpleContext):
                left = self._handle_rule_side_simple(child,context)
            elif isinstance(child,SpudParser.RulerightsimpleContext):
                right = self._handle_rule_side_simple(child,context)
        for i in range(len(left)):
            pattern = SinglePattern(left[i][0],self._props_conversion(left[i][1]))
            pattern_size = len(left[i][0])
            outputs = []
            for j in range(len(right)):
                ro = InsertingRuleOutput(pattern_size,right[j][0])
                if len(right[j][1]) != 0:
                    ro = PropertiesRuleOutput(ro,right[j][1])
                outputs.append(ro)
            self.rules.append(Rule(pattern,outputs))
    def _handle_singleconvertingleftelem(self,tree,context):
        # tree is SpudParser.SingleconvertingleftelemContext
        for child in tree.children:
            if isinstance(child,SpudParser.NumberContext):
                number = MyNumber.from_tree(child)
            elif isinstance(child,SpudParser.PownamewithpropsContext):
                name, props = self._handle_name_and_props(child,context)
                return (number,name,props)
    def _handle_singleconvertingrightelem(self,tree,context):
        # tree is SpudParser.SingleconvertingrightelemContext
        for child in tree.children:
            if isinstance(child,SpudParser.NumberContext):
                number = MyNumber.from_tree(child)
            elif isinstance(child,antlr4.tree.Tree.TerminalNodeImpl):
                if child.getText() == "$":
                    return None # ignore this otherwise
            elif isinstance(child,SpudParser.BasicwildwithpropsContext):
                name, props = self._handle_name_and_props(child,context)
                return (number,name,props)
    def _handle_singleconvertingleft(self,tree,context):
        # tree is SpudParser.SingleconvertingleftContext
        patterns = []
        for child in tree.children:
            if isinstance(child,SpudParser.SingleconvertingleftelemContext):
                patterns.append(self._handle_singleconvertingleftelem(child,context))
        return patterns
    def _handle_singleconvertingright(self,tree,context):
        # tree is SpudParser.SingleconvertingrightContext
        outputs = []
        for child in tree.children:
            if isinstance(child,SpudParser.SingleconvertingrightelemContext):
                outputs.append(self._handle_singleconvertingrightelem(child,context))
        return outputs
    def _handle_linesingleconverting(self,tree,context):
        # tree is SpudParser.LinesingleconvertingContext
        for child in tree.children:
            if isinstance(child,SpudParser.SingleconvertingleftContext):
                left = self._handle_singleconvertingleft(child,context)
            elif isinstance(child,SpudParser.SingleconvertingrightContext):
                right = self._handle_singleconvertingright(child,context)
        for i in range(len(left)):
            # left[i][0] is the number, not None
            # left[i][1] is the name
            # left[i][2] is the props
            denominator = left[i][0].multiplicative_inverse()
            pattern = SinglePattern(left[i][1],self._props_conversion(left[i][2]))
            outputs = []
            for j in range(len(right)):
                # elements of right are (number,name,props)
                # number may be None
                if right[j][0] is None:
                    ratio = MyNumber.one
                else:
                    ratio = denominator * right[j][0]
                ro = SingleConvertingRuleOutput(ratio,right[j][1])
                if len(right[j][2]) != 0:
                    ro = PropertiesRuleOutput(ro,right[j][2])
                outputs.append(ro)
            self.rules.append(Rule(pattern,outputs))
    def _handle_doubleconvertingleftsub_1_2(self,tree,context):
        # tree is SpudParser.Doubleconvertingleftsub1Context
        # or SpudParser.Doubleconvertingleftsub2Context
        for child in tree.children:
            if isinstance(child,antlr4.tree.Tree.TerminalNodeImpl):
                if child.getText() == "$":
                    unit = None
                    continue
            if isinstance(child,SpudParser.PownameContext):
                unit = self._handle_all_names(child,context)
            elif isinstance(child,
                (SpudParser.PownamewithpropsContext,
                SpudParser.PowwildwithpropsContext)):
                    name, props = self._handle_name_and_props(child,context)
                    return unit, name, props
    def _handle_doubleconvertingleftelem(self,tree,context):
        # tree is SpudParser.DoubleconvertingleftelemContext
        for child in tree.children:
            if isinstance(child,SpudParser.NumberContext):
                number = MyNumber.from_tree(child)
            elif isinstance(child,
                (SpudParser.Doubleconvertingleftsub1Context,
                SpudParser.Doubleconvertingleftsub2Context)):
                    unit, name, props = self._handle_doubleconvertingleftsub_1_2(child,context)
                    return (number,unit,name,props)
    def _handle_doubleconvertingrightelem(self,tree,context):
        # tree is SpudParser.DoubleconvertingrightelemContext
        is_number_seen = False
        for child in tree.children:
            if isinstance(child,antlr4.tree.Tree.TerminalNodeImpl):
                if child.getText() == "$": # ignore otherwise
                    # but may be number or unit
                    # depending on context
                    if is_number_seen:
                        # it is the unit
                        unit = None
                    else:
                        # it is the number
                        is_number_seen = True
                        number = None
            elif isinstance(child,SpudParser.NumberContext):
                is_number_seen = True
                number = MyNumber.from_tree(child)
            elif isinstance(child,SpudParser.BasicnameContext):
                unit = self._handle_all_names(child,context)
            elif isinstance(child,SpudParser.BasicwildwithpropsContext):
                name, props = self._handle_name_and_props(child,context)
                return (number,unit,name,props)
    def _handle_doubleconvertingleft(self,tree,context):
        # tree is SpudParser.DoubleconvertingleftContext
        patterns = []
        for child in tree.children:
            if isinstance(child,SpudParser.DoubleconvertingleftelemContext):
                patterns.append(self._handle_doubleconvertingleftelem(child,context))
        return patterns
    def _handle_doubleconvertingright(self,tree,context):
        # tree is SpudParser.DoubleconvertingrightContext
        outputs = []
        for child in tree.children:
            if isinstance(child,SpudParser.DoubleconvertingrightelemContext):
                outputs.append(self._handle_doubleconvertingrightelem(child,context))
        return outputs
    def _handle_linedoubleconverting(self,tree,context):
        # tree is SpudParser.LinedoubleconvertingContext
        for child in tree.children:
            if isinstance(child,SpudParser.DoubleconvertingleftContext):
                left = self._handle_doubleconvertingleft(child,context)
            elif isinstance(child,SpudParser.DoubleconvertingrightContext):
                right = self._handle_doubleconvertingright(child,context)
        for i in range(len(left)):
            # left[i][0] is the number, not None
            # left[i][1] is the unit, may be None
            # left[i][2] is the name, may be None
            # left[i][3] is the props
            denominator = left[i][0].multiplicative_inverse()
            pattern = DoublePattern(left[i][1],left[i][2],self._props_conversion(left[i][3]))
            outputs = []
            for j in range(len(right)):
                if right[j][0] is None:
                    ratio = None
                else:
                    ratio = denominator * right[j][0]
                ro = DoubleConvertingRuleOutput(ratio,right[j][1],right[j][2])
                if len(right[j][3]) != 0:
                    ro = PropertiesRuleOutput(ro,right[j][3])
                outputs.append(ro)
            self.rules.append(Rule(pattern,outputs))
    def _handle_linestandardrule(self,tree,context):
        # tree is SpudParser.LinestandardruleContext
        for child in tree.children:
            if isinstance(child,SpudParser.LinerenamingContext):
                self._handle_line_renaming_prefixing(child,context,RenamingRuleOutput)
            elif isinstance(child,SpudParser.LineprefixingContext):
                self._handle_line_renaming_prefixing(child,context,PrefixingRuleOutput)
            elif isinstance(child,SpudParser.LineinsertingContext):
                self._handle_lineinserting(child,context)
            elif isinstance(child,SpudParser.LinesingleconvertingContext):
                self._handle_linesingleconverting(child,context)
            elif isinstance(child,SpudParser.LinedoubleconvertingContext):
                self._handle_linedoubleconverting(child,context)
    def _handle_atrun(self,tree,context):
        # tree is SpudParser.AtrunContext
        statement = tree.getText()
        # search and replace all @run with @import
        statement = "@import".join(statement.split("@run"))
        abs_path = self.resolve_import_path(context["BASE_DIR"],statement)
        self.recursive_load_parse(abs_path,True,context)
    def _handle_atsub1(self,tree,context):
        # tree is SpudPArser.Atsub1Context
        for child in tree.children:
            if isinstance(child,SpudParser.PownamewithpropsContext):
                name, props = self._handle_name_and_props(child,context)
                return DoublePattern(None,name,self._props_conversion(props))
    def _handle_atsub2(self,tree,context):
        # tree is SpudParser.Atsub2Context
        name = None
        props = {}
        for child in tree.children:
            if isinstance(child,SpudParser.PownameContext):
                unit = self._handle_all_names(child,context)
            elif isinstance(child,SpudParser.PowwildwithpropsContext):
                name, props = self._handle_name_and_props(child,context)
        return DoublePattern(unit,name,self._props_conversion(props))
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
    def _handle_atbeginmultiply(self,tree,context):
        # tree is SpudParser.AtbeginmultiplyContext
        for child in tree.children:
            if isinstance(child,SpudParser.NumberContext):
                value = MyNumber.from_tree(child)
                new_context = copy(context)
                if "multiply" in new_context:
                    value = new_context["multiply"] * value
                new_context["multiply"] = value
                return new_context
    def _handle_atbegin(self,tree,context):
        # tree is SpudParser.AtbeginContext
        # return a new context with updated values
        for child in tree.children:
            if isinstance(child,SpudParser.AtbeginisolateContext):
                # ignore all external forces
                return {"BASE_DIR":context["BASE_DIR"]}
            if isinstance(child,SpudParser.AtbeginmultiplyContext):
                return self._handle_atbeginmultiply(child,context)
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
            if isinstance(child,SpudParser.AtrunContext):
                self._handle_atrun(child,context)
            elif isinstance(child,SpudParser.AtholdContext):
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
    def _handle_spud(self,tree,context):
        # tree is a SpudParser.SpudContext
        if tree.children is None:
            return
        for child in tree.children:
            if isinstance(child,SpudParser.LineContext):
                self._handle_line(child,context)
    def recursive_load_parse(self,abs_path,force,context=None):
        # abs_path is a string with the absolute file path to load
        tree = self.get_tree(abs_path,force)
        if tree is None:
            return
        imports = []
        self.extract_imports(imports,tree)
        if context is None:
            context = {}
        else:
            context = copy(context)
        context["BASE_DIR"] = os.path.dirname(abs_path)
        for statement in imports:
            self.recursive_load_parse(self.resolve_import_path(
                    context["BASE_DIR"],
                    statement
                    ),
                False
                )
        self._handle_spud(tree,context)
