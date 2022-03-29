
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

def test_todict():
    configs = AttrMap(CONFIGS)
    # CONFIGS["attr3"]["subattr1"] = "new value"
    # assert configs.attr3.subattr1 == CONFIGS["attr3"]["subattr1"]
    d = configs.todict()
    d["attr1"] = "hello world"
    assert d["attr1"] == configs.attr1
