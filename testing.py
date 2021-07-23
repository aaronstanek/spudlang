import unittest

from MyNumber import MyNumber
from Ingredient import Ingredient
from Pattern import Pattern, SinglePattern, DoublePattern
from RuleOutput import (
    NoneRuleOutputInstance, RenamingRuleOutput,
    PrefixingRuleOutput, InsertingRuleOutput,
    SingleConvertingRuleOutput, DoubleConvertingRuleOutput,
    PropertiesRuleOutput,
    DecRuleOutputInstance, FracRuleOutputInstance
    )

class TestMyNumber(unittest.TestCase):

    def test_creation(self):
        a = MyNumber((5,1))
        self.assertTrue(a.is_fraction)
        self.assertEqual(str(a),"5")
        a = MyNumber(13.4)
        self.assertFalse(a.is_fraction)
        self.assertEqual(str(a),"13.4")
        a = MyNumber((3,7))
        self.assertTrue(a.is_fraction)
        self.assertEqual(str(a),"3/7")
        a = MyNumber((7,3))
        self.assertTrue(a.is_fraction)
        self.assertEqual(str(a),"2 1/3")

    def test_as_float(self):
        a = MyNumber((5,2))
        b = a.as_float()
        self.assertEqual(type(b),MyNumber)
        self.assertFalse(b.is_fraction)
        self.assertEqual(b.value,2.5)
    
    def test_as_fraction(self):
        a = MyNumber(6/7)
        b = a.as_fraction(10)
        self.assertEqual(type(b),MyNumber)
        self.assertTrue(b.is_fraction)
        self.assertEqual(b.value,(6,7))

    def test_as_fraction_advanced(self):
        a = MyNumber(13/9)
        b = a.as_fraction(10)
        self.assertEqual(b.value,(13,9))
        a = MyNumber(99/100)
        self.assertEqual(a.as_fraction(100).value,(99,100))
        self.assertEqual(a.as_fraction(600).value,(99,100))
        a = MyNumber((85,64))
        self.assertEqual(a.as_fraction(64).value,(85,64))
        self.assertEqual(a.as_fraction(500).value,(85,64))
    
    def test_addition_fractions(self):
        a = MyNumber((13,9))
        b = MyNumber((7,9))
        c = a + b
        self.assertEqual(type(c),MyNumber)
        self.assertTrue(c.is_fraction)
        self.assertEqual(c.value,(20,9))
        a = MyNumber((13,9))
        b = MyNumber((7,8))
        c = a + b
        self.assertEqual(type(c),MyNumber)
        self.assertTrue(c.is_fraction)
        self.assertEqual(c.value,(167,72))
        a = MyNumber((3,6))
        b = MyNumber((7,8))
        c = a + b
        self.assertEqual(type(c),MyNumber)
        self.assertTrue(c.is_fraction)
        self.assertEqual(c.value,(11,8))
    
    def test_addition_float(self):
        a = MyNumber((13,9))
        b = MyNumber(4.0)
        c = a + b
        self.assertEqual(type(c),MyNumber)
        self.assertFalse(c.is_fraction)
        self.assertTrue(abs(c.value - 5.444) < 0.01)
        c = b + a
        self.assertEqual(type(c),MyNumber)
        self.assertFalse(c.is_fraction)
        self.assertTrue(abs(c.value - 5.444) < 0.01)
        a = MyNumber(11.93)
        b = MyNumber(8.43)
        c = a + b
        self.assertEqual(type(c),MyNumber)
        self.assertFalse(c.is_fraction)
        self.assertTrue(abs(c.value - 20.36) < 0.01)

    def test_multiplication_fraction(self):
        a = MyNumber((13,9))
        b = MyNumber((7,9))
        c = a * b
        self.assertEqual(type(c),MyNumber)
        self.assertTrue(c.is_fraction)
        self.assertEqual(c.value,(91,81))
        a = MyNumber((13,9))
        b = MyNumber((7,8))
        c = a * b
        self.assertEqual(type(c),MyNumber)
        self.assertTrue(c.is_fraction)
        self.assertEqual(c.value,(91,72))
        a = MyNumber((3,6))
        b = MyNumber((7,8))
        c = a * b
        self.assertEqual(type(c),MyNumber)
        self.assertTrue(c.is_fraction)
        self.assertEqual(c.value,(7,16))

    def test_multiplication_float(self):
        a = MyNumber((13,9))
        b = MyNumber(4.0)
        c = a * b
        self.assertEqual(type(c),MyNumber)
        self.assertFalse(c.is_fraction)
        self.assertTrue(abs(c.value - 5.777) < 0.01)
        c = b * a
        self.assertEqual(type(c),MyNumber)
        self.assertFalse(c.is_fraction)
        self.assertTrue(abs(c.value - 5.777) < 0.01)
        a = MyNumber(11.93)
        b = MyNumber(8.43)
        c = a * b
        self.assertEqual(type(c),MyNumber)
        self.assertFalse(c.is_fraction)
        self.assertTrue(abs(c.value - 100.57) < 0.01)

    def test_multiplicative_inverse(self):
        a = MyNumber((13,9))
        b = a.multiplicative_inverse()
        self.assertEqual(type(b),MyNumber)
        self.assertTrue(b.is_fraction)
        self.assertEqual(b.value,(9,13))
        a = MyNumber(2.0)
        b = a.multiplicative_inverse()
        self.assertEqual(type(b),MyNumber)
        self.assertFalse(b.is_fraction)
        self.assertEqual(b.value,0.5)

    def test_from_string(self):
        a = MyNumber.from_string("3")
        self.assertEqual(type(a),MyNumber)
        self.assertTrue(a.is_fraction)
        self.assertEqual(a.value,(3,1))
        a = MyNumber.from_string("3.0")
        self.assertEqual(type(a),MyNumber)
        self.assertFalse(a.is_fraction)
        self.assertEqual(a.value,3.0)
        a = MyNumber.from_string("3/4")
        self.assertEqual(type(a),MyNumber)
        self.assertTrue(a.is_fraction)
        self.assertEqual(a.value,(3,4))
        a = MyNumber.from_string("3 1/2")
        self.assertEqual(type(a),MyNumber)
        self.assertTrue(a.is_fraction)
        self.assertEqual(a.value,(7,2))

class TestPattern(unittest.TestCase):

    def test_ingredient_creation(self):
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        self.assertEqual(type(a),Ingredient)
        with self.assertRaises(Exception):
            Ingredient(MyNumber((5,1)),[],[],set())
    
    def test_pattern_creation(self):
        with self.assertRaises(Exception):
            Pattern()

    def test_compare_true(self):
        sample = ["pepper","bell","red"]
        rules = [["pepper"],["bell"],["red"]]
        for rule_n in range(len(rules)):
            rule = rules[rule_n]
            self.assertEqual(Pattern._compare(rule,sample),rule_n)
        rules = [["pepper","bell"],["bell","red"]]
        for rule_n in range(len(rules)):
            rule = rules[rule_n]
            self.assertEqual(Pattern._compare(rule,sample),rule_n)
        rule = sample
        self.assertEqual(Pattern._compare(rule,sample),0)

    def test_compare_false(self):
        sample = ["pepper","bell","red"]
        rule = ["radish"]
        self.assertEqual(Pattern._compare(rule,sample),None)
        rule = ["pepper","radish"]
        self.assertEqual(Pattern._compare(rule,sample),None)
        rule = ["red","very"]
        self.assertEqual(Pattern._compare(rule,sample),None)
        rule = ["veg","pepper","bell","red","very"]
        self.assertEqual(Pattern._compare(rule,sample),None)
    
    def test_single_pattern_true(self):
        with self.assertRaises(Exception):
            SinglePattern(None,{})
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        b = SinglePattern(None,{"chopped":True})
        self.assertEqual(b.matches(a),(2,-1))
        self.assertEqual(b.specificity,1)
        b = SinglePattern(None,{"minced":False})
        self.assertEqual(b.matches(a),(2,-1))
        self.assertEqual(b.specificity,1)
        b = SinglePattern(["bell"],{})
        self.assertEqual(b.matches(a),(2,1))
        self.assertEqual(b.specificity,1)
        b = SinglePattern(["bell","red"],{"chopped":True})
        self.assertEqual(b.matches(a),(2,1))
        self.assertEqual(b.specificity,3)
        b = SinglePattern(["pepper"],{"minced":False})
        self.assertEqual(b.matches(a),(2,0))
        self.assertEqual(b.specificity,2)
        b = SinglePattern(["count"],{})
        self.assertEqual(b.matches(a),(1,0))
        self.assertEqual(b.specificity,1)

    def test_single_pattern_false(self):
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        b = SinglePattern(["count"],{"minced":False,"chopped":True})
        self.assertEqual(b.matches(a),(0,None))
        b = SinglePattern(["bell","pepper"],{})
        self.assertEqual(b.matches(a),(0,None))
        b = SinglePattern(["pepper","bell","red"],{"chopped":False})
        self.assertEqual(b.matches(a),(0,None))
        b = SinglePattern(["count"],{"chopped":False})
        self.assertEqual(b.matches(a),(0,None))

    def test_double_pattern_true(self):
        with self.assertRaises(Exception):
            DoublePattern(None,None,{})
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        b = DoublePattern(["count"],["pepper","bell"],{})
        self.assertEqual(b.matches(a),(1,0,0))
        self.assertEqual(b.specificity,3)
        b = DoublePattern(None,["red"],{"minced":False})
        self.assertEqual(b.matches(a),(1,-1,2))
        self.assertEqual(b.specificity,2)
        b = DoublePattern(["count"],None,{"minced":False,"chopped":True})
        self.assertEqual(b.matches(a),(1,0,-1))
        self.assertEqual(b.specificity,3)
        b = DoublePattern(["count"],["pepper"],{})
        self.assertEqual(b.matches(a),(1,0,0))
        self.assertEqual(b.specificity,2)
        b = DoublePattern(None,None,{"minced":False,"chopped":True})
        self.assertEqual(b.matches(a),(1,-1,-1))
        self.assertEqual(b.specificity,2)
    
    def test_double_pattern_false(self):
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        b = DoublePattern(["count"],["bell","pepper"],{})
        self.assertEqual(b.matches(a),(0,None,None))
        b = DoublePattern(None,["red"],{"chopped":False,"minced":True})
        self.assertEqual(b.matches(a),(0,None,None))
        b = DoublePattern(["count"],["much","pepper"],{})
        self.assertEqual(b.matches(a),(0,None,None))
        b = DoublePattern(["g","count"],["pepper","bell","red"],{"chopped":True})
        self.assertEqual(b.matches(a),(0,None,None))

class TestRuleOutput(unittest.TestCase):

    def test_none(self):
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        b = NoneRuleOutputInstance.apply(a,(None,None))
        self.assertTrue(b is a)
    
    def test_rename(self):
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        b = RenamingRuleOutput(["carrot"])
        c = b.apply(a,(2,1))
        self.assertEqual(c.name,["pepper","carrot"])
        self.assertEqual(a.name,["pepper","bell","red"])
        self.assertEqual(str(c.count),"5")
        self.assertEqual(c.unit,["count"])
        self.assertEqual(c.props,{"chopped"})
        b = RenamingRuleOutput(["kg"])
        c = b.apply(a,(1,0))
        self.assertEqual(str(c.count),"5")
        self.assertEqual(c.unit,["kg"])
        self.assertEqual(a.unit,["count"])
        self.assertEqual(c.name,["pepper","bell","red"])
        self.assertEqual(c.props,{"chopped"})
        b = RenamingRuleOutput(["black","ground"])
        c = b.apply(a,(2,1))
        self.assertEqual(str(c.count),"5")
        self.assertEqual(c.name,["pepper","black","ground"])
        self.assertEqual(a.name,["pepper","bell","red"])
        self.assertEqual(c.unit,["count"])
        self.assertEqual(c.props,{"chopped"})

    def test_prefix(self):
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        b = PrefixingRuleOutput(["metric"])
        c = b.apply(a,(2,1))
        self.assertTrue(c is a)
        c = b.apply(a,(1,0))
        self.assertEqual(str(c.count),"5")
        self.assertEqual(c.unit,["metric","count"])
        self.assertEqual(a.unit,["count"])
        self.assertEqual(c.name,["pepper","bell","red"])
        self.assertEqual(c.props,{"chopped"})
        b = PrefixingRuleOutput(["food","vegetable"])
        c = b.apply(a,(2,0))
        self.assertEqual(str(c.count),"5")
        self.assertEqual(c.name,["food","vegetable","pepper","bell","red"])
        self.assertEqual(a.name,["pepper","bell","red"])
        self.assertEqual(c.unit,["count"])
        self.assertEqual(c.props,{"chopped"})

    def test_insert(self):
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        b = InsertingRuleOutput(1,["fire"])
        c = b.apply(a,(2,1))
        self.assertEqual(str(c.count),"5")
        self.assertEqual(c.name,["pepper","fire","red"])
        self.assertEqual(a.name,["pepper","bell","red"])
        self.assertEqual(c.unit,["count"])
        self.assertEqual(c.props,{"chopped"})
        b = InsertingRuleOutput(1,["banana","cabbage","watermelon"])
        c = b.apply(a,(2,1))
        self.assertEqual(str(c.count),"5")
        self.assertEqual(c.name,["pepper","banana","cabbage","watermelon","red"])
        self.assertEqual(a.name,["pepper","bell","red"])
        self.assertEqual(c.unit,["count"])
        self.assertEqual(c.props,{"chopped"})
        b = InsertingRuleOutput(1,[])
        c = b.apply(a,(2,1))
        self.assertEqual(str(c.count),"5")
        self.assertEqual(c.name,["pepper","red"])
        self.assertEqual(a.name,["pepper","bell","red"])
        self.assertEqual(c.unit,["count"])
        self.assertEqual(c.props,{"chopped"})
        b = InsertingRuleOutput(1,["banana","cabbage","watermelon"])
        c = b.apply(a,(1,0))
        self.assertEqual(str(c.count),"5")
        self.assertEqual(c.name,["pepper","bell","red"])
        self.assertEqual(a.name,["pepper","bell","red"])
        self.assertEqual(c.unit,["banana","cabbage","watermelon"])
        self.assertEqual(c.props,{"chopped"})

    def test_single_convert(self):
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        b = SingleConvertingRuleOutput(MyNumber((5,2)),["black"])
        c = b.apply(a,(2,1))
        self.assertEqual(str(c.count),"12 1/2")
        self.assertEqual(c.unit,["count"])
        self.assertEqual(c.name,["pepper","black"])
        self.assertEqual(c.props,{"chopped"})
        self.assertEqual(str(a.count),"5")
        self.assertEqual(a.name,["pepper","bell","red"])

    def test_double_convert(self):
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        b = DoubleConvertingRuleOutput(MyNumber((4,5)),["cup"],None)
        c = b.apply(a,(1,0,-1))
        self.assertEqual(str(c.count),"4")
        self.assertEqual(c.unit,["cup"])
        self.assertEqual(c.name,["pepper","bell","red"])
        self.assertEqual(c.props,{"chopped"})
        b = DoubleConvertingRuleOutput(None,["pound"],["green"])
        c = b.apply(a,(1,-1,2))
        self.assertEqual(str(c.count),"5")
        self.assertEqual(c.unit,["pound"])
        self.assertEqual(c.name,["pepper","bell","green"])
        self.assertEqual(c.props,{"chopped"})

    def test_prop(self):
        a = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        b = PropertiesRuleOutput(NoneRuleOutputInstance,[
            ("minced",True),("chopped",False),("cheesey",False),("slimey",True)
        ])
        c = b.apply(a,(None,None))
        self.assertEqual(str(c.count),"5")
        self.assertEqual(c.unit,["count"])
        self.assertEqual(c.name,["pepper","bell","red"])
        self.assertEqual(c.props,{"minced","slimey"})
        self.assertEqual(a.props,{"chopped"})
    
    def test_dec(self):
        a = Ingredient(MyNumber((11,2)),["count"],["pepper","bell","red"],{"chopped"})
        c = DecRuleOutputInstance.apply(a,(None,None))
        self.assertEqual(str(c.count),"5.5")
        self.assertEqual(c.unit,["count"])
        self.assertEqual(c.name,["pepper","bell","red"])
        self.assertEqual(c.props,{"chopped"})
        self.assertEqual(str(a.count),"5 1/2")

    def test_frac(self):
        a = Ingredient(MyNumber(5.5),["count"],["pepper","bell","red"],{"chopped"})
        c = FracRuleOutputInstance.apply(a,(None,None))
        self.assertEqual(str(c.count),"5 1/2")
        self.assertEqual(c.unit,["count"])
        self.assertEqual(c.name,["pepper","bell","red"])
        self.assertEqual(c.props,{"chopped"})
        self.assertEqual(str(a.count),"5.5")
    
    def test_priority(self):
        a = NoneRuleOutputInstance
        b = DecRuleOutputInstance
        c = FracRuleOutputInstance
        self.assertEqual(a.priority(),b.priority())
        self.assertEqual(a.priority(),c.priority())
        b = RenamingRuleOutput(["hi"])
        c = InsertingRuleOutput(1,["hi"])
        self.assertLess(a.priority(),b.priority())
        self.assertLess(a.priority(),c.priority())
        self.assertEqual(b.priority(),c.priority())
        a = PrefixingRuleOutput(["hi"])
        self.assertLess(b.priority(),a.priority())
        self.assertLess(c.priority(),a.priority())
        b = SingleConvertingRuleOutput(MyNumber(1.0),["hi"])
        c = DoubleConvertingRuleOutput(MyNumber(1.0),["hi"],["hi"])
        self.assertLess(a.priority(),b.priority())
        self.assertLess(a.priority(),c.priority())
        self.assertEqual(b.priority(),c.priority())

if __name__ == '__main__':
    unittest.main()