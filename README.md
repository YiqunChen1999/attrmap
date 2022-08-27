
# AttrMap

`attrmap` is an open source tool with **read-only protection** to help users get rid of dictionary in Python.

## Introduction

`attrmap` maps the `dict` to an object of `AttrMap`, so users can avoid using the annoying `[""]` syntax. 

Users are welcome to report issues or request new features.

The API references can be found [here](https://attrmap.readthedocs.io/en/latest/index.html).

## What's New

- 2022-08-27: Add utilities for AttrMap, see [docs](https://attrmap.readthedocs.io/en/latest/index.html).
- 2022-08-27: Add deprecated warnings.
- 2022-08-13: Fix the `delattr` bug, you can delete an item via `del obj.attr` when `AttrMap` object is modifiable.
- 2022-08-13: Fix the improper use of type hint, now `attrmap` is available for python>=3.6.
- 2022-08-13: Update the document.

## Installation

You can install `attrmap` via pip:

```bash
pip install -U attrmap
```

## Getting Started

Assuming you have an instance of `dict`, then you can build an object of `AttrMap` as follows:

```python
from attrmap import AttrMap

CONFIGS = {
    "attr1": 1, 
    "attr2": ["hello", " ", "world"], 
    "attr3": {
        "subattr1": "subattr1", 
        "subattr2": {
            "subsubattr1": "subsubattr1",
        }
    }
}

configs = AttrMap(CONFIGS)

# Set the object unmodifiable.
configs = configs.convert_state(read_only=True)
# Equivalent to:
# configs.convert_state(read_only=True)

print(configs) # The outputs is more human readable.
# Object Contains Following Attributes
#  attr1: 1
#  attr2: ['hello', ' ', 'world']
#  attr3:
#          subattr1: subattr1
#          subattr2:
#                  subsubattr1: subsubattr1
```

You can also assign the attributes and their values in a more simple way:

```python
# Assume you have import AttrMap
# Create an empty AttrMap object.
configs = AttrMap()
configs.attr1 = 1
configs.attr2 = ["hello", " ", "world"]
configs.attr3.subattr1 = "subattr1"
configs.attr3.subattr2.subsubattr2 = "subsubattr1"

print(configs)
# Object Contains Following Attributes
#  attr1: 1
#  attr2: ['hello', ' ', 'world']
#  attr3:
#          subattr1: subattr1
#          subattr2:
#                  subsubattr2: subsubattr1
```

You can convert the `AttrMap` object to Python `dict` anytime:

```python
configs_dict = configs.todict()

print(configs_dict)
# {'attr1': 1, 'attr2': ['hello', ' ', 'world'], 'attr3': {'subattr1': 'subattr1', 'subattr2': {'subsubattr1': 'subsubattr1'}}}

print(type(configs_dict))
# <class 'dict'>

# AttrMap object doesn't store the original dict. 
print(id(configs_dict))
# 139881853477376
print(id(CONFIGS))
# 139881853478464

# But it do not change the items:
print(configs_dict == CONFIGS)
# True
```

`attrmap` has the `read-only` protection to protect you from unintentional modification:

```python
# Assume you have the above AttrMap object named configs
# Now set the AttrMap object as read-only.
configs = configs.convert_state(read_only=True)

# Try to create a new attribute.
configs.attr4 = "unintentional modification"
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "/xxxx/attrmap.py", line xxx, in __setattr__
#     raise AttributeError(
# AttributeError: A read only AttrMap instance is not allowed to modify its attribute.

# Try to modify the value of existing attribute:
configs.attr1 = "unintentional modification"
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "/xxxxx/attrmap.py", line xxx, in __setattr__
#     raise AttributeError(
# AttributeError: A read only AttrMap instance is not allowed to modify its attribute.
```

The `read-only` protection is quite useful when you use `AttrMap` object to store the configuration of any system, any unintentional modification is not allowed. If you want to update the value of attribute, just set the `read_only` of `AttrMap` instance as `False` via `.convert_state(read_only=False)`. 

If the `AttrMap` object should be unmodifiable, set the object as **read only** is recommended.

You can also build a `AttrMap` instance from a `.json` or `.yaml` file. For example, assume you have an `file.json` file:

```json
{
    "language": ["python", "cpp", "java"], 
    "value": [["one", "two"]], 
    "structure":{
        "tree":["left tree", "right tree"]
    }
}
```

Then you can build `AttrMap` object via:

```python
from attrmap import AttrMap

configs = AttrMap(path2file="/PATH_TO_YOUR_DIRECTORY/file.json") # .yaml file works too.
print(configs)
# Object Contains Following Attributes
#  language: ['python', 'cpp', 'java']
#  value: [['one', 'two']]
#  structure:
#          tree: ['left tree', 'right tree']
```

**NOTE:** The `read-only` protection should be explicitly enabled, `AttrMap` assumes you are still setting the attributes and their values.

## Known Issues

- Attributes start with `_` might be conflict with `AttrMap` perserved methods/properties. Attributes can still be accessed via dict-style (`[""]`), but the attribute-style
will return the "protected" (not the term of python, only means it's not "public") method such as `_build_from_dict`.
- Some public available properties and methods are reserved, they can only accessed via the dict-style.

## Running Tests

Open bash shell and execute:

```bash
bash -i ./auto_test.sh
```

## APIs

See [The API Reference](https://attrmap.readthedocs.io/en/latest/modules.html)

## TODO

## LICENSE

`AttrMap` is an open source tool under Apache 2.0 license.
