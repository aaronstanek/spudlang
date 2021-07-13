# defines a class MyNumber
# this can hold floating point numbers
# and fractions, and convert between
# then easily

import math

class MyNumber(object):
    # has 2 member variables
    # bool is_fraction
    # ? value
    # if is_fraction is False, value will be a float
    # if is_fraction is True, value will be (int,int)
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
        # returns a string representation of self.value
        # will use proper fractions over improper fractions
        if self.is_fraction:
            whole = self.value[0] // self.value[1]
            part = self.value[0] % self.value[1]
            if whole == 0:
                if part == 0:
                    # the value is zero
                    return "0"
                else:
                    # it's a short fraction
                    return str(part) + "/" + str(self.value[1])
            else:
                # it's an long fraction
                if part == 0:
                    # it's a whole number
                    return str(whole)
                else:
                    # it's a true long fraction
                    return str(whole) + " " + str(part) + "/" + str(self.value[1])
        else:
            return str(self.value)
    def as_float(self):
        # returns a version of this object
        # where is_fraction will be False
        if self.is_fraction:
            n = float(self.value[0]) / float(self.value[1])
            return MyNumber(n)
        else:
            return self
    def as_fraction(self,d):
        # returns a version of this object
        # where is_fraction will be True
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
            # we will return a floating point MyNumber
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
            # return a floating-point MyNumber
            n = self.as_float().value * other.as_float().value
            return MyNumber(n)
    def multiplicative_inverse(self):
        # returns the multiplicative inverse, if it exists
        if self.is_fraction:
            return MyNumber( (self.value[1],self.value[0]) )
        else:
            return MyNumber( 1.0 / self.value )
    @staticmethod
    def from_string(s):
        # convert a string to an appropriate
        # MyNumber
        # integers -> fraction with denominator 1
        # floats -> floats
        # short fractions -> fractions
        # long fractions -> fractions
        if type(s) != str:
            raise TypeError("Expected s to be a string")
        # int is the most restrictive
        found = False
        # found will indicate that we are ready
        # to return a value
        try:
            n = int(s)
            found = True
        except:
            # it's not an integer
            pass
        if found:
            # n is the int representation of s
            return MyNumber((n,1))
        # float is less restrictive
        try:
            n = float(s)
            found = True
        except:
            # it's not a float
            pass
        if found:
            # n is the float representation of s
            # s does not encode an int, even if the
            # value is an integer
            return MyNumber(n)
        # we either have a fraction or garbage
        halves = s.split("/")
        # halves should be the two parts of the fraction
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
            # it's not a short fraction
            # but it may still be a long fraction
            pass
        if found:
            # n is the int representation of s before the /
            # d is the int representation of s after the /
            # (reduced by gcd)
            return MyNumber((n,d))
        # at this point, it can only be a long fraction
        # or garbage
        front_half = halves[0].split(" ")
        # front half is everything before the
        # / character, diliminated by spaces
        front_half_meaningful = []
        for segment in front_half:
            if len(segment) > 0:
                front_half_meaningful.append(segment)
        # front_half_meaningful are all of the nonempty segments
        # of front_half
        # ideally, there should only be two nonempty segments
        # the first will the the whole number part of the fraction
        # the second will be the numerator
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
            # it's not an long function
            # it's garbage
            pass
        if found:
            # n_total will be the numerator of the improper fraction representation
            # d will be the denominator of the improper fraction representation
            # (both reduced by gcd)
            return MyNumber((n_total,d))
        raise ValueError("String count not be converted to MyNumber")