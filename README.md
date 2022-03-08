# spudlang

Spud is a domain-specific programming language for creating grocery shopping lists.

One of the big overheads to effective grocery shopping
is the time involved in creating a good shopping list.
A good shopping list should:
- contain all the ingredients that you need
- contain nothing that you don't need
- be organized
  - ingredients should be grouped together by where they appear in a store, or by which store sells them
- be deduplicated
  - if two different recipes call for the same ingredient, then there shouldn't be two entries on your shopping list; the two entries should be added together

Creating grocery shopping lists that follow these guidelines takes time.
Wouldn't it be so much easier if you just had to decide which recipes to make
and then an organized and well-formatted grocery shopping list were produced for you?

With Spud, you can easily store recipes and preferred normalization rules
in a personal library. Then, when you need to go shopping, you simply
write the names of the recipes you want to make and presto!
Spud will output a grocery shopping list that contains what you need to buy.
You can even scale the quantities of ingredients, recipes, or entire shopping lists as needed.

## Installation

The Spud interpreter is hosted through [PyPI](https://pypi.org/project/spudlang/)
and can be downloaded using [pip](https://pip.pypa.io/en/stable/).

To install Spud, use:

```
pip install spudlang
```

## Easy Syntax

The syntax is designed to closely follow the English language
to make it easier for newcomers.
For example:
```
6 kg carrots + chopped
```
Without any additional information, one would correctly assume
that this line of Spud code refers to six kilograms of chopped carrots.

Spud can handle arbitrary units of measure, and allows users to use
express numbers in whichever form is most natural.

```
6 kg carrots
1/3 cup water
9/7 lb potatoes
1 3/4 bunch parsley
3.21 cloves garlic
```

Note that the fourth line is a mixed fraction, referring to 1.75 bunches of parsley.

Also consider the following, which instructs the Spud interpreter to
replace every 100 ml of cooked spinach in the original recipes with
500 ml of uncooked spinach in the final grocery list:

```
100 ml spinach +cooked -uncooked is 500 ml spinach -cooked +uncooked
```

Using constructs such as these, it is possible to easily represent a
set of ingredients and normalize it into some standard form.

## Organization

Spud keeps things organized:

```
apples are a type of fruit
bananas are a type of fruit

1 kg apples is 8.5 count apples

2 apples
0.5 kg apples
3 bananas
1 loaf bread
```

The first two lines declare that apples and bananas are fruits.
The next line is a normalization rule, converting
apples by weight into apples by number.
These first three lines can be placed in an importable
library, so that they do not need to be rewritten
for every shopping list.

The output of the above program is:

```
- groceries
  - bread
    - 1 loaf
  - fruit
    - apples
      - 6.25 count
    - bananas
      - 3 count
```

The two lines calling for apples were converted into the same units
and added into a single line item.
Apples and bananas were categorized together as fruit.

## License

Spudlang is released using the MIT License.