import string


class DefaultFormatter(string.Formatter):

    def get_value(self, key, args, kwargs):
        # Handle a key not found
        try:
            val = super(DefaultFormatter, self).get_value(
                key, args, kwargs)
            # Python 3, 'super().get_field(field_name, args, kwargs)' works
        except (IndexError, KeyError):
            if str(key).endswith("_pre"):
                val = "@ipubreplace{above}{" + str(key) + "}"
            else:
                val = "@ipubreplace{below}{" + str(key) + "}"
        return val


def convert_format_str(template):

    temp_str = "\n".join(template)
    fmt = DefaultFormatter()
    outstr = fmt.format(temp_str)

    return outstr


if __name__ == "__main__":

    template = ["{{%- extends 'null.tpl' -%}}",
                "{{% block header %}}",
                "{{{{ nb.metadata | meta2yaml('#~~ ') }}}}",
                "{{% endblock header %}}",
                "{{% block codecell %}}",
                "#%%",
                "{{{{ super() }}}}",
                "{{% endblock codecell %}}",
                "{{% block in_prompt %}}{{% endblock in_prompt %}}",
                "{{% block input %}}{{{{ cell.metadata | meta2yaml('#~~ ') }}}}",  # noqa: E501
                "{{{{ cell.source | ipython2python }}}}",
                "{{% endblock input %}}",
                "{{% block markdowncell scoped %}}#%% [markdown]",
                "{{{{ cell.metadata | meta2yaml('#~~ ') }}}}",
                "{{{{ cell.source | comment_lines }}}}",
                "{{% endblock markdowncell %}}"
                ]

    print(convert_format_str(template))
