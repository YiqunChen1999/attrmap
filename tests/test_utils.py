
import yaml
import json
from attrmap import AttrMap
from copy import deepcopy as dcp
import pytest

from attrmap.utils import (
    contains,
    convert_state,
    get_items,
    get_keys,
    get_vals,
    is_modifiable,
    is_read_only,
    merge_from,
    todict)


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


def test_attrmap():
    configs = AttrMap(CONFIGS)
    cfg = AttrMap(attr1=1)
    cfg.attr2 = dcp(CONFIGS["attr2"])
    cfg.attr3.subattr2.subsubattr1 = "subsubattr1"
    cfg.attr3.subattr1 = "subattr1"

    assert cfg == configs


def test_build_from_file():
    cfg_json = AttrMap(
        path2file=__file__.replace("test_utils.py", "test.json")
    )
    cfg_yaml = AttrMap(
        path2file=__file__.replace("test_utils.py", "test.yaml")
    )
    assert cfg_json == cfg_yaml


def test_merge_from():
    path2file = __file__.replace("test_utils.py", "test.yaml")
    cfg_yaml = AttrMap(path2file=path2file)
    assert "language" in get_keys(cfg_yaml), get_keys(cfg_yaml)
    configs = AttrMap(dcp(CONFIGS))
    merge_from(configs, cfg_yaml)
    for key in list(CONFIGS.keys()):
        assert key in get_keys(configs), get_keys(configs)
    for key in get_keys(cfg_yaml):
        assert key in get_keys(configs), get_keys(configs)

    with open(path2file, 'r') as fp:
        mapping_file = yaml.safe_load(fp)
    configs = AttrMap()
    merge_from(configs, path2file=path2file)
    todict(configs) == mapping_file


def test_read_only():
    configs = AttrMap(CONFIGS)
    convert_state(configs, True)
    assert configs.readonly is is_read_only(configs)
    assert configs.readonly is not is_modifiable(configs)
    try:
        configs.attr1 = "hello world"
        assert False, configs.readonly
    except AttributeError:
        pass


def test_to_dict():
    configs = AttrMap(CONFIGS)
    configs = todict(configs)
    assert configs == CONFIGS


def test_convert_state():
    configs = AttrMap(CONFIGS)
    _configs = convert_state(configs, read_only=True)
    assert configs is _configs
    assert is_read_only(configs) is True
    convert_state(configs, read_only=False)
    assert is_read_only(configs) is False


def test_contains():
    configs = AttrMap(CONFIGS)
    for key in CONFIGS.keys():
        assert contains(configs, key), key
        assert key in configs


def test_getitem():
    configs = AttrMap(CONFIGS)
    for key in CONFIGS.keys():
        val = configs[key]
        if isinstance(val, AttrMap):
            val = todict(val)
        assert val == CONFIGS[key], val


def test_keys():
    configs = AttrMap(CONFIGS)
    assert sorted(list(CONFIGS.keys())) \
           == sorted(get_keys(configs)),\
           configs.keys()


def test_vals():
    configs = AttrMap(CONFIGS)
    attr_vals = get_vals(configs)
    dict_vals = CONFIGS.values()
    for attr_val, dict_val in zip(attr_vals, dict_vals):
        if isinstance(attr_val, AttrMap):
            attr_val = todict(attr_val)
        assert attr_val == dict_val, attr_val


def test_items():
    configs = AttrMap(CONFIGS)
    attr_items = get_items(configs)
    dict_items = CONFIGS.items()
    # dict_items = list(dict_items)
    for attr_it, dict_it in zip(attr_items, dict_items):
        assert attr_it[0] == dict_it[0], attr_it[0]
        val = attr_it[1]
        if isinstance(val, AttrMap):
            val = todict(val)
        assert val == dict_it[1], attr_it[1]


def test_delete_item():
    configs = AttrMap(CONFIGS)

    convert_state(configs, read_only=True)
    with pytest.raises(AttributeError):
        del configs.attr1
    assert hasattr(configs, "attr1")

    with pytest.raises(AttributeError):
        del configs.attr3.subattr2.subsubattr1
    assert hasattr(configs.attr3.subattr2, "subsubattr1")

    with pytest.raises(AttributeError):
        del configs.attr3.subattr1
    assert hasattr(configs.attr3, "subattr1")

    convert_state(configs, read_only=False)
    del configs.attr1
    convert_state(configs, read_only=True)
    assert not hasattr(configs, "attr1")
    convert_state(configs, read_only=False)
    del configs.attr3.subattr2.subsubattr1
    convert_state(configs, read_only=True)
    assert not hasattr(configs.attr3.subattr2, "subsubattr1")
    convert_state(configs, read_only=False)
    del configs.attr3["subattr1"]
    convert_state(configs, read_only=True)
    assert not hasattr(configs.attr3, "subattr1")
