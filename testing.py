import unittest

from MyNumber import MyNumber
from Ingredient import Ingredient
from Pattern import Pattern, SinglePattern, DoublePattern
from RuleOutput import NoneRuleOutput, RenamingRuleOutput, PrefixingRuleOutput, PropertiesRuleOutput

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
        b = NoneRuleOutput.apply(a,(None,None))
        self.assertTrue(b is a)

if __name__ == '__main__':
    unittest.main()