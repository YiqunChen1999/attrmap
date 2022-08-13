
from collections import UserDict
from attrmap import AttrMap
from copy import deepcopy as dcp


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
    assert "language" in cfg_yaml.keys(), cfg_yaml.keys()
    configs = AttrMap(dcp(CONFIGS))
    configs.merge_from(cfg_yaml)
    for key in list(CONFIGS.keys()):
        assert key in configs.keys(), configs.keys()
    for key in cfg_yaml.keys():
        assert key in configs.keys(), configs.keys()

def test_read_only():
    configs = AttrMap(CONFIGS)
    configs.convert_state(True)
    assert configs.readonly
    try:
        configs.attr1 = "hello world"
        assert False, configs.readonly
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
    assert string == str(configs) == repr(configs), str(configs)

def test_contains():
    configs = AttrMap(CONFIGS)
    for key in CONFIGS.keys():
        assert configs.contains(key), key

def test_getitem():
    configs = AttrMap(CONFIGS)
    for key in CONFIGS.keys():
        val = configs[key]
        if isinstance(val, AttrMap):
            val = val.todict()
        assert val == CONFIGS[key], val

def test_keys():
    configs = AttrMap(CONFIGS)
    assert sorted(configs.keys()) == sorted(list(CONFIGS.keys())),\
        configs.keys()

def test_vals():
    configs = AttrMap(CONFIGS)
    attr_vals = configs.values()
    dict_vals = CONFIGS.values()
    for attr_val, dict_val in zip(attr_vals, dict_vals):
        if isinstance(attr_val, AttrMap):
            attr_val = attr_val.todict()
        assert attr_val == dict_val, attr_val

def test_items():
    configs = AttrMap(CONFIGS)
    attr_items = configs.items()
    dict_items = CONFIGS.items()
    # dict_items = list(dict_items)
    for attr_it, dict_it in zip(attr_items, dict_items):
        assert attr_it[0] == dict_it[0], attr_it[0]
        val = attr_it[1]
        if isinstance(val, AttrMap):
            val = val.todict()
        assert val == dict_it[1], attr_it[1]


def test_delete_item():
    configs = AttrMap(CONFIGS)
    configs.convert_state(read_only=True)
    del configs.attr1
    assert not hasattr(configs, "attr1")
    del configs.attr3.subattr2.subsubattr1
    assert not hasattr(configs.attr3.subattr2, "subsubattr1")
    del configs.attr3["subattr1"]
    assert not hasattr(configs.attr3, "subattr1")
