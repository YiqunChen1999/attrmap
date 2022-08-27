
"""
Utilities for AttrMap.

Author:
    Yiqun Chen
"""

from copy import deepcopy
from typing import Dict, Iterable, List, Union
import os
import yaml
import json

from attrmap import AttrMap


_READ_ONLY = 'READ_ONLY'
_ATTRMAP_PREFIX = 'ATTRMAP_PREFIX'
_ATTRMAP_LEVEL = 'ATTRMAP_LEVEL'
_RESERVED = 'RESERVED'


def is_read_only(am: AttrMap) -> bool:
    """
    Return the state of `AttrMap` object.
    `True` is read-only and any modification to the object
    is not allowed, e.g., add or delete an attribute,
    change the value of any attribute.

    >>> configs = AttrMap(CONFIGS)
    >>> configs = convert_state(configs, read_only=True)
    >>> print(configs)
    Object Contains Following Attributes
        attr1: 1
        attr2: ['hello', ' ', 'world']
        attr3:
            subattr1: subattr1
            subattr2:
                    subsubattr1: subsubattr1
    # Try to create a new attribute.
    >>> configs.attr4 = "unintentional modification"
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/xxxx/attrmap.py", line xxx, in __setattr__
            self._check_modifiable()
        File "/xxxx/attrmap.py", line xxx, in _check_modifiable
            raise AttributeError(
        AttributeError: A read only AttrMap instance is not allowed to modify\
            its attribute.
    # Try to modify the value of existing attribute:
    >>> configs.attr1 = "unintentional modification"
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/xxxx/attrmap.py", line xxx, in __setattr__
            self._check_modifiable()
        File "/xxxx/attrmap.py", line xxx, in _check_modifiable
            raise AttributeError(
        AttributeError: A read only AttrMap instance is not allowed to modify\
            its attribute.
    >>> print(configs)
    Object Contains Following Attributes
        attr1: 1
        attr2: ['hello', ' ', 'world']
        attr3:
            subattr1: subattr1
            subattr2:
                    subsubattr1: subsubattr1
    """
    return am.__dict__[_READ_ONLY]


def is_modifiable(am: AttrMap) -> bool:
    """
    Return the state of `AttrMap` object.
    If the object is read only, then return False, and vice versa.
    """
    return not is_read_only(am)


def todict(am: AttrMap) -> Dict:
    """
    Convert to a python builtin dict, which does not
    share memory with AttrMap instance.
    The state (is read-only or not) will not influence this method.
    For example:

    >>> configs = AttrMap(CONFIGS)
    >>> configs_dict = todict(configs)
    >>> print(configs_dict)
    {'attr1': 1, 'attr2': ['hello', ' ', 'world'],
    'attr3': {'subattr1': 'subattr1',
    'subattr2': {'subsubattr1': 'subsubattr1'}}}
    >>> print(type(configs_dict))
    <class 'dict'>
    # AttrMap object doesn't store the original dict.
    >>> print(id(configs_dict))
    139881853477376
    >>> print(id(CONFIGS))
    139881853478464
    # But it do not change the items:
    >>> print(configs_dict == CONFIGS)
    True
    """
    result = {}
    _prefix = _get_prefix(am)
    for key, value in am.__dict__.items():
        value = todict(value) \
            if isinstance(value, AttrMap) else value
        if key.startswith(_prefix):
            new_key = key.replace(_prefix, "")
            result[new_key] = value
    return result


convert_to_dict = todict
to_dict = todict


def convert_state(am: AttrMap, read_only: bool) -> AttrMap:
    """
    Convert the state as read only or not.

    This method will return the self object,
    so the both two code snipts are equivalent:

    >>> configs = AttrMap(CONFIGS)
    >>> convert_state(configs, True)
    >>> configs_new = convert_state(configs, True)
    >>> id(configs) == id(configs_new)
    True
    """
    if read_only not in [True, False]:
        raise ValueError(
            f"Expect attribute read_only takes value "
            f"from [True, False, None], but got {read_only}")
    am.__dict__["READ_ONLY"] = read_only
    for _, value in am.__dict__.items():
        if isinstance(value, AttrMap):
            convert_state(value, read_only)
    return am


def convert_to_read_only(am: AttrMap) -> AttrMap:
    """
    Convert the statue to read only.
    """
    return convert_state(am, True)


def convert_to_modifiable(am: AttrMap) -> AttrMap:
    """Convert the state to modifiable."""
    return convert_state(am, False)


def merge_from(
        am: AttrMap,
        mapping: AttrMap = None,
        path2file: os.PathLike = None) -> AttrMap:
    """
    Merge from a file (json or yaml) or a mappable object (dict or AttrMap).

    .. NOTE:: The existing value will be overwrited.

    Args:
        am:
            AttrMap object, key-value pairs of other object
            will be merged in it.
        mapping:
            An instance of dict or AttrMap.
        path2file:
            The path to the json or yaml file.

    Returns:
        The merged object, shares id with input am.

    >>> configs = AttrMap(CONFIGS)
    >>> print(configs)
    Object Contains Following Attributes
    attr1: 1
    attr2: ['hello', ' ', 'world']
    attr3:
            subattr1: subattr1
            subattr2:
                    subsubattr1: subsubattr1
    >>> id(configs)
    140416566573808
    >>> configs_new = merge_from(configs, {'attr4': 'attr4'})
    >>> print(configs)
    Object Contains Following Attributes
    attr1: 1
    attr2: ['hello', ' ', 'world']
    attr3:
            subattr1: subattr1
            subattr2:
                    subsubattr1: subsubattr1
    attr4: attr4
    >>> id(configs_new) == id(configs)
    True
    >>> configs is configs_new
    True
    """
    if is_read_only(am):
        raise AttributeError("Cannot merge to a read only AttrMap object.")
    if mapping is not None:
        new = merge_from_mapping(AttrMap(), mapping)
        # Make sure the original object is modified instead creating
        # a new object.
        am.__dict__.update(new.__dict__)
    if path2file is not None:
        new = merge_from_file(AttrMap(), path2file)
        # Make sure the original object is modified instead creating
        # a new object.
        am.__dict__.update(new.__dict__)
    return am


def get_keys(am: AttrMap) -> List:
    """
    Get the (top level) keys of `AttrMap` object.

    Returns:
        keys: A list of keys.

    >>> configs = AttrMap(CONFIGS)
    >>> get_keys(configs)
    ['attr1', 'attr2', 'attr3']
    >>> type(configs.keys())
    <class 'list'>

    That is, only the top-level attribute names will be returned.
    Similarily:

    >>> get_keys(configs['attr3']) # equivalent to get_keys(configs.attr3)
    ['subattr1', 'subattr2']
    """
    _prefix = _get_prefix(am)
    keys = filter(
        lambda x: x.startswith(_prefix), am.__dict__.keys()
    )
    keys = map(lambda x: x.replace(_prefix, ""), keys)
    return list(keys)


def get_vals(am: AttrMap) -> List:
    """
    Get the (top level) values of `AttrMap` object.
    The alias of `values` is `vals`.

    Returns:
        values: A list of values.

    >>> values = get_vals(configs)
    >>> print(type(values))
    <class 'list'>
    >>> print(values)
    [1, ['hello', ' ', 'world'],     subattr1: subattr1
        subattr2:
                subsubattr1: subsubattr1, ]
    >>> type(values[0])
    <class 'int'>
    >>> type(values[1])
    <class 'list'>
    >>> type(values[2])
    <class 'attrmap.attrmap.AttrMap'>
    >>> type(values[3])
    <class 'attrmap.attrmap.AttrMap'>

    .. NOTE:: If the returned value is modified by user,
        the original AttrMap object may be modified too.
    """
    values = []
    keys = get_keys(am)
    for key in keys:
        values.append(am[key])
    return values


get_values = get_vals


def get_items(am: AttrMap) -> Iterable:
    """
    Get the (top level) `key-value` pair of `AttrMap` object like `dict`.

    Returns:
        items: zip object.

    >>> configs = AttrMap(CONFIGS)
    >>> get_items(configs)
    <zip object at 0x7fdaf3843a80>
    >>> for key, val in get_items(configs):
    ...     print(key, val)
    ... # End of for loop.
    attr1 1
    attr2 ['hello', ' ', 'world']
    attr3   subattr1: subattr1
            subattr2:
                    subsubattr1: subsubattr1
    """
    return zip(get_keys(am), get_vals(am))


def contains(am: AttrMap, key: str) -> bool:
    """
    Check if `AttrMap` contains specific attribute.

    >>> configs = AttrMap(CONFIGS)
    >>> for obj in configs:
    ...     print(obj)
    ... # End of for loop.
    ('attr1', 1)
    ('attr2', ['hello', ' ', 'world'])
    ('attr3', {'subattr1': 'subattr1', \
        'subattr2': {'subsubattr1': 'subsubattr1'}})
    """
    return key in am


def merge_from_mapping(
    mapping: Union[AttrMap, Dict],
    another: Union[AttrMap, Dict],
) -> AttrMap:
    """
    Merge another dict or AttrMap object to a given dict or AttrMap object.

    Args:
        mapping:
            The given object.
        another:
            Another object.

    Returns:
        obj: An AttrMap object.

    .. NOTE:: The value of the given object `mapping` will be overwritten.
    """
    if isinstance(mapping, AttrMap):
        mapping = todict(mapping)
    if isinstance(another, AttrMap):
        another = todict(another)
    for key, val in another.items():
        if key not in mapping.keys():
            mapping[key] = val
        elif isinstance(val, dict) \
                and isinstance(mapping[key], dict):
            cfg = todict(merge_from_mapping(mapping[key], val))
            mapping[key] = cfg
        else:
            mapping[key] = val
    return AttrMap(mapping)


def merge_from_file(
    mapping: Union[dict, AttrMap], path2file: Union[str, os.PathLike]
) -> AttrMap:
    """
    Similar to `merge_mapping`, the difference lie in another source, here
    another source is a json file or a yaml file.

    Args:
        mapping:
            The given source.
        path2file:
            The path to another source,
            currently supports both json and yaml file.

    Returns:
        obj: An AttrMap object.
    """
    if not os.path.exists(path2file):
        raise FileNotFoundError(f"File {path2file} not found.")
    with open(path2file, 'r') as fp:
        if path2file.endswith(".yaml") or path2file.endswith(".yml"):
            mapping_file = yaml.safe_load(fp)
        if path2file.endswith(".json"):
            mapping_file = json.load(fp)
    mapping = merge_from_mapping(mapping, mapping_file)
    return mapping


def _get_prefix(am: AttrMap) -> str:
    return am.__dict__[_ATTRMAP_PREFIX]


def _wrap_name(am: AttrMap, name: str) -> str:
    _prefix = _get_prefix(am)
    return f"{_prefix}{str(name)}"


def _get_level(am: AttrMap) -> int:
    return am.__dict__[_ATTRMAP_LEVEL]
