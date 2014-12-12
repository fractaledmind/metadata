metadata
========

Python wrapper for OS X `mdfind` and `mdls`

## Installation

Download the `.zip` file from GitHub.

I'm working on getting the library on [PyPi](https://pypi.python.org/pypi) soon.

## File Metadata Query Expression Syntax

I have modeled the Python syntax on [Apple's original Spotlight query syntax](https://developer.apple.com/library/mac/documentation/Carbon/Conceptual/SpotlightQuery/Concepts/QueryFormat.html). File metadata queries are constructed using a simple query language that takes advantage of Python's flexible class construction. The syntax is relatively straightforward, including comparisons, language agnostic options, and time and date variables.

### Comparison Syntax

The `metadata` library implements 3 custom classes (`MDAttribute`, `MDComparison`, and `MDExpression`) to represent the various units of `mdfind`'s [Query Expression Syntax](https://developer.apple.com/library/mac/documentation/Carbon/Conceptual/SpotlightQuery/Concepts/QueryFormat.html). 

Query comparisons have the following basic format:
```
[attribute] [operator] [value]
```

The following sub-sections will describe these 3 elements more fully, but any such comparison will generate a `MDComparison` object. If you ever want to see what a particular `MDComparison` object will look like as an query string, you can coerce it into a unicode string using the `unicode()` operation (or into a string using the `str()` operation). 

#### Attribute

The first element of a query comparison is the *attribute*, which is a `MDAttribute` object in `metadata`. `metadata` automatically generates `MDAttribute` objects for every Spotlight attribute on your system. You can view the names of all of these objects via `metadata.attributes` variable. Attributes have a Pythonic naming scheme, so `kMDItemFSName` becomes `metadata.name` and `kMDItemContentType` becomes `metadata.content_type`. The `MDAttribute` class is built on top of the metadata information retrieved from `mdimport -A`. If you wish to see all of the information for a metadata attributes, you can use the `metadata.[attribute].info()` function.

As with all of the custom classes, you can coerce a `MDAttribute` object into a unicode string using the `unicode()` operation (i.e. `unicode(metadata.name)` returns `u'kMDItemFSName'`).

#### Operator

The *operator* can be any one of the following:

| Operator                                      | Description                                                                                   |
| :-------------------------------------------: | --------------------------------------------------------------------------------------------- |
| `==`                                          | equal                                                                                         |
| `!=`                                          | not equal                                                                                     |
| `<`                                           | less than (available for numeric values and dates only)                                       |
| `>`                                           | greater than (available for numeric values and dates only)                                    |
| `<=`                                          | less than or equal (available for numeric values and dates only)                              |
| `>=`                                          | greater than or equal (available for numeric values and dates only)                           |
| `in_range(attribute, min_value, max_value)`   | numeric values within the range of min_value through max_value in the specified attribute     |

The `==` and `!=` operators allow for modification. These modifiers specify how the comparison is made.

|                     Modifier                     |                     Description                     |
|--------------------------------------------------|-----------------------------------------------------|
| `metadata.[object].ignore_case`       | The comparison is case insensitive.                 |
| `metadata.[object].ignore_diacritics` | The comparison is insensitive to diacritical marks. |

Both modifiers are on by default. In order to turn one off, you need to set the property to `False`:
```
import metadata

metadata.content_type.ignore_case = False
comparison = metadata.content_type == 'com.adobe.pdf'
```

#### Value

The *value* element of a query comparison can be a string or integer. Strings can use wildcard characters (`*` and `?`) to make the search fuzzy. The `*` character matches multiple characters whereas the `?` wildcard character matches a single character (*Note*: Even in the Terminal, I cannot get wildcard searches with `?` to function properly. I would recommend using `*` as your ony wildcard character). Here are some examples demonstrating how the wildcards function:
```
# Matches attribute values that begin with “paris”. For example, matches “paris”, but not “comparison”.
metadata.text_content == "paris*"

# Matches attribute values that end with “paris”.
metadata.text_content == "*paris"

# Matches attributes that contain "paris" anywhere within the value. For example, matches “paris” and “comparison”.
metadata.text_content == "*paris*"

# Matches attribute values that are exactly equal to “paris”.
metadata.text_content == "paris"
```

In order to use any of the greater-than or less-than operators, your value needs either to be an integer (or float) or a date object. In order to make the API as intuitive as possible, `metadata` allows for human-readable date statements. That is, you do not need to pass `datetime` objects as the *value* of a comparison with a date attribute (like `metadata.creation_date`). `metadata` uses the `parsedatetime` library to convert human-readable dates into `datetime` objects. The following are all acceptable date comparisons:
```
# Created before today
metadata.creation_date < 'today'

# Created after last month
metadata.creation_date > 'one month ago'
```
If `metadata` cannot parse your datetime string, it will raise an `Exception`. The parsing engine is good, but not perfect and can seem capricious. For example, `one month ago` is parsable, but `a month ago` is not. Datetime strings that are parsed are converted into an ISO-8601-STR compliant string.


### Expression syntax

You can combine `MDComparison` objects to create a more complex expression, represented by the `MDExpression` class. Comparison objects can be combined in one of two ways: using a conjuction (`&`) or using a disjuction (`|`). Not only can `MDComparison` objects be combined, but you can nest and combine any combination of `MDComparison` objects and `MDExpression` objects. For example:
```
# query for audio files authored by “stephen” (ignoring case)
metadata.authors == "stephen" & metadata.content_type == "public.audio"

# query for audio files authored by “stephen” or “daniel”
(metadata.authors == "daniel" | metadata.authors == "stephen") & metadata.content_type == "public.audio"

# query for audio or video files authored by “stephen” or “daniel”
(metadata.authors == "daniel" | metadata.authors == "stephen") & (metadata.content_type == "public.audio" | metadata.content_type == "public.video")

# you could also break the last expression into chunks
author_exp = (metadata.authors == "daniel") | (metadata.authors == "stephen")
type_exp = (metadata.content_type == "public.audio") | (metadata.content_type == "public.video")
final_exp = author_exp & type_exp
```

Here's a complex expression to find only audio or video files that have been changed in the last week authored by someone named either "Stephen" or "Daniel" (ignoring case and diacritics, so it would match a file authored by "danièl"):
```
author_exp = (metadata.authors == "daniel") | (metadata.authors == "stephen")
type_exp = (metadata.content_type == "public.audio") | (metadata.content_type == "public.video")
time_comp = metadata.content_change_date == 'one week ago'
query_expression = author_exp & type_exp & time_comp
```
*Note*: parentheses are needed for the first two expressions. Without them, you would get a `TypeError` as Python thinks you are trying to combine the string `"daniel"` with the `MDAttribute` object `authors`, which is an obviously unsupported expression.

Once you have created your query expression (or even a simple comarison), you will pass this to `metadata.find()` in order to execute the file searching.

## Functions

### `find`

The main function is `metadata.find()`. It takes one required argument, `query_expression`, which can be either an `MDExpression` object or an `MDComparison` object. In addition to this one required argument, `metadata.find()` also has the optional argument `only_in` for you to focus the scope of your search to a particular directory tree. This simply needs to be a full (non-relative) path passed as a Unicode string. Other than that, there's nothing else to it. Build you query expression, pass it to `find()` and get your results as a Python list. Here's an example of building the sample expression above and passing it to `metadata.find()`:
```
import metadata

author_exp = (metadata.authors == "daniel") | (metadata.authors == "stephen")
type_exp = (metadata.content_type == "public.audio") | (metadata.content_type == "public.video")
time_comp = metadata.content_change_date == 'one week ago'
query_expression = author_exp & type_exp & time_comp
results = metadata.find(query_expression)
``` 

### `list`

In addition to `find()`, the `metadata` module has the `list` function, which is a wrapper around the `mdls` command. You simply pass it a file path and it returns a dictionary of metadata attributes and values. Once again, the attribute names (the dictionary keys) are simplified using the algorithm used to convert Spotlight attributes to Pythonic names. 
```
import metadata

file_metadata = metadata.list(file_path)
print(file_metadata['name'])
```

### `write`

Finally, there is an alpha version of a `write()` function, which allows you to write metadata to a file. Right now, I have it defaulted to writing to the `kMDItemUserTags` attribute, but a few others have worked. I need to test it more to make it more general. 
