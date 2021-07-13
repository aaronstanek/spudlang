import unittest

from MyNumber import MyNumber

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

if __name__ == '__main__':
    unittest.main()