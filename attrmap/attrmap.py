
"""
Author:
    Yiqun Chen
Docs:
    An easy module for configuration.
"""

import os
import yaml
import json
from warnings import warn
from typing import Any, Iterable, Mapping, Union, List
from copy import deepcopy as dcp


class AttrMap(object):
    """
    `attrmap` is an open source tool with read-only protection
    to help users get rid of dictionary in Python. AttrMap behaves
    like a dict, but user can access values by attribute style.

    Args:
        source:
            A python built-in `dict` object to be converted to
            `AttrMap` object.
        path2file:
            The path to `.json` or `.yaml` file.
            The content of file will be merged to `AttrMap` object.
        read_only:
            Set the `AttrMap` object to read-only after the
            object is built. See `read_only` property.
        kwargs:
            To allow the users build an `AttrMap` object like
            built-in `dict()` method.

    For example: Users can create an `AttrMap` object from an
    existing python built-in object:

    >>> from attrmap import AttrMap
    >>> import attrmap.utils as au
    >>> CONFIGS = {
    ... "attr1": 1,
    ... "attr2": ["hello", " ", "world"],
    ... "attr3": {
    ...     "subattr1": "subattr1",
    ...     "subattr2": {
    ...         "subsubattr1": "subsubattr1",
    ...     }
    ... }
    }
    >>> configs = AttrMap(CONFIGS)
    >>> print(configs)
    Object Contains Following Attributes
        attr1: 1
        attr2: ['hello', ' ', 'world']
        attr3:
                subattr1: subattr1
                subattr2:
                        subsubattr1: subsubattr1

    Users can also create from an empty `AttrMap` object:

    >>> configs = AttrMap()
    >>> configs.attr1 = 1
    >>> configs.attr2 = ["hello", " ", "world"]
    >>> configs.attr3.subattr1 = "subattr1"
    >>> configs.attr3.subattr2.subsubattr2 = "subsubattr1"
    >>> configs.attr4
    # Get an empty line, but the attribute attr1 is created.
    >>> type(configs.attr4)
    <class 'attrmap.attrmap.AttrMap'>

    That is, assume the `AttrMap` object is modifiable (read_only property
    is False), when an attribute is accessed, the object will first look
    in the stored attributes and return the value if the attribute is stored.
    Otherwise, the object will create an attribute with the given name, and
    the value is the given value (or an instance of `AttrMap` if get nothing).

    A common scene of `AttrMap` is load the configuration of a system. Let's
    assume you have a `file.json` (`.yaml` file works too)
    with following contents:

    .. code-block:: json
        :linenos:

        {
            "language": ["python", "cpp", "java"],
            "value": [["one", "two"]],
            "structure":{
                "tree":["left tree", "right tree"]
            }
        }

    Then you can create an `AttrMap` object via:

    >>> configs = AttrMap(path2file="/PATH_TO_FOLDER/file.json")
    >>> print(configs)
    Object Contains Following Attributes
    language: ['python', 'cpp', 'java']
    value: [['one', 'two']]
    structure:
            tree: ['left tree', 'right tree']

    Users can access the value of a specific attribute via attribute-style
    or dict-style or the mixing of both:

    >>> configs = AttrMap(CONFIGS)
    >>> configs.attr1
    1
    >>> configs["attr1"]
    1
    >>> au.convert_state(configs, read_only=False)
    >>> del configs.attr1
    >>> au.convert_state(configs, read_only=True)
    >>> configs.attr1
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/xxxx/attrmap.py", line xxx, in __getattr__
        Get the (top level) `key-value` pair of `AttrMap` object like `dict`.
    AttributeError: No such attribute: attr1
    >>> au.convert_state(configs, read_only=False)
    >>> configs.attr1
    # Get an empty line, but the attribute attr1 is created.
    >>> type(configs.attr1)
    <class 'attrmap.attrmap.AttrMap'>
    >>> configs["attr3"].subattr1
    "subattr1"

    AttrMap supports the deepcopy:

    >>> from copy import deepcopy
    >>> configs = AttrMap(CONFIGS)
    >>> configs_new = deepcopy(configs)
    >>> configs is configs_new
    False # They do not share the same memory.
    >>> id(configs)
    140578368145776
    >>> id(configs_new)
    140578368434576
    >>> configs == configs_new
    True # But the attributes and values are the same.

    Users can delete the attributes with their corresponding values:

    >>> del configs.attr1
    >>> del configs["attr2"]
    >>> print(configs)
    Object Contains Following Attributes
    attr3:
            subattr1: subattr1
            subattr2:
                    subsubattr1: subsubattr1
    # Protecting users from unintentionally creating attributes.
    >>> au.convert_state(configs, read_only=True)
    >>> configs.attr1
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "xxxx/attrmap.py", line xxx, in __getattr__
        if key.startswith(self._prefix):
    AttributeError: No such attribute: attr1
    >>> configs.attr2
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/xxxx/attrmap.py", line xxx, in __getattr__
        if key.startswith(self._prefix):
    AttributeError: No such attribute: attr2
    >>> au.convert_state(configs, False)
    >>> configs.attr1
    # Empty line, but attribute `attr1` of type(AttrMap) has been created.
    >>> configs.attr2
    # Empty line, but attribute `attr2` of type(AttrMap) has been created.
    >>> print(configs)
    Object Contains Following Attributes
    attr3:
            subattr1: subattr1
            subattr2:
                    subsubattr1: subsubattr1
    attr1:
    attr2:

    .. NOTE:: `AttrMap` doesn't check the conflicts between
        the content of `source` and parsed file.

    .. Warning:: Due to `AttrMap` maintains properties and methods,
        some attribute cannot be accessed via attribute style, but they
        can still be accessed via `[""]` style. For example:

    >>> configs = AttrMap(readonly="unintentional modification")
    >>> au.is_read_only(configs)
    False
    >>> configs["readonly"]
    'unintentional modification'

    .. Warning:: Set the name of attributes to be the same as any python magic
        the method is discouraged, even if it can be accessed via dict-style.

    .. Warning:: The attribute start with `_` might be conflict with `AttrMap`
        reserved methods. If it's, your can access their values in dict-style.
    """
    def __init__(
        self,
        source: dict = None,
        path2file: os.PathLike = None,
        read_only: bool = False,
        **kwargs,
    ) -> None:
        super(AttrMap, self).__init__()
        self.__dict__["ATTRMAP_LEVEL"] = 0
        self.__dict__["ATTRMAP_PREFIX"] = "_ATTRMAP_PREFIX_"
        self.__dict__["READ_ONLY"] = False
        self.__dict__["RESERVED"] = {}
        self.__dict__["RESERVED"] = dir(self)
        if source is not None:
            self._build_from_dict(source)
        if kwargs:
            self._build_from_dict(kwargs)
        if path2file is not None:
            self._build_from_file(path2file)
        import attrmap.utils as au
        au.convert_state(self, read_only=read_only)

    @property
    def read_only(self) -> bool:
        """
        Return the state of `AttrMap` object.
        `True` is read-only and any modification to the object
        is not allowed, i.e., add or delete an attribute,
        change the value of any attribute.

        >>> configs = AttrMap(CONFIGS)
        >>> configs = configs.convert_state(read_only=True)
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
          File "/xxxx/attrmap.py", line x, in __setattr__
            raise AttributeError(
        AttributeError: A read only AttrMap instance is not allowed to modify \
            its attribute.
        # Try to modify the value of existing attribute:
        >>> configs.attr1 = "unintentional modification"
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "/xxxxx/attrmap.py", line x, in __setattr__
            raise AttributeError(
        AttributeError: A read only AttrMap instance is not allowed to modify \
            its attribute.
        >>> print(configs)
        Object Contains Following Attributes
         attr1: 1
         attr2: ['hello', ' ', 'world']
         attr3:
                subattr1: subattr1
                subattr2:
                        subsubattr1: subsubattr1

        .. Warning:: To reduce 'problematic' attributes,
            `read_only` is deprecated,
            use `attrmap.utils.is_read_only` instead.
        """
        warn("To reduce 'problematic' attributes, `read_only` is deprecated, "
             "use `attrmap.utils.is_read_only` instead.")
        return self.__dict__["READ_ONLY"]

    @property
    def readonly(self) -> bool:
        """
        Alias of `read_only`

        .. Warning:: To reduce 'problematic' attributes,
            `readonly` is deprecated,
            use `attrmap.utils.is_read_only` instead.
        """
        warn("To reduce 'problematic' attributes, `readonly` is deprecated, "
             "use `attrmap.utils.is_read_only` instead.")
        return self.read_only

    def todict(self) -> dict:
        """
        Convert to a python builtin dict, which does not
        share memory with AttrMap instance.
        The state (is read-only or not) will not influence this method.
        For example:

        >>> configs = AttrMap(CONFIGS)
        >>> configs_dict = configs.todict()
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

        .. Warning:: To reduce 'problematic' attributes,
            `todict` is deprecated,
            use `attrmap.utils.todict`
            or `attrmap.utils.to_dict`
            or `attrmap.utils.convert_to_dict` instead.
        """
        warn("To reducec 'problematic' attributes, todict is deprecated, "
             "use `attrmap.utils.todict` "
             "or `attrmap.utils.to_dict` "
             "or `attrmap.utils.convert_to_dict` instead.")
        result = {}
        for key, value in self.__dict__.items():
            value = value.todict() \
                if isinstance(value, AttrMap) else value
            if key.startswith(self._prefix):
                new_key = key.replace(self._prefix, "")
                result[new_key] = value
        return result

    def convert_state(self, read_only: bool = None):
        """
        Convert the state as read only or not.
        If `None` is passed (not recommended), the state
        will be revert from `True` to `False`
        or `False` to `True`. This method will return the self object,
        so the both two code snipts are equivalent:

        >>> configs = AttrMap(CONFIGS)
        >>> configs.convert_state(True)
        >>> configs_new = configs.convert_state(True)
        >>> id(configs) == id(configs_new)
        True

        .. Warning:: To reduce 'problematic' attributes,
            `convert_state` is deprecated,
            use `attrmap.utils.convert_state` instead.
        """
        warn("To reduce `problematic` attributes, "
             "`convert_state` is deprecated, "
             "use `attrmap.utils.convert_state` instead.")
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

    def merge_from(self, mapping=None, path2file: os.PathLike = None):
        """
        Allows users to merge from a file or a mappable object.
        NOTE The existing value will be overwrited.

        Args:
            mapping:
                An instance of dict or AttrMap.
            path2file:
                The path to the json or yaml file.

        Returns:
            self object.

        .. Warning:: To reduce 'problematic' attributes,
            `merge_from` is deprecated,
            use `attrmap.utils.merge_from` instead.
        """
        warn("To reduce `problematic` attributes, "
             "`merge_from` is deprecated, "
             "use `attrmap.utils.merge_from` instead.")
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
        """
        Get the (top level) keys of `AttrMap` object.

        Returns:
            keys: A list of keys.

        >>> configs = AttrMap(CONFIGS)
        >>> configs.keys()
        ['attr1', 'attr2', 'attr3']
        >>> type(configs.keys())
        <class 'list'>

        That is, only the top-level attribute names will be returned.
        Similarily:

        >>> configs['attr3'].keys() # equivalent to configs.attr3.keys()
        ['subattr1', 'subattr2']

        .. Warning:: To reduce 'problematic' attributes,
            `keys` is deprecated,
            use `attrmap.utils.get_keys` instead.
        """
        warn("To reduce 'problematic' attributes, "
             "`keys` is deprecated, "
             "use `attrmap.utils.get_keys` instead.")
        keys = filter(
            lambda x: x.startswith(self._prefix), self.__dict__.keys()
        )
        keys = map(lambda x: x.replace(self._prefix, ""), keys)
        return list(keys)

    def values(self) -> List[Any]:
        """
        Get the (top level) values of `AttrMap` object.
        The alias of `values` is `vals`.

        Returns:
            values: A list of values.

        >>> values = configs.values()
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

        .. Warning:: To reduce 'problematic' attributes,
            `keys` is deprecated,
            use `attrmap.utils.get_vals`
            or `attrmap.utils.get_values` instead.
        """
        warn("To reduce 'problematic' attributes, "
             "`values` is deprecated, "
             "use `attrmap.utils.get_vals` "
             "or `attrmap.utils.get_values` instead.")
        values = []
        for key in self.keys():
            values.append(self[key])
        return values

    vals = values

    def items(self) -> Iterable:
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

        .. Warning:: To reduce 'problematic' attributes,
            `items` is deprecated,
            use `attrmap.utils.get_items` instead.
        """
        warn("To reduce 'problematic' attributes, "
             "`items` is deprecated, "
             "use `attrmap.utils.get_items` instead.")
        return zip(self.keys(), self.vals())

    def contains(self, name: str) -> bool:
        """
        Check if `AttrMap` contains specific attribute. It's the core
        of python magic method `__contains__`, which support the for loop.

        >>> configs = AttrMap(CONFIGS)
        >>> for obj in configs:
        ...     print(obj)
        ... # End of for loop.
        ('attr1', 1)
        ('attr2', ['hello', ' ', 'world'])
        ('attr3', {'subattr1': 'subattr1', \
            'subattr2': {'subsubattr1': 'subsubattr1'}})

        .. Warning:: To reduce 'problematic' attributes,
            `contains` is deprecated,
            use `attrmap.utils.contains`
            or `in` syntax instead.
        """
        warn("To reduce 'problematic' attributes, "
             "`contains` is deprecated, "
             "use `attrmap.utils.contains` "
             "or `in` syntax instead.")
        return self.__contains__(name)

    def _update_level(self):
        for key, value in self.__dict__.items():
            if self._prefix not in key:
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
        if key in self.__dict__["RESERVED"]:
            self._reserved_warning(key)
        value = AttrMap(value) if isinstance(value, Mapping) else value
        self.__dict__[self._wrap_name(key)] = value
        self._update_level()

    def __getitem__(self, key: str) -> Any:
        return self.__getattr__(key)

    def __getattr__(self, key: str) -> Any:
        if not self._wrap_name(key) in self.__dict__.keys():
            import attrmap.utils as au
            if au.is_read_only(self):
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
        import attrmap.utils as au
        return iter(au.todict(self).items())

    def __contains__(self, item: str) -> bool:
        return self._wrap_name(item) in self.__dict__.keys()

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
        import attrmap.utils as au
        for key, value in au.get_items(self):
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

    def _check_modifiable(self):
        import attrmap.utils as au
        if au.is_read_only(self):
            raise AttributeError(
                f"Modifying the attributes of a read-only AttrMap instance is "
                f"not allowed."
            )

    def _reserved_warning(self, key: str):
        warn(
            f"AttrMap get an attribute `{key}` which is in the "
            f"reserved set {self.__dict__['RESERVED']}."
            f"You cannot access this attribute via attribute-style "
            f"accessing, but the dict style [''] still works.")


def merge_mapping(
    mapping: Union[AttrMap, dict],
    another: Union[AttrMap, dict],
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

    .. Warning:: `merge_mapping` is deprecated,
        use `attrmap.utils.merge_from_mapping` instead.
    """
    warn("`attrmap.attrmap.merge_mapping` is deprecated, "
         "use `attrmap.utils.merge_from_mapping` instead.")
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

    .. Warning:: `overwrite_mapping_from_file` is deprecated,
        use `attrmap.utils.merge_from_file` instead.
    """
    warn("`attrmap.attrmap.overwrite_mapping_from_file` is deprecated, "
         "use `attrmap.utils.merge_from_file` instead.")
    if not os.path.exists(path2file):
        raise FileNotFoundError(f"File {path2file} not found.")
    with open(path2file, 'r') as fp:
        if path2file.endswith(".yaml") or path2file.endswith(".yml"):
            mapping_file = yaml.safe_load(fp)
        if path2file.endswith(".json"):
            mapping_file = json.load(fp)
    mapping = merge_mapping(mapping, mapping_file)
    return mapping


AttributeMap = AttributeMapping = AttrMapping = AttrMap
