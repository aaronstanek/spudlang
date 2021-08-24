# defines the SpudLoader class
# to load and parse source files

import os
import hashlib
import antlr4
from antlr4.error.ErrorListener import ErrorListener
from .SpudLexer import SpudLexer
from .SpudParser import SpudParser

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
    def _handle_lineingredient(self,tree,context):
        raise NotImplemented
    def _handle_linestandardrule(self,tree,context):
        raise NotImplemented
    def _handle_athold(self,tree,context):
        raise NotImplemented
    def _handle_atholdunit(self,tree,context):
        raise NotImplemented
    def _handle_atdec(self,tree,context):
        raise NotImplemented
    def _handle_atfrac(self,tree,context):
        raise NotImplemented
    def _handle_atbegin(self,tree,context):
        raise NotImplemented
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