
from attrmap import AttrMap
import attrmap.utils as au
from copy import deepcopy as dcp
import pytest


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
        path2file=__file__.replace("test_attrmap.py", "test.json")
    )
    cfg_yaml = AttrMap(
        path2file=__file__.replace("test_attrmap.py", "test.yaml")
    )
    assert cfg_json == cfg_yaml


def test_merge_from():
    cfg_yaml = AttrMap(
        path2file=__file__.replace("test_attrmap.py", "test.yaml")
    )
    assert "language" in au.get_keys(cfg_yaml), au.get_keys(cfg_yaml)
    configs = AttrMap(dcp(CONFIGS))
    configs = au.merge_from_mapping(configs, cfg_yaml)
    for key in list(CONFIGS.keys()):
        assert key in au.get_keys(configs), au.get_keys(configs)
    for key in au.get_keys(cfg_yaml):
        assert key in au.get_keys(configs), au.get_keys(configs)


def test_read_only():
    configs = AttrMap(CONFIGS)
    au.convert_state(configs, read_only=True)
    assert au.is_read_only(configs)
    try:
        configs.attr1 = "hello world"
        assert False, au.is_read_only(configs)
    except AttributeError:
        pass


def test_str():
    start = ""
    configs = AttrMap(CONFIGS)
    string = f"Object Contains Following Attributes\n" \
             + f"{start} attr1: 1\n" \
             + f"{start} attr2: ['hello', ' ', 'world']\n" \
             + f"{start} attr3: \n" \
             + f"\t{start} subattr1: subattr1\n" \
             + f"\t{start} subattr2: \n" \
             + f"\t\t{start} subsubattr1: subsubattr1"
    assert string == str(configs), str(configs)


def test_contains():
    configs = AttrMap(CONFIGS)
    for key in CONFIGS.keys():
        assert au.contains(configs, key), key


def test_getitem():
    configs = AttrMap(CONFIGS)
    for key in CONFIGS.keys():
        val = configs[key]
        if isinstance(val, AttrMap):
            val = au.todict(val)
        assert val == CONFIGS[key], val


def test_keys():
    configs = AttrMap(CONFIGS)
    assert sorted(au.get_keys(configs)) == sorted(list(CONFIGS.keys())),\
        au.get_keys(configs)


def test_vals():
    configs = AttrMap(CONFIGS)
    attr_vals = au.get_vals(configs)
    dict_vals = CONFIGS.values()
    for attr_val, dict_val in zip(attr_vals, dict_vals):
        if isinstance(attr_val, AttrMap):
            attr_val = au.todict(attr_val)
        assert attr_val == dict_val, attr_val


def test_items():
    configs = AttrMap(CONFIGS)
    attr_items = au.get_items(configs)
    dict_items = CONFIGS.items()
    # dict_items = list(dict_items)
    for attr_it, dict_it in zip(attr_items, dict_items):
        assert attr_it[0] == dict_it[0], attr_it[0]
        val = attr_it[1]
        if isinstance(val, AttrMap):
            val = au.todict(val)
        assert val == dict_it[1], attr_it[1]


def test_delete_item():
    configs = AttrMap(CONFIGS)

    au.convert_state(configs, read_only=True)
    with pytest.raises(AttributeError):
        del configs.attr1
    assert hasattr(configs, "attr1")

    with pytest.raises(AttributeError):
        del configs.attr3.subattr2.subsubattr1
    assert hasattr(configs.attr3.subattr2, "subsubattr1")

    with pytest.raises(AttributeError):
        del configs.attr3.subattr1
    assert hasattr(configs.attr3, "subattr1")

    au.convert_state(configs, read_only=False)
    del configs.attr1
    au.convert_state(configs, read_only=True)
    assert not hasattr(configs, "attr1")
    au.convert_state(configs, read_only=False)
    del configs.attr3.subattr2.subsubattr1
    au.convert_state(configs, read_only=True)
    assert not hasattr(configs.attr3.subattr2, "subsubattr1")
    au.convert_state(configs, read_only=False)
    del configs.attr3["subattr1"]
    au.convert_state(configs, read_only=True)
    assert not hasattr(configs.attr3, "subattr1")
