
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
    return am.__dict__[_READ_ONLY]


def is_modifiable(am: AttrMap) -> bool:
    return not is_read_only(am)


def convert_to_dict(am: AttrMap) -> Dict:
    return todict(am)


def to_dict(am: AttrMap) -> Dict:
    return todict(am)


def todict(am: AttrMap) -> Dict:
    result = {}
    _prefix = _get_prefix(am)
    for key, value in am.__dict__.items():
        value = todict(value) \
            if isinstance(value, AttrMap) else value
        if key.startswith(_prefix):
            new_key = key.replace(_prefix, "")
            result[new_key] = value
    return result


def convert_state(am: AttrMap, read_only: bool) -> AttrMap:
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
    return convert_state(am, True)


def convert_to_modifiable(am: AttrMap) -> AttrMap:
    return convert_state(am, False)


def merge_from(
        am: AttrMap,
        mapping: AttrMap = None,
        path2file: os.PathLike = None) -> AttrMap:
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
    _prefix = _get_prefix(am)
    keys = filter(
        lambda x: x.startswith(_prefix), am.__dict__.keys()
    )
    keys = map(lambda x: x.replace(_prefix, ""), keys)
    return list(keys)


def get_values(am: AttrMap) -> List:
    return get_vals(am)


def get_vals(am: AttrMap) -> List:
    """
    Get the (top level) `key-value` pair of `AttrMap` object like `dict`.

    Returns:
        items: zip object.

    >>> configs = AttrMap(CONFIGS)
    >>> configs.items()
    <zip object at 0x7fdaf3843a80>
    >>> for key, val in configs.items():
    ...     print(key, val)
    ... # End of for loop.
    attr1 1
    attr2 ['hello', ' ', 'world']
    attr3   subattr1: subattr1
            subattr2:
                    subsubattr1: subsubattr1

    .. NOTE:: If the returned value is modified by user,
        the original AttrMap object may be modified too.
    """
    values = []
    keys = get_keys(am)
    for key in keys:
        values.append(am[key])
    return values


def get_items(am: AttrMap) -> Iterable:
    return zip(get_keys(am), get_vals(am))


def contains(am: AttrMap, key: str) -> bool:
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
