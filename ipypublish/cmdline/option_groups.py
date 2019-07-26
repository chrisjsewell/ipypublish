""" replication of argparse add_argument_group method
adapted from https://github.com/pallets/click/issues/373

Usage::

    def f(*args, **kwargs):
        print(args, kwargs)


    SECTIONS = {"Primary": ["cmd1", "cmd2"], "Extras": ["cmd3", "cmd4"]}

    commands = [
        click.Command("cmd1", callback=f, help="first"),
        click.Command("cmd2", callback=f, help="second"),
        click.Command("cmd3", callback=f, help="third"),
        click.Command("cmd4", callback=f, help="fourth"),
    ]


    cli = SectionedGroup(commands={c.name: c for c in commands}, sections=SECTIONS)

"""
import click


class SectionedFormatter(click.formatting.HelpFormatter):

    def __init__(self, *args, sections, **kwargs):
        self.sections = sections
        super().__init__(*args, **kwargs)

    def write_dl(self, rows, *args, **kwargs):

        cmd_to_section = {}
        for section, commands in self.sections.items():
            for command in commands:
                cmd_to_section[command] = section

        sections = {}
        for subcommand, help in rows:
            sections.setdefault(cmd_to_section.get(subcommand, 'Commands'), []).append((subcommand, help))

        for section_name, rows in sections.items():
            if rows[0][0][0] == '-':
                super().write_dl(rows)
            else:
                with super().section(section_name):
                    super().write_dl(rows)


class SectionedContext(click.Context):

    def __init__(self, *args, sections, **kwargs):
        self.sections = sections
        super().__init__(*args, **kwargs)

    def make_formatter(self):
        """Creates the formatter for the help and usage output."""
        return SectionedFormatter(
            sections=self.sections,
            width=self.terminal_width,
            max_width=self.max_content_width,
        )


class SectionedGroup(click.Group):

    def __init__(self, *args, sections, **kwargs):
        self.sections = sections
        super().__init__(self, *args, **kwargs)

    def make_context(self, info_name, args, parent=None, **extra):
        """This function when given an info name and arguments will kick
        off the parsing and create a new :class:`Context`.  It does not
        invoke the actual command callback though.

        :param info_name: the info name for this invocation.  Generally this
                          is the most descriptive name for the script or
                          command.  For the toplevel script it's usually
                          the name of the script, for commands below it it's
                          the name of the script.
        :param args: the arguments to parse as list of strings.
        :param parent: the parent context if available.
        :param extra: extra keyword arguments forwarded to the context
                      constructor.
        """
        for key, value in click._compat.iteritems(self.context_settings):
            if key not in extra:
                extra[key] = value
        ctx = SectionedContext(self, info_name=info_name, parent=parent, sections=self.sections, **extra)
        with ctx.scope(cleanup=False):
            self.parse_args(ctx, args)
        return ctx

    def format_commands(self, ctx, formatter):
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue
            if cmd.hidden:
                continue

            commands.append((subcommand, cmd))

        # allow for 3 times the default spacing
        if len(commands):
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

            rows = []
            for subcommand, cmd in commands:
                help = cmd.get_short_help_str(limit)
                rows.append((subcommand, help))

            if rows:
                formatter.write_dl(rows)
