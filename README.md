metadata
========

Python wrapper for OS X `mdfind` and `mdls`

## Installation

Download the `.zip` file from GitHub.

I'm working on getting the library on [PyPi](https://pypi.python.org/pypi) soon.

## Data Structures

`metadata` implements 3 classes (`MDAttribute`, `MDComparison`, and `MDExpression`) to represent the various units of `mdfind`'s [Query Expression Syntax](https://developer.apple.com/library/mac/documentation/Carbon/Conceptual/SpotlightQuery/Concepts/QueryFormat.html). 

### `MDAttribute`
An `MDAttribute` object represents exactly that, a metadata attribute (like `kMDItemFSName`). The `attributes.py` module dynamically generates `MDAttribute` object to represent all Spotlight attributes on the user's system (using `mdimport -A` to get them). The naming of these objects aims to get them into Pythonic form, using this function:
```
def clean_key(self, key):
    uid = key.replace('kMDItemFS', '')\
             .replace('kMDItem', '')\
             .replace('kMD', '')\
             .replace('com_', '')\
             .replace(' ', '')
    return self.convert_camel(uid)
```

Thus, `kMDItemFSName` becomes `name` and `kMDItemContentType` becomes `content_type`. You can view all `MDAttribute`s available in `attributes.py` via `all`. That is:
```
from metadata import attributes
print(sorted(attributes.all))
```

### `MDComparison`
An `MDComparison` object is created whenever you compare an `MDAttribute` object to a predicate. The `MDComparison` makes use of Python's comparison magic methods to implement the API, so these are all `MDComparison` objects:
```
from metadata import attributes

attributes.name == 'blank'
attributes.user_tags != 'test'
attributes.creation_date > 'today'
attributes.creation_date < 'yesterday'
attributes.logical_size >= 1000
attributes.logical_size <= 1000
```
Note that only numeric and date attributes can use any of the greater or lesser comparisons.

If you want to see how the `MDComparison` object looks as a query string, use the `<MDComparison>.format()` method:
```
>>> (attributes.name == 'blank').format()
kMDItemFSName == "blank"cd
>>> (attributes.user_tags != 'test').format()
kMDItemUserTags != "test"cd
>>> (attributes.creation_date > 'today').format()
kMDItemFSCreationDate > $time.iso(2014-12-10T09:00:00)
>>> (attributes.creation_date < 'yesterday').format()
kMDItemFSCreationDate < $time.iso(2014-12-09T09:00:00)
>>> (attributes.logical_size >= 1000).format()
kMDItemLogicalSize >= 1000
>>> (attributes.logical_size <= 1000).format()
kMDItemLogicalSize <= 1000
``` 

### `MDExpression`
You group `MDComparison` objects together to form `MDExpression` objects. An `MDExpression` object represents the query expression created when `MDComparison` objects and/or `MDExpression` objects are joined. There are only two ways to join elements in an `MDExpression` object: conjunction and disjunction. `MDExpression` uses the magic methods `__and__` and `__or__` to handle these relations. And, as hinted at above, an `MDExpression` object can consist of infinite units of either the `MDComparison` or `MDExpression` type. For example:
```
from metadata import attributes

comp1 = attributes.name == '*blank*'
comp2 = attributes.user_tags != 'test?'
comp3 = attributes.creation_date > 'today'
comp4 = attributes.creation_date < 'yesterday'
comp5 = attributes.logical_size >= 1000
comp6 = attributes.logical_size <= 1000

# `MDExpression` objects
exp1 = comp1 & comp2
exp2 = comp3 | comp4
exp3 = comp1 & (comp5 | comp6)
exp4 = (comp1 | comp2) & (comp3 | comp4)
exp5 = exp1 | comp1 | exp2
```

Once again, to see how the `MDExpression` object looks as a query string, use the `<MDExpression>.format()` method:
```
# exp1
kMDItemFSName == "*blank*"cd && kMDItemUserTags != "test?"cd
# exp2
kMDItemFSCreationDate > $time.iso(2014-12-11T09:00:00) || kMDItemFSCreationDate < $time.iso(2014-12-10T09:00:00)
# exp3
kMDItemFSName == "*blank*"cd && (kMDItemLogicalSize >= 1000 || kMDItemLogicalSize <= 1000)
# exp4
(kMDItemFSName == "*blank*"cd || kMDItemUserTags != "test?"cd) && (kMDItemFSCreationDate > $time.iso(2014-12-11T09:00:00) || kMDItemFSCreationDate < $time.iso(2014-12-10T09:00:00))
# exp5
((kMDItemFSName == "*blank*"cd && kMDItemUserTags != "test?"cd) || kMDItemFSName == "*blank*"cd) && (kMDItemFSCreationDate > $time.iso(2014-12-11T09:00:00) || kMDItemFSCreationDate < $time.iso(2014-12-10T09:00:00))
```

I personally really like the Operator Overloading, though I know that some people don't. I was going for a silky-smooth API, and I think this achieves that best. No need for wordy methods like `<MDAttribute>.is_equal(predicate)`. 

## Functions
### `find`
Okay, so once you generate your `MDExpression` object, this is what you will pass to `metadata.find()`. In addition to this one required argument, `metadata.find()` also has the optional argument `only_in` for you to focus the scope of your search to a particular directory tree. Other than that, there's nothing else to it. Build you query expression, pass it to `find()` and get your results as a Python list or string (depending on if there is more than one result). Here's an example of building an expression and passing it to `find()`:
```
from metadata import attributes, find

comp1 = attributes.name == '*blank*'
comp2 = attributes.user_tags != 'test?'
comp3 = attributes.creation_date > 'today'

exp = comp1 & comp2 & comp3
find(exp)
``` 

### `ls`
In addition to `find()`, the module has `ls`, which is a wrapper around the `mdls` command. You simply pass it a file path and it returns a dictionary of metadata attributes and values. Once again, the attribute names (the dictionary keys) are simplified using the `clean_key` function seen above. 

### `write`
Finally, there is an alpha version of a `write()` function, which allows you to write metadata to a file. Right now, I have it defaulted to writing to the `kMDItemUserTags` attribute, but a few others have worked. I need to test it more to make it more general. 
