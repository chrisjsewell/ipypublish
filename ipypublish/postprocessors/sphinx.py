import webbrowser
import shutil
import os
from subprocess import Popen, PIPE, STDOUT
from distutils.spawn import find_executable

from six import u
from traitlets import TraitError, validate, Bool, Dict, Unicode

from ipypublish import __version__
from ipypublish.postprocessors.base import IPyPostProcessor
from ipypublish.sphinx.utils import import_sphinx
from ipypublish.sphinx.create_setup import make_conf, make_index


# NOTE Interesting note about adding a directive to actually run python code
# https://stackoverflow.com/questions/7250659/how-to-use-python-to-programmatically-generate-part-of-sphinx-documentation

class RunSphinx(IPyPostProcessor):
    """ run sphinx to create an html output
    """
    @property
    def allowed_mimetypes(self):
        return ("text/restructuredtext",)

    @property
    def requires_path(self):
        return True

    @property
    def logger_name(self):
        return "run-sphinx"

    open_in_browser = Bool(
        True,
        help="launch a html page containing a pdf browser").tag(config=True)

    numbered = Bool(
        True,
        help="set :numbered: in toc, which numbers sections, etc"
    ).tag(config=True)

    show_prompts = Bool(
        True,
        help="whether to include cell prompts").tag(config=True)

    prompt_style = Unicode(
        '[{count}]:',
        help="the style of cell prompts").tag(config=True)

    @validate('prompt_style')
    def _valid_prompt_style(self, proposal):
        try:
            proposal.format(count=1)
        except TypeError:
            raise TraitError("prompt_style should be formatable by "
                             "`prompt_style.format(count=1)`")
        return proposal['value']

    conf_kwargs = Dict(
        help=("additional key-word arguments to be included in the conf.py "
              "as <key> = <val>")).tag(config=True)

    override_defaults = Bool(
        True,
        help="if True, conf_kwargs override default values").tag(config=True)

    nitpick = Bool(
        False,
        help="nit-picky mode, warn about all missing references"
    )

    def run_postprocess(self, stream, mimetype, filepath, resources):

        # check sphinx is available and the correct version
        try:
            import_sphinx()
        except ImportError as err:
            self.handle_error(err.msg, ImportError)

        self.logger.info("Creating Sphinx files")

        titlepage = {}
        if "titlepage" in resources.get("ipub", {}):
            titlepage = resources["ipub"]["titlepage"]
        #  includes ['author', 'email', 'supervisors', 'title', 'subtitle',
        #            'tagline', 'institution', 'logo']

        # create a conf.py
        kwargs = {} if not self.conf_kwargs else self.conf_kwargs
        kwargs["ipysphinx_show_prompts"] = self.show_prompts
        kwargs["ipysphinx_input_prompt"] = self.prompt_style
        kwargs["ipysphinx_output_prompt"] = self.prompt_style
        if "author" in titlepage:
            kwargs["author"] = titlepage["author"]
        if "tagline" in titlepage:
            kwargs["description"] = titlepage["tagline"]
        if "email" in titlepage:
            kwargs["email"] = titlepage["email"]

        conf_str = make_conf(overwrite=self.override_defaults, **kwargs)
        conf_path = filepath.parent.joinpath("conf.py")
        with conf_path.open("w", encoding="utf8") as f:
            f.write(u(conf_str))

        # create an index.rst
        toc_files = [filepath.name]

        toc_depth = 3
        title = None
        prolog = []
        epilog = []
        if "author" in titlepage:
            prolog.append(".. sectionauthor:: {0}".format(titlepage["author"]))
            prolog.append("")
        if "title" in titlepage:
            title = titlepage["title"]
        if "tagline" in titlepage:
            prolog.append(titlepage["tagline"])
        if "institution" in titlepage:
            for inst in titlepage["institution"]:
                epilog.append("| " + inst)

        epilog.append("")
        epilog.append('Created by IPyPublish (version {})'.format(__version__))

        toc = resources.get("ipub", {}).get("toc", {})
        if hasattr(toc, "get") and "depth" in toc:
            toc_depth = toc["depth"]

        index_str = make_index(toc_files,
                               toc_depth=toc_depth, header=title,
                               toc_numbered=self.numbered,
                               prolog="\n".join(prolog),
                               epilog="\n".join(epilog))

        index_path = filepath.parent.joinpath("index.rst")
        with index_path.open("w", encoding="utf8") as f:
            f.write(u(index_str))

        # clear any existing build
        build_dir = filepath.parent.joinpath('build/html')
        if build_dir.exists():
            # >> rm -r build/html
            shutil.rmtree(str(build_dir))
        build_dir.mkdir(parents=True)

        # run sphinx
        exec_path = find_executable('sphinx-build')
        args = [exec_path, "-b", "html"]
        if self.nitpick:
            args.append("-n")
        args.extend([str(filepath.parent.absolute()),
                     str(build_dir.absolute())])

        self.logger.info("running: " + " ".join(args))

        # this way overrides the logging
        # sphinx_build = find_entry_point("sphinx-build", "console_scripts",
        #                                 self.logger, "sphinx")

        def log_process_output(pipe):
            for line in iter(pipe.readline, b''):
                self.logger.info('{}'.format(
                    line.decode("utf-8").strip()))

        process = Popen(args, stdout=PIPE, stderr=STDOUT)
        with process.stdout:
            log_process_output(process.stdout)
        exitcode = process.wait()  # 0 means success

        if exitcode:
            self.logger.warn(
                "sphinx-build exited with code: {}".format(exitcode))

        if self.open_in_browser and not exitcode:
            # get entry path
            entry_path = filepath.parent.joinpath('build/html')
            entry_path = entry_path.joinpath(
                os.path.splitext(filepath.name)[0] + '.html')
            if entry_path.exists():
                #  2 opens the url in a new tab
                webbrowser.open(entry_path.as_uri(), new=2)
            else:
                self.handle_error(
                    "can't find {0} to open".format(entry_path), IOError)

        return stream, filepath, resources
