r"""
Author:
    Yiqun Chen
Docs:
    An easy module for configuration.
"""

import os, yaml, json
from warnings import warn
from typing import Any, Iterable, Mapping, Union, List
from copy import deepcopy as dcp

class AttrMap(object):
    r"""
    AttrMap behaves like a dict, but user can access values 
    by attribute style.
    """
    def __init__(
        self, 
        source: dict=None, 
        path2file: os.PathLike=None, 
        read_only: bool=False, 
        **kwargs, 
    ) -> None:
        r"""
        Args:
            source: A python built-in `dict` object to be converted to 
                `AttrMap` object.
            path2file: The path to `.json` or `.yaml` file. 
                The content of file will be merged to `AttrMap` object.
                NOTE `AttrMap` doesn't check the conflicts between
                the content of `source` and parsed file.
            read_only: Set the `AttrMap` object to read-only after the 
                object is built.
            kwargs: To allow the users build an `AttrMap` object like
                built-in `dict()` method.

        NOTE Due to `AttrMap` maintains properties and methods, 
        some attribute cannot be accessed via attribute style, but they 
        can still be accessed via `[""]` style. For example:
        ```python
        >>> configs = AttrMap(readonly="unintentional modification")
        >>> configs.readonly
        False
        >>> configs["readonly"]
        'unintentional modification'

        NOTE The attributes should not be the same with any python magic 
        method.

        NOTE The attribute start with `_` might be conflict with `AttrMap`
        preserved methods.
        ```
        """
        super(AttrMap, self).__init__()
        self.__dict__["ATTRMAP_LEVEL"] = 0
        self.__dict__["ATTRMAP_PREFIX"] = "_ATTRMAP_PREFIX_"
        self.__dict__["READ_ONLY"] = False
        self.__dict__["PRESERVED"] = {
            "read_only", "readonly", "todict", "convert_state", 
            "merge_from", "keys", "values", "vals", "items", 
            "contains"}
        if source is not None:
            self._build_from_dict(source)
        if kwargs:
            self._build_from_dict(kwargs)
        if path2file is not None:
            self._build_from_file(path2file)
        self.convert_state(read_only=read_only)

    @property
    def read_only(self) -> bool:
        r"""
        Return the state of `AttrMap` object. 
        `True` is read-only and any modification to the object 
        is not allowed.
        """
        return self.__dict__["READ_ONLY"]

    @property
    def readonly(self) -> bool:
        r"""Alias of `read_only`"""
        return self.read_only

    def todict(self) -> dict:
        r"""
        Convert to a python builtin dict, which does not 
        share memory with AttrMap instance. 
        The state (is read-only or not) will not influence this method.
        """
        result = {}
        for key, value in self.__dict__.items():
            value = value.todict() \
                if isinstance(value, AttrMap) else value
            if key.startswith(self._prefix):
                new_key = key.replace(self._prefix, "")
                result[new_key] = value
        return result

    def convert_state(self, read_only: bool=None):
        r"""
        Convert the state as read only or not. 
        If `None` is passed (not recommended), the state
        will be revert from `True` to `False` 
        or `False` to `True`.
        """
        if read_only is None:
            read_only = not self.readonly
        elif read_only not in [True, False]:
            raise ValueError(
                    f"Expect attribute read_only takes value "
                    f"from [True, False, None], but got {read_only}"
                )
        self.__dict__["READ_ONLY"] = read_only
        for _, value in self.__dict__.items():
            if isinstance(value, AttrMap):
                value.convert_state(read_only)
        return self

    def merge_from(self, mapping=None, path2file: os.PathLike=None):
        r"""
        Allows users to merge from a file or a mappable object.
        NOTE The existing value will be overwrited.
        """
        self._check_modifiable()
        if mapping is not None:
            new = merge_mapping(self, mapping)
        if path2file is not None:
            new = overwrite_mapping_from_file(self, path2file)
        self.__dict__.update(new.__dict__)
        return self

    @property
    def _prefix(self) -> str:
        return self.__dict__["ATTRMAP_PREFIX"]
    
    @property
    def _level(self) -> int:
        return self.__dict__["ATTRMAP_LEVEL"]

    def keys(self) -> List[str]:
        r"""
        Get the (top level) keys of `AttrMap` object.
        """
        keys = filter(
            lambda x: x.startswith(self._prefix), self.__dict__.keys()
        )
        keys = map(lambda x: x.replace(self._prefix, ""), keys)
        return list(keys)

    def values(self) -> List[Any]:
        r"""
        Get the (top level) values of `AttrMap` object.
        The alias of `values` is `vals`.
        """
        values = []
        for key in self.keys():
            values.append(self[key])
        return values

    vals = values

    def items(self) -> Iterable:
        r"""
        Get the (top level) `key-value` pair of `AttrMap` object like `dict`.
        """
        return zip(self.keys(), self.vals())

    def contains(self, name: str) -> bool:
        r"""Check if `AttrMap` contains specific attribute."""
        return self._wrap_name(name) in self.__dict__.keys()

    def _update_level(self):
        for key, value in self.__dict__.items():
            if not self._prefix in key:
                continue
            if isinstance(value, AttrMap):
                value.__dict__["ATTRMAP_LEVEL"] = self._level + 1
                value._update_level()

    def _build_from_dict(self, src_dict: dict):
        for key, value in src_dict.items():
            self.__setattr__(key, value)

    def _build_from_file(self, path2file: Union[str, os.PathLike]):
        if not os.path.exists(path2file):
            raise FileNotFoundError(
                f"Failed to find such yaml file: {path2file}."
            )
        with open(path2file, 'r') as fp:
            if path2file.endswith(".json"):
                source = json.load(fp)
            if path2file.endswith(".yaml") or path2file.endswith(".yml"):
                source = yaml.safe_load(fp)
            self._build_from_dict(source)

    def _wrap_name(self, name: str) -> str:
        return f"{self._prefix}{str(name)}"

    def __setitem__(self, key: str, value: Any):
        self.__setattr__(key, value)

    def __setattr__(self, key: str, value: Any):
        self._check_modifiable()
        if key in self.__dict__["PRESERVED"]:
            self._preserved_warning(key)
        value = AttrMap(value) if isinstance(value, Mapping) else value
        self.__dict__[self._wrap_name(key)] = value
        self._update_level()

    def __getitem__(self, key: str) -> Any:
        return self.__getattr__(key)

    def __getattr__(self, key: str) -> Any:
        if not self._wrap_name(key) in self.__dict__.keys():
            if self.read_only:
                raise AttributeError("No such attribute: {}".format(key))
            self.__dict__[self._wrap_name(key)] = AttrMap()
            self._update_level()
        return self.__dict__[self._wrap_name(key)]

    def __getstate__(self) -> dict:
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __delitem__(self, key: str):
        self._check_modifiable()
        del self.__dict__[self._wrap_name(key)]

    def __delattr__(self, key: str) -> None:
        self._check_modifiable()
        del self.__dict__[self._wrap_name(key)]

    def __eq__(self, other) -> bool:
        return self.__dict__ == other.__dict__

    def __iter__(self) -> Iterable:
        return iter(self.todict().items())

    def __contains__(self, item: str) -> bool:
        return self.contains(item)

    def __copy__(self):
        target = AttrMap()
        for key, value in self.__dict__.items():
            if self._prefix in key:
                key = key.replace(self._prefix, "")
                target[key] = value
        return target

    def __deepcopy__(self, memo):
        other = AttrMap()
        for key, value in self.__dict__.items():
            if id(self) in memo:
                continue
            if self._prefix in key:
                _key = key.replace(self._prefix, "")
                other[dcp(_key)] = dcp(value, memo)
        memo[id(self)] = self
        return other

    def __str__(self) -> str:
        start = ""
        template = "{}{} {}: {}{}"
        string = []
        level = self._level
        if level == 0:
            string.append("Object Contains Following Attributes")
        for key, value in self.items():
            substring = template.format(
                "\t" * self._level, 
                start, 
                key, 
                "\n" if isinstance(value, AttrMap) else "", 
                str(value), 
            )
            string.append(substring)
        string = "\n".join(string)
        return string

    __repr__ = __str__

    def _check_modifiable(self):
        if self.read_only:
            raise AttributeError(
                f"A read only AttrMap instance "
                f"is not allowed to modify its attribute."
            )

    def _preserved_warning(self, key: str):
        warn(
            f"AttrMap get an attribute `{key}` which is in the "
            f"preserved set {self.__dict__['PRESERVED']}."
            f"You cannot access this attribute via attribute-style "
            f"accessing, but the dict style [''] still works.")

def merge_mapping(
    mapping: Union[AttrMap, dict], 
    another: Union[AttrMap, dict], 
) -> AttrMap:
    if isinstance(mapping, AttrMap):
        mapping = mapping.todict()
    if isinstance(another, AttrMap):
        another = another.todict()
    for key, val in another.items():
        if key not in mapping.keys():
            mapping[key] = val
        elif isinstance(val, dict) \
                and isinstance(mapping[key], dict):
            cfg = merge_mapping(mapping[key], val).todict()
            mapping[key] = cfg
        else:
            mapping[key] = val
    return AttrMap(mapping)


def overwrite_mapping_from_file(
    mapping: AttrMap, path2file: Union[str, os.PathLike]
) -> AttrMap:
    if not os.path.exists(path2file):
        return mapping
    with open(path2file, 'r') as fp:
        if path2file.endswith(".yaml") or path2file.endswith(".yml"):
            mapping_file = yaml.safe_load(fp)
        if path2file.endswith(".json"):
            mapping_file = json.load(fp)
    mapping = merge_mapping(mapping, mapping_file)
    return mapping


AttributeMap = AttributeMapping = AttrMapping = AttrMap

