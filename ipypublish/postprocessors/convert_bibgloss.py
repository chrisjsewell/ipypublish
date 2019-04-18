import os
import sys
from traitlets import Unicode
from ipypublish.postprocessors.base import IPyPostProcessor
from ipypublish.bib2glossary import BibGlossDB


class ConvertBibGloss(IPyPostProcessor):
    """ convert a bibglossary to the required format
    """
    @property
    def allowed_mimetypes(self):
        return None

    @property
    def requires_path(self):
        return True

    @property
    def logger_name(self):
        return "convert-bibgloss"

    encoding = Unicode(
        "utf8",
        help="the encoding of the input file"
    ).tag(config=True)

    resource_key = Unicode(
        "bibglosspath",
        help="the key in the resources dict containing the path to the file"
    ).tag(config=True)

    files_folder = Unicode(
        "_static",
        help="the path (relative to the main file path) to dump to"
    ).tag(config=True)

    def run_postprocess(self, stream, mimetype, filepath, resources):

        if "bibglosspath" not in resources:
            return stream, filepath, resources

        bibpath = resources["bibglosspath"]

        if not os.path.exists(str(bibpath)):
            self.logger.warning(
                "the bibglossary could not be converted, "
                "since its path does not exist: {}".format(bibpath))
            return stream, filepath, resources

        bibname, extension = os.path.splitext(os.path.basename(bibpath))
        outstr = None
        outext = None

        if extension in [".bib"]:
            if mimetype == "text/restructuredtext":
                pass
            elif mimetype == "text/latex":
                self.logger.info("converting bibglossary to tex")
                bibdb = BibGlossDB()
                bibdb.load_bib(path=str(bibpath), encoding=self.encoding)
                outstr = bibdb.to_latex_string()
                outext = ".tex"

        elif extension in [".tex"]:
            if mimetype == "text/latex":
                pass
            elif mimetype == "text/restructuredtext":
                self.logger.info("converting bibglossary to bibtex")
                bibdb = BibGlossDB()
                bibdb.load_tex(path=str(bibpath), encoding=self.encoding)
                outstr = bibdb.to_bib_string()
                outext = ".bib"

        else:
            self.logger.warning(
                "the bibglossary could not be converted, "
                "since its file extension was not one of: "
                "bib, tex")

        if outstr is None:
            return stream, filepath, resources

        if sys.version_info < (3, 0):
            outstr = unicode(outstr, encoding=self.encoding)  # noqa: F821

        output_folder = filepath.parent.joinpath(self.files_folder)
        if not output_folder.exists():
            output_folder.mkdir(parents=True)

        outfile = output_folder.joinpath(bibname + outext)
        self.logger.info("writing bibglossary: {}".format(outfile))
        with outfile.open("w", encoding=self.encoding) as fh:
            fh.write(outstr)

        self.logger.debug("finished")

        return stream, filepath, resources
