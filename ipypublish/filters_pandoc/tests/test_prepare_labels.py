import io
import json
import panflute as pf
from jsonextended import edict
from six import u

from panflute import Element, Doc  # noqa: F401
from types import FunctionType  # noqa: F401

from ipypublish.filters_pandoc.prepare_labels import main


def apply_to_json(in_json, filter_func):
    # type: (dict, FunctionType) -> dict
    f = io.StringIO(u(json.dumps(in_json)))
    doc = pf.load(f)
    new_doc = filter_func(doc)  # type: Doc
    return new_doc.to_json()


def test_basic():
    """
    $a=1$ {#a b=$2$}

    ![a](a/b.jpg){b .x a=$1$ b=2}
    """
    in_json = {
        "meta": {},
        "pandoc-api-version": [1, 17, 5, 1],
        "blocks": [
            {"t": "Para",
                "c": [{"t": "Math", "c": [{"t": "InlineMath"}, "a=1"]},
                      {"t": "Space"},
                      {"t": "Str", "c": "{#a"},
                      {"t": "Space"},
                      {"t": "Str", "c": ".a"},
                      {"t": "Space"},
                      {"t": "Str", "c": "b="},
                      {"t": "Math", "c": [
                          {"t": "InlineMath"}, "2"]}, {"t": "Str", "c": "}"}]},
            {"t": "Para", "c": [
                {"t": "Image",
                    "c": [["b", ["x"], [["a", "$1$"], ["b", "2"]]],
                          [{"t": "Str", "c": "a"}], ["a/b.jpg", "fig:"]]
                 }]}]
    }

    out_json = apply_to_json(in_json, main)

    assert edict.diff(out_json, {
        "pandoc-api-version": [1, 17, 5,  1],
        "meta": {
            "$$references": {
                "t": "MetaMap",
                "c": {
                    "a": {
                        "t": "MetaMap",
                        "c": {
                            "type": {
                                "t": "MetaString",
                                "c": "Math"
                            },
                            "number": {
                                "t": "MetaString",
                                "c": "1"
                            }
                        }
                    },
                    "b": {
                        "t": "MetaMap",
                        "c": {
                            "type": {
                                "t": "MetaString",
                                "c": "Image"
                            },
                            "number": {
                                "t": "MetaString",
                                "c": "1"
                            }
                        }
                    }
                }
            }
        },
        "blocks": [
            {"t": "Para",
             "c": [
                 {"t": "Span",
                  "c": [
                      ["a", ["labelled-Math", "a"], [["b",  "2"]]],
                      [{"t": "Math",
                          "c": [{"t": "InlineMath"},  "a=1"]}]]
                  }]
             },
            {
                "t": "Para",
                "c": [
                    {
                        "t": "Image",
                        "c": [["b", ["x"],  [["a",   "$1$"],  ["b",   "2"]]],
                              [{"t": "Str",  "c": "a"}],
                              ["a/b.jpg",  "fig:"]]
                    }
                ]
            }
        ]
    }
    ) == {}


def test_multiple_on_line():
    """"
    $a=1$ {#a b=$2$} $g=3$ {#gid}

    ![a](a/b.jpg)
    """
    in_json = {
        "pandoc-api-version": [1, 17, 5, 1], "meta": {},
        "blocks": [
            {"t": "Para", "c": [
                {"t": "Math", "c": [{"t": "InlineMath"}, "a=1"]},
                {"t": "Space"},
                {"t": "Str", "c": "{#a"},
                {"t": "Space"},
                {"t": "Str", "c": "b="},
                {"t": "Math", "c": [
                    {"t": "InlineMath"}, "2"]},
                {"t": "Str", "c": "}"},
                {"t": "Space"},
                {"t": "Math", "c": [
                    {"t": "InlineMath"}, "g=3"]},
                {"t": "Space"},
                {"t": "Str", "c": "{#gid}"}]
             },
            {"t": "Para", "c": [
                {"t": "Image", "c": [
                    ["", [], []], [{"t": "Str", "c": "a"}],
                    ["a/b.jpg", "fig:"]]}]
             }]
    }

    out_json = apply_to_json(in_json, main)

    assert edict.diff(out_json, {
        "pandoc-api-version": [
            1, 17,  5, 1
        ],
        "meta": {
            "$$references": {
                "t": "MetaMap",
                "c": {
                    "a": {
                        "t": "MetaMap",
                        "c": {
                            "type": {
                                "t": "MetaString",
                                "c": "Math"},
                            "number": {
                                "t": "MetaString",
                                "c": "1"
                            }
                        }
                    },
                    "gid": {
                        "t": "MetaMap",
                        "c": {
                            "type": {
                                "t": "MetaString",
                                "c": "Math"},
                            "number": {
                                "t": "MetaString",
                                "c": "2"
                            }}}}}
        },
        "blocks": [
            {"t": "Para",
                "c": [
                    {"t": "Span",
                        "c": [
                            ["a", ["labelled-Math"], [["b",  "2"]]],
                            [{"t": "Math",
                                "c": [{"t": "InlineMath"},  "a=1"]}]]
                     },
                    {"t": "Space"},
                    {
                        "t": "Span",
                        "c": [["gid", ["labelled-Math"], []],
                              [{"t": "Math",
                                "c": [{"t": "InlineMath"},  "g=3"]}]]
                    }]
             },
            {"t": "Para",
                "c": [
                    {"t": "Image",
                        "c": [["", [], []],
                              [{"t": "Str",  "c": "a"}],
                              ["a/b.jpg",  "fig:"]]
                     }
                ]
             }]
    }) == {}


def test_with_tables():
    """
    Some text

    a b c
    - - -
    1 2 3
    4 5 6

    Table: Caption. {#tbl:id}
    """
    in_json = {
        "pandoc-api-version": [1, 17, 5, 1], "meta": {},
        "blocks": [
            {"t": "Para", "c": [
                {"t": "Str", "c": "Some"},
                {"t": "Space"},
                {"t": "Str", "c": "text"}]},
            {"t": "Table", "c": [
                [{"t": "Str", "c": "Caption."},
                 {"t": "Space"},
                 {"t": "Str", "c": "{#tbl:id}"}],
                [{"t": "AlignDefault"},
                 {"t": "AlignDefault"},
                 {"t": "AlignDefault"}],
                [0, 0, 0],
                [[{"t": "Plain", "c": [{"t": "Str", "c": "a"}]}],
                 [{"t": "Plain", "c": [{"t": "Str", "c": "b"}]}],
                 [{"t": "Plain", "c": [{"t": "Str", "c": "c"}]}]],
                [[[{"t": "Plain", "c": [{"t": "Str", "c": "1"}]}],
                  [{"t": "Plain", "c": [{"t": "Str", "c": "2"}]}],
                  [{"t": "Plain", "c": [{"t": "Str", "c": "3"}]}]],
                    [[{"t": "Plain", "c": [{"t": "Str", "c": "4"}]}],
                     [{"t": "Plain", "c": [{"t": "Str", "c": "5"}]}],
                     [{"t": "Plain", "c": [{"t": "Str", "c": "6"}]}]]]]}],
    }

    out_json = apply_to_json(in_json, main)

    assert edict.diff(
        out_json,
        {
            "pandoc-api-version": [1, 17, 5, 1],
            "meta": {
                "$$references": {
                    "t": "MetaMap",
                    "c": {
                        "tbl:id": {
                            "t": "MetaMap",
                            "c": {
                                "type": {
                                    "t": "MetaString",
                                    "c": "Table"
                                },
                                "number": {
                                    "t": "MetaString",
                                    "c": "1"
                                }
                            }
                        }}
                }
            },
            "blocks":
            [
                {"t": "Para", "c": [
                    {"t": "Str", "c": "Some"},
                    {"t": "Space"},
                    {"t": "Str", "c": "text"}
                ]
                },
                {"t": "Div", "c":
                 [
                     ["tbl:id", ["labelled-Table"], []],
                     [{"t": "Table",
                       "c": [
                           [{"t": "Str", "c": "Caption."},
                            {"t": "Space"}
                            ],
                           [
                               {"t": "AlignDefault"},
                               {"t": "AlignDefault"},
                               {"t": "AlignDefault"}
                           ],
                           [0, 0, 0],
                           [[{"t": "Plain", "c": [{"t": "Str", "c": "a"}]}],
                            [{"t": "Plain", "c": [{"t": "Str", "c": "b"}]}],
                            [{"t": "Plain", "c": [{"t": "Str", "c": "c"}]}]],
                           [[[{"t": "Plain",
                               "c": [{"t": "Str", "c": "1"}]}],
                             [{"t": "Plain",
                               "c": [{"t": "Str", "c": "2"}]}],
                             [{"t": "Plain",
                               "c": [{"t": "Str", "c": "3"}]}]],
                            [[{"t": "Plain",
                               "c": [{"t": "Str",  "c": "4"}]}],
                             [{"t": "Plain",
                               "c": [{"t": "Str", "c": "5"}]}],
                             [{"t": "Plain",
                               "c": [{"t": "Str",  "c": "6"}]}]]
                            ]
                       ]
                       }
                      ]]
                 }
            ]}) == {}
