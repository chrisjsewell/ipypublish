from copy import deepcopy
import six

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser


class HTML2JSONParser(HTMLParser, object):
    """parses html content to a JSON object,
    of the form::

        {"attrs": {}, "data": [], "children": []}

    """

    _tag_key = "1_tag"
    _data_key = "2_data"
    _tag_attrs_key = "3_attributes"
    _children_key = "4_children"

    def __init__(
        self,
        ignore_tags=("head", "script", "style"),
        ignore_classes=("footer", "sphinxsidebar", "clearer"),
        rstrip_data=True,
        sort_class_attr=True,
        replace_data_lines=None,
        convert_charrefs=False,
    ):
        """parses html content to a JSON object,
        of the form::

            {"tag": "tag_name", "attrs": {}, "data": [], "children": []}

        Parameters
        ----------
        ignore_tags : list[str]
            HTML tags that will be ignored (and all their children)
        ignore_classes : list[str]
            HTML tags with one or more of these classes will be ignored (and all their children)
        rstrip_data : bool
            apply `rstrip()` to data text, and don't add if data == ''
        sort_class_attr : bool
            if an attribute is named 'class', its contents will be split and sorted
        replace_data_lines: None or dict
            mapping of data lines to replace (useful for mapping across different environment versions)
        convert_charrefs: bool
            If True, all character references (except the ones in script/style elements)
            are automatically converted to the corresponding Unicode characters.

        """
        if six.PY2:
            super(HTML2JSONParser, self).__init__()
        else:
            super(HTML2JSONParser, self).__init__(convert_charrefs=convert_charrefs)
        self._content = {}
        self._curr_tags = []
        self._curr_depth = 0
        self._ignore_depth = None
        self._rstrip_data = rstrip_data
        self._sort_class_attr = sort_class_attr
        self._ignore_tags = ignore_tags
        self._ignore_classes = set(ignore_classes)
        self._replace_data_lines = replace_data_lines or {}

    @property
    def parsed(self):
        return deepcopy(self._content)

    def reset(self):
        self._content = {}
        self._curr_tags = []
        self._curr_depth = 0
        self._ignore_depth = None
        super(HTML2JSONParser, self).reset()

    def _get_subcontent(self):
        sub_content = self._content
        for ptag in self._curr_tags:
            sub_content = sub_content[self._children_key][ptag]
        return sub_content

    def handle_starttag(self, tag, attrs):
        self._curr_depth += 1
        attr_dict = dict(attrs)
        classes = attr_dict.get("class", "").split()
        if self._ignore_depth is not None:
            return
        elif tag in self._ignore_tags or self._ignore_classes.intersection(classes):
            # we ignore any tags and data, until the current depth is less than the ignore depth
            self._ignore_depth = self._curr_depth
            return
        sub_content = self._get_subcontent()
        if self._sort_class_attr and "class" in attr_dict:
            attr_dict["class"] = sorted(classes)
        tag_dict = {self._tag_key: tag}
        if attr_dict:
            tag_dict[self._tag_attrs_key] = attr_dict
        sub_content.setdefault(self._children_key, []).append(tag_dict)
        self._curr_tags.append(len(sub_content[self._children_key]) - 1)

    def handle_endtag(self, tag):
        self._curr_depth -= 1

        if self._ignore_depth is not None:
            if self._ignore_depth > self._curr_depth:
                # print("exited ignore: {}".format(tag))
                self._ignore_depth = None
            return

        if tag != self._get_subcontent()[self._tag_key]:
            raise AssertionError(
                "{} != {} (current path: {})".format(
                    tag, self._get_subcontent()[self._tag_key], self._curr_tags
                )
            )
        self._curr_tags = self._curr_tags[:-1]

    def handle_data(self, data):
        if self._ignore_depth is not None:
            return
        if not data.strip():
            return
        data = data.splitlines()
        if self._rstrip_data:
            data = [d.rstrip() for d in data]
        if self._replace_data_lines:
            data = [self._replace_data_lines.get(d, d) for d in data]
        sub_content = self._get_subcontent()
        sub_content.setdefault(self._data_key, []).extend(data)

    def handle_entityref(self, name):
        pass

    def handle_charref(self, name):
        pass

    def handle_comment(self, data):
        pass
