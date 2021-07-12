# defines a class MyNumber
# this can hold floating point numbers
# and fractions, and convert between
# then easily

import math

class MyNumber(object):
    def __init__(self,value):
        # value is either float
        # or tuple(int,int)
        if type(value) == float:
            if math.isnan(value) or math.isinf(value):
                raise ValueError("Expected value to be regular")
            if value < 0.0:
                raise ValueError("Expected value to be nonnegative")
            self.is_fraction = False
            self.value = value
        elif type(value) == tuple:
            if len(value) != 2:
                raise ValueError("Expected tuple to have length 2")
            if not all(map(lambda x: type(x) == int,value)):
                raise TypeError("Expected tuple to contain only int")
            if value[0] < 0:
                raise ValueError("Expected first int to be nonnegative")
            if value[1] < 1:
                raise ValueError("Expected second int to be greater than zero")
            self.is_fraction = True
            self.value = value
        else:
            raise TypeError("Expected float or tuple")
    def __str__(self):
        if self.is_fraction:
            whole = self.value[0] // self.value[1]
            part = self.value[0] % self.value[1]
            if whole == 0:
                if part == 0:
                    # the value is zero
                    return "0"
                else:
                    # it's a proper fraction
                    return str(part) + "/" + str(self.value[1])
            else:
                # it's an improper fraction
                if part == 0:
                    # it's a whole number
                    return str(whole)
                else:
                    # it's a true improper fraction
                    return str(whole) + " " + str(part) + "/" + str(self.value[1])
        else:
            return str(self.value)
    def as_float(self):
        if self.is_fraction:
            n = float(self.value[0]) / float(self.value[1])
            return MyNumber(n)
        else:
            return self
    def as_fraction(self,d):
        if self.is_fraction:
            return self
        # implements Farey sequence iteration
        if type(d) != int:
            raise TypeError("Expected d to be an int")
        if d < 1:
            raise ValueError("Expected d to be at least 1")
        whole = int(self.value)
        part = self.value - whole
        left = (0,1)
        right = (1,1)
        prev_best = left
        while True:
            now = (
                left[0] + right[0],
                left[1] + right[1]
            )
            if now[1] >= d:
                if now[1] == d:
                    return MyNumber(
                        (now[0]+whole*now[1],now[1])
                    )
                else:
                    return MyNumber(
                        (prev_best[0]+whole*prev_best[1],prev_best[1])
                    )
            # now[1] is too small
            f = float(now[0]) / float(now[1])
            if f == part:
                    return MyNumber(
                        (now[0]+whole*now[1],now[1])
                    )
            if f < part:
                # now is too small
                # it is the new lower bound
                left = now
            else:
                # now is too large
                # it is the new upper bound
                right = now
    def __add__(self,other):
        if type(other) != MyNumber:
            raise TypeError("Expected other to be of type MyNumber")
        if self.is_fraction and other.is_fraction:
            # both are fractions
            # if they have the same denominator
            # this is a bit easier
            if self.value[1] == other.value[1]:
                # same denominators
                # can just add numerators
                n = self.value[0] + other.value[0]
                return MyNumber((n,self.value[1]))
            else:
                # different denominators
                # need to convert
                d = self.value[1] * other.value[1]
                n = self.value[0] * other.value[1] + other.value[0] * self.value[1]
                gcd = math.gcd(d,n)
                d = d // gcd
                n = n // gcd
                return MyNumber((n,d))
        else:
            # at least one of the inputs is not a fraction
            # we will return a floating point number
            n = self.as_float().value + other.as_float().value
            return MyNumber(n)
    def __mul__(self,other):
        if type(other) != MyNumber:
            raise TypeError("Expected other to be of type MyNumber")
        if self.is_fraction and other.is_fraction:
            # both are fractions
            n = self.value[0] * other.value[0]
            d = self.value[1] * other.value[1]
            gcd = math.gcd(d,n)
            n = n // gcd
            d = d // gcd
            return MyNumber((n,d))
        else:
            # at least one is a floating-point number
            # return a floating-point number
            n = self.as_float().value * other.as_float().value
            return MyNumber(n)
    @staticmethod
    def from_string(s):
        if type(s) != str:
            raise TypeError("Expected s to be a string")
        # int is the most restrictive
        found = False
        try:
            n = int(s)
            found = True
        except:
            # it's not an integer
            pass
        if found:
            return MyNumber((n,1))
        # float is less restrictive
        try:
            n = float(s)
            found = True
        except:
            # it's not a float
            pass
        if found:
            return MyNumber(n)
        # we either have a fraction or garbage
        halves = s.split("/")
        if len(halves) != 2:
            raise ValueError("String count not be converted to MyNumber")
        try:
            n = int(halves[0])
            d = int(halves[1])
            gcd = math.gcd(d,n)
            n = n // gcd
            d = d // gcd
            found = True
        except:
            # it's not a proper fraction
            # but it may still be an inproper fraction
            pass
        if found:
            return MyNumber((n,d))
        front_half = halves[0].split(" ")
        front_half_meaningful = []
        for segment in front_half:
            if len(segment) > 0:
                front_half_meaningful.append(segment)
        if len(front_half_meaningful) != 2:
            raise ValueError("String count not be converted to MyNumber")
        try:
            whole = int(front_half_meaningful[0])
            n = int(front_half_meaningful[1])
            d = int(halves[1])
            n_total = n + whole * d
            gcd = math.gcd(d,n_total)
            n_total = n_total // gcd
            d = d // gcd
            found = True
        except:
            # it's not an improper function
            # it's garbage
            pass
        if found:
            return MyNumber((n_total,d))
        raise ValueError("String count not be converted to MyNumber")