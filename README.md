metadata
========

Python wrapper for OS X `mdfind` and `mdls`

## Installation

Download the `.zip` file from GitHub.

I'm working on getting the library on [PyPi](https://pypi.python.org/pypi) soon.

## Sample Usage

`metadata` implements 3 classes (`MDAttribute`, `MDComparison`, and `MDExpression`) to represent the various units of `mdfind`'s [Query Expression Syntax](https://developer.apple.com/library/mac/documentation/Carbon/Conceptual/SpotlightQuery/Concepts/QueryFormat.html). 

### `find`

Okay, so once you generate your `MDExpression` object, this is what you will pass to `metadata.find()`. In addition to this one required argument, `metadata.find()` also has the optional argument `only_in` for you to focus the scope of your search to a particular directory tree. Other than that, there's nothing else to it. Build you query expression, pass it to `find()` and get your results as a Python list or string (depending on if there is more than one result). Here's an example of building an expression and passing it to `find()`:
```
import metadata

comp1 = metadata.attributes.name == '*blank*'
comp2 = metadata.attributes.user_tags != 'test?'
comp3 = metadata.attributes.creation_date > 'today'

exp = (comp1 & comp2) | comp3
metadata.find(exp)
``` 
Note that date attributes can accept human-readable date statements. `metadata` uses the `parsedatetime` library to convert human-readable dates into `datetime` objects.

### `list`

In addition to `find()`, the module has `list`, which is a wrapper around the `mdls` command. You simply pass it a file path and it returns a dictionary of metadata attributes and values. Once again, the attribute names (the dictionary keys) are simplified using the `clean_key` function seen above. 
```
import metadata

file_metadata = metadata.list(file_path)
print(file_metadata['name'])
```

### `write`
Finally, there is an alpha version of a `write()` function, which allows you to write metadata to a file. Right now, I have it defaulted to writing to the `kMDItemUserTags` attribute, but a few others have worked. I need to test it more to make it more general. 
