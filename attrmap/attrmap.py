r"""
Author:
    Yiqun Chen
Docs:
    An easy module for configuration.
"""

import os, copy, yaml, json
from typing import Union
from copy import deepcopy as dcp

class AttrMap(object):
    r"""
    """
    def __init__(
        self, 
        source: dict=None, 
        path2yaml: os.PathLike=None, 
        path2json: os.PathLike=None, 
        read_only: bool=False, 
        **kwargs, 
    ):
        super(AttrMap, self).__init__()
        self.__dict__["_ATTRMAP_LEVEL_"] = 0
        self.__dict__["_ATTRMAP_PREFIX_"] = "_ATTRMAP_PREFIX_"
        self.__dict__["_read_only"] = read_only
        if source is not None:
            self._build_from_dict(source)
        if kwargs:
            self._build_from_dict(kwargs)
        if path2yaml is not None:
            if os.path.exists(path2yaml):
                try:
                    with open(path2yaml, 'r') as fp:
                        source = yaml.safe_load(fp)
                        self._build_from_dict(source)
                except:
                    raise IOError(
                        f"Failed to load from: {path2yaml}."
                    )
            else:
                raise FileNotFoundError(
                    f"Failed to find: {path2yaml}."
                )
        if path2json is not None:
            if os.path.exists(path2json):
                try:
                    with open(path2json, 'r') as fp:
                        source = json.load(fp)
                        self._build_from_dict(source)
                except:
                    raise IOError(
                        f"Failed to load from such file: {path2json}."
                    )
            else:
                raise FileNotFoundError(
                    f"Failed to find such yaml file: {path2json}."
                )


    @property
    def read_only(self) -> bool:
        return self.__dict__["_read_only"]

    @property
    def readonly(self) -> bool:
        return self.read_only

    def todict(self):
        r"""
        Info:
            Convert to a python builtin dict.
        """
        trg_dict = {}
        _PREFIX_ = self.__dict__["_ATTRMAP_PREFIX_"]
        for key, value in self.__dict__.items():
            value = value.todict() \
                if isinstance(value, self.__class__) else value
            if key.startswith(_PREFIX_):
                new_key = key.replace(_PREFIX_, "")
                trg_dict[new_key] = value
        return trg_dict

    def convert_state(self, read_only: bool=None):
        r"""
        Info:
            Convert the state as read only or not.
        """
        if read_only is None:
            read_only = not self.readonly
        elif read_only not in [True, False]:
            raise ValueError(
                    f"Expect attribute read_only takes value "
                    f"from [True, False, None], but got {read_only}"
                )
        self.__dict__["_read_only"] = read_only
        for attr, value in self.__dict__.items():
            if isinstance(value, self.__class__):
                value.convert_state(read_only)
        return self


    def merge_from(self, mapping=None, path2yaml: os.PathLike=None):
        if mapping is not None:
            self = merge_mapping(self, mapping)
        if path2yaml is not None:
            self = overwrite_mapping_from_yaml(self, path2yaml)
        return self


    def keys(self):
        return self.todict().keys()


    def values(self):
        return self.todict().values()


    def items(self):
        return self.todict().items()


    def _update(self):
        _PREFIX_ = self.__dict__["_ATTRMAP_PREFIX_"]
        _ATTRMAP_LEVEL_ = self.__dict__["_ATTRMAP_LEVEL_"]
        for key, value in self.__dict__.items():
            if not _PREFIX_ in key:
                continue
            if isinstance(value, self.__class__):
                value.__dict__["_ATTRMAP_LEVEL_"] = _ATTRMAP_LEVEL_ + 1
                value._update()


    def _build_from_dict(self, src_dict: dict):
        for key, value in src_dict.items():
            self.__setattr__(key, value)
        

    def _get_name(self, name: str):
        prefix = self.__dict__['_ATTRMAP_PREFIX_']
        return f"{prefix}{str(name)}"


    def __setitem__(self, key, value):
        self.__setattr__(key, value)


    def __setattr__(self, key, value):
        if self.read_only:
            raise AttributeError(
                f"A read only AttrMap instance "
                f"is not allowed to modify its attribute."
            )
        value = self.__class__(value) if isinstance(value, dict) else value
        self.__dict__[self._get_name(key)] = value
        self._update()


    def __getitem__(self, key):
        return self.__getattr__(key)


    def __getattr__(self, key):
        if not self._get_name(key) in self.__dict__.keys():
            if self.read_only:
                raise AttributeError("No such attribute: {}".format(key))
            self.__dict__[self._get_name(key)] = self.__class__()
            self._update()
        return self.__dict__[self._get_name(key)]


    def __getstate__(self):
        return self.__dict__


    def __setstate__(self, state):
        self.__dict__.update(state)


    def __eq__(self, other):
        return self.__dict__ == other.__dict__


    def __iter__(self):
        return iter(self.todict().items())


    def __copy__(self):
        trg_dict = self.__class__()
        _PREFIX_ = self.__dict__["_ATTRMAP_PREFIX_"]
        for key, value in self.__dict__.items():
            if _PREFIX_ in key:
                key = key.replace(_PREFIX_, "")
                trg_dict[key] = value
        return trg_dict


    def __deepcopy__(self, memo):
        other = self.__class__()
        _PREFIX_ = self.__dict__["_ATTRMAP_PREFIX_"]
        for key, value in self.__dict__.items():
            if id(self) in memo:
                continue
            if _PREFIX_ in key:
                _key = key.replace(_PREFIX_, "")
                other[copy.deepcopy(_key)] = copy.deepcopy(value, memo)
        memo[id(self)] = self
        return other


    def __str__(self):
        start = "-"
        string = []
        if self._ATTRMAP_LEVEL_ == 0:
            string.append("* ATTRIBUTES *")
        for key, value in self.__dict__.items():
            if not self._PREFIX_ in key:
                continue
            substring = "{}{} {}: {}{}".format(
                "\t"*self.__dict__["_ATTRMAP_LEVEL_"], 
                start, 
                key.replace(self._PREFIX_, ""), 
                "\n" if isinstance(value, self.__class__) else "", 
                str(value), 
            )
            string.append(substring)
        string = "\n".join(string)
        return string


def merge_mapping(
    mapping: Union[AttrMap, dict], 
    another: Union[AttrMap, dict], 
) -> AttrMap:
    if isinstance(mapping, AttrMap):
        mapping = dcp(mapping).todict()
    if isinstance(another, AttrMap):
        another = dcp(another).todict()
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


def overwrite_mapping_from_yaml(
    mapping: AttrMap, path2yaml: os.PathLike
) -> AttrMap:
    if not os.path.exists(path2yaml):
        return mapping
    with open(path2yaml, 'r') as fp:
        mapping_yaml = yaml.load(fp, yaml.Loader)["mapping"]
    mapping = merge_mapping(mapping, mapping_yaml)
    return mapping


AttrMapping = AttrMap

