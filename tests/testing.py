import unittest
import sys
sys.path.append("../src")

from spudlang.MyNumber import MyNumber
from spudlang.Ingredient import Ingredient
from spudlang.Pattern import Pattern, SinglePattern, DoublePattern
from spudlang.RuleOutput import (
    NoneRuleOutputInstance, RenamingRuleOutput,
    PrefixingRuleOutput, InsertingRuleOutput,
    SingleConvertingRuleOutput, DoubleConvertingRuleOutput,
    PropertiesRuleOutput,
    DecRuleOutputInstance, FracRuleOutputInstance
    )
from spudlang.Rule import Rule, HoldRule, RuleBox

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
        a = MyNumber(1.6666666666)
        self.assertEqual(a.as_fraction(10).value,(5,3))
    
    def test_comparison(self):
        # lt
        self.assertTrue( MyNumber((8,9)) < MyNumber(1.0) )
        self.assertTrue( MyNumber(1.1) < MyNumber((3,2)) )
        self.assertFalse( MyNumber((5,2)) < MyNumber(2.5) )
        self.assertFalse( MyNumber(1.0) < MyNumber((8,9)) )
        self.assertFalse( MyNumber((3,2)) < MyNumber(1.1) )
        self.assertFalse( MyNumber(2.5) < MyNumber((5,2)) )
        # le
        self.assertTrue( MyNumber((8,9)) <= MyNumber(1.0) )
        self.assertTrue( MyNumber(1.1) <= MyNumber((3,2)) )
        self.assertTrue( MyNumber((5,2)) <= MyNumber(2.5) )
        self.assertFalse( MyNumber(1.0) <= MyNumber((8,9)) )
        self.assertFalse( MyNumber((3,2)) <= MyNumber(1.1) )
        self.assertTrue( MyNumber(2.5) <= MyNumber((5,2)) )
        # gt
        self.assertFalse( MyNumber((8,9)) > MyNumber(1.0) )
        self.assertFalse( MyNumber(1.1) > MyNumber((3,2)) )
        self.assertFalse( MyNumber((5,2)) > MyNumber(2.5) )
        self.assertTrue( MyNumber(1.0) > MyNumber((8,9)) )
        self.assertTrue( MyNumber((3,2)) > MyNumber(1.1) )
        self.assertFalse( MyNumber(2.5) > MyNumber((5,2)) )
        # ge
        self.assertFalse( MyNumber((8,9)) >= MyNumber(1.0) )
        self.assertFalse( MyNumber(1.1) >= MyNumber((3,2)) )
        self.assertTrue( MyNumber((5,2)) >= MyNumber(2.5) )
        self.assertTrue( MyNumber(1.0) >= MyNumber((8,9)) )
        self.assertTrue( MyNumber((3,2)) >= MyNumber(1.1) )
        self.assertTrue( MyNumber(2.5) >= MyNumber((5,2)) )
    
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
        a = NoneRuleOutputInstance
        b = PropertiesRuleOutput(NoneRuleOutputInstance,[("yes",True)])
        c = PropertiesRuleOutput(c,[("hi",True)])
        self.assertEqual(a.priority(),b.priority())
        self.assertLess(b.priority(),c.priority())

class TestRule(unittest.TestCase):

    def test_rule(self):
        # the Rule class is transparent enough
        # that it should trivially work
        # but we should test an example anyway
        a = SinglePattern(["bell"],{"chopped":True})
        b = RenamingRuleOutput(["spicy"])
        c = PropertiesRuleOutput(InsertingRuleOutput(1,["crunch","turnip"]),[("chopped",False),("watered",True)])
        d = Rule(a,[b,c])
        ig = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        match_token = d.matches(ig)
        self.assertEqual(type(match_token),tuple)
        self.assertEqual(match_token,(2,1))
        results = d.apply(ig,match_token)
        self.assertEqual(type(results),list)
        self.assertEqual(len(results),2)
        self.assertEqual(str(results[0].count),"5")
        self.assertEqual(results[0].unit,["count"])
        self.assertEqual(results[0].name,["pepper","spicy"])
        self.assertEqual(results[0].props,{"chopped"})
        self.assertEqual(str(results[1].count),"5")
        self.assertEqual(results[1].unit,["count"])
        self.assertEqual(results[1].name,["pepper","crunch","turnip","red"])
        self.assertEqual(results[1].props,{"watered"})
        self.assertEqual(type(d.priority()),int)
        self.assertTrue(d.priority()>=0)
        self.assertEqual(type(d.specificity()),int)
        self.assertTrue(d.specificity()>=0)
    
    def test_hold_rule(self):
        a = SinglePattern(["bell"],{"chopped":True})
        b = HoldRule(a,99)
        self.assertTrue(isinstance(b,Rule))
        self.assertEqual(b.priority(),99)

    def test_rule_box(self):
        # we will do a simple example to make sure that
        # something at least works
        A = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        box = RuleBox()
        # $+chopped-fresh is $+fresh
        box.add(Rule(
            SinglePattern(None,{"chopped":True,"fresh":False}),
            [PropertiesRuleOutput(NoneRuleOutputInstance,[("fresh",True)])]
            ))
        output_array = []
        box.resolve(output_array,A)
        self.assertEqual(len(output_array),1)
        self.assertEqual(type(output_array[0]),Ingredient)
        self.assertEqual(str(output_array[0].count),"5")
        self.assertEqual(output_array[0].unit,["count"])
        self.assertEqual(output_array[0].name,["pepper","bell","red"])
        self.assertEqual(output_array[0].props,{"chopped","fresh"})
    
    def test_rule_box2(self):
        # more advanced test to make sure that rules
        # are applied in order
        A = Ingredient(MyNumber((5,1)),["count"],["pepper","bell","red"],{"chopped"})
        box = RuleBox()
        # $+pepper.bell is pepper.black+fresh+ground
        # run second
        box.add(Rule(
            SinglePattern(["pepper","bell"],{}),
            [
                PropertiesRuleOutput(
                    RenamingRuleOutput(["pepper","black"]),
                    [("fresh",True),("ground",True)]
                    )
            ]
        ))
        # $+chopped-fresh is $+fresh
        # run first
        box.add(Rule(
            SinglePattern(None,{"chopped":True,"fresh":False}),
            [PropertiesRuleOutput(NoneRuleOutputInstance,[("fresh",True)])]
            ))
        # 1 kg $ is 1000 g $
        # not run
        box.add(Rule(
            SinglePattern(["kg"],{}),
            [SingleConvertingRuleOutput(MyNumber((1000,1)),["g"])]
        ))
        # 1 count pepper is $ cup $
        # run third
        box.add(Rule(
            DoublePattern(["count"],["pepper"],{}),
            [DoubleConvertingRuleOutput(None,["cup"],None)]
        ))
        # cup is an imperial
        # does not get run
        box.add(Rule(
            SinglePattern(["cup"],{}),
            [PrefixingRuleOutput(["imperial"])]
        ))
        # hold after reaching cup pepper+ground
        box.add(HoldRule(
            DoublePattern(["cup"],["pepper"],{"ground":True}),
            0
        ))
        # do it
        output_array = []
        box.resolve(output_array,A,dict())
        self.assertEqual(len(output_array),1)
        r = output_array[0]
        self.assertEqual(type(r),Ingredient)
        self.assertEqual(str(r.count),"5")
        self.assertEqual(r.unit,["cup"])
        self.assertEqual(r.name,["pepper","black"])
        self.assertEqual(r.props,{"chopped","fresh","ground"})

if __name__ == '__main__':
    unittest.main()