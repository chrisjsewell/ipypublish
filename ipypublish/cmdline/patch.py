"""
This is a patch for ``click_completion``, that enables ``click.Option`` autocompletion callbacks.
See https://github.com/click-contrib/click-completion/pull/27/
"""
from click_completion.core import completion_configuration, match, Argument, Option, MultiCommand


def resolve_ctx(cli, prog_name, args, resilient_parsing=True):
    """

    Parameters
    ----------
    cli : click.Command
        The main click Command of the program
    prog_name : str
        The program name on the command line
    args : [str]
        The arguments already written by the user on the command line

    Returns
    -------
    click.core.Context
        A new context corresponding to the current command
    """
    ctx = cli.make_context(prog_name, list(args), resilient_parsing=resilient_parsing)
    args = ctx.protected_args + ctx.args
    while args and isinstance(ctx.command, MultiCommand):
        if not ctx.command.chain:
            cmd_name, cmd, args = ctx.command.resolve_command(ctx, args)
            if cmd is None:
                return ctx
            if hasattr(cmd, 'no_args_is_help'):
                no_args_is_help = cmd.no_args_is_help
                cmd.no_args_is_help = False
            ctx = cmd.make_context(cmd_name, args, parent=ctx, resilient_parsing=resilient_parsing)
            if hasattr(cmd, 'no_args_is_help'):
                cmd.no_args_is_help = no_args_is_help
            args = ctx.protected_args + ctx.args
        else:
            # Walk chained subcommand contexts saving the last one.
            while args:
                cmd_name, cmd, args = ctx.command.resolve_command(ctx, args)
                if cmd is None:
                    return ctx
                if hasattr(cmd, 'no_args_is_help'):
                    no_args_is_help = cmd.no_args_is_help
                    cmd.no_args_is_help = False
                sub_ctx = cmd.make_context(
                    cmd_name,
                    args,
                    parent=ctx,
                    allow_extra_args=True,
                    allow_interspersed_args=False,
                    resilient_parsing=resilient_parsing)
                if hasattr(cmd, 'no_args_is_help'):
                    cmd.no_args_is_help = no_args_is_help
                args = sub_ctx.args
            ctx = sub_ctx
            args = sub_ctx.protected_args + sub_ctx.args

    return ctx


def get_choices(cli, prog_name, args, incomplete):
    """

    Parameters
    ----------
    cli : click.Command
        The main click Command of the program
    prog_name : str
        The program name on the command line
    args : [str]
        The arguments already written by the user on the command line
    incomplete : str
        The partial argument to complete

    Returns
    -------
    [(str, str)]
        A list of completion results. The first element of each tuple is actually the argument to complete, the second
        element is an help string for this argument.
    """
    ctx = resolve_ctx(cli, prog_name, args)
    if ctx is None:
        return
    optctx = None
    if args:
        options = [param for param in ctx.command.get_params(ctx) if isinstance(param, Option)]
        arguments = [param for param in ctx.command.get_params(ctx) if isinstance(param, Argument)]
        for param in options:
            if not param.is_flag and args[-1] in param.opts + param.secondary_opts:
                optctx = param
        if optctx is None:
            for param in arguments:
                if (not incomplete.startswith('-') and (ctx.params.get(param.name) in (None, ()) or param.nargs == -1)):
                    optctx = param
                    break
    choices = []
    if optctx:
        choices += [c if isinstance(c, tuple) else (c, None) for c in optctx.type.complete(ctx, incomplete)]
        if not choices and hasattr(optctx, 'autocompletion') and optctx.autocompletion is not None:
            dynamic_completions = optctx.autocompletion(ctx=ctx, args=args, incomplete=incomplete)
            choices += [c if isinstance(c, tuple) else (c, None) for c in dynamic_completions]
    else:
        for param in ctx.command.get_params(ctx):
            if (completion_configuration.complete_options or
                    incomplete and not incomplete[:1].isalnum()) and isinstance(param, Option):
                for opt in param.opts:
                    if match(opt, incomplete):
                        choices.append((opt, param.help))
                for opt in param.secondary_opts:
                    if match(opt, incomplete):
                        # don't put the doc so fish won't group the primary and
                        # and secondary options
                        choices.append((opt, None))
        if isinstance(ctx.command, MultiCommand):
            for name in ctx.command.list_commands(ctx):
                command = ctx.command.get_command(ctx, name)
                if match(name, incomplete) and not command.hidden:
                    choices.append((name, command.get_short_help_str()))

    for item, help in choices:
        yield (item, help)
