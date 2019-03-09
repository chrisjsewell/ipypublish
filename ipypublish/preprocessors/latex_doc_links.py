import logging
import os
from binascii import a2b_base64
import sys
import json
import re
from mimetypes import guess_extension

from six import string_types
import traitlets as traits
from nbconvert.preprocessors import Preprocessor

if sys.version_info[0] == 2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse

logger = logging.getLogger("resolve_links")


def guess_extension_without_jpe(mimetype):
    """
    This function fixes a problem with '.jpe' extensions
    of jpeg images which are then not recognised by latex.
    For any other case, the function works in the same way
    as mimetypes.guess_extension
    """
    ext = guess_extension(mimetype)
    if ext == ".jpe":
        ext = ".jpeg"
    return ext


def is_hyperlink(path):
    """test whether a path is a hyperlink, e.g. https://site.org"""
    if urlparse(path).scheme:
        return True
    return False


def resolve_path(fpath, filepath):
    """resolve a relative path, w.r.t. another filepath """

    if is_hyperlink(fpath):
        return fpath

    if not os.path.isabs(fpath):
        fpath = os.path.join(os.path.dirname(str(filepath)), fpath)
        fpath = os.path.abspath(fpath)

    return os.path.normpath(fpath)


def extract_file_links(source, parent_path, redirect_path,
                       replace_nonexistent=False):
    """ extract local linked files

    Examples
    --------
    >>> source = '''## Cell with Linked Image
    ... ![test_image](subdir/logo_example.png)
    ... a [test_link](other_doc#a-link)'''
    >>> src, rpaths, npaths = extract_file_links(
    ...                             source, '/root/nb.ipynb', 'redirect', True)
    >>> print(src)
    ## Cell with Linked Image
    ![test_image](redirect/logo_example.png)
    a [test_link](redirect/other_doc#a-link)

    >>> print(rpaths[0])
    /root/subdir/logo_example.png
    >>> print(rpaths[1])
    /root/other_doc


    """
    # TODO is this robust enough
    regex = re.compile('\\[([^\\]]*)\\]\\(([^\\)^\\#]*)([^\\)]*)\\)')
    new_source = source
    redirected_paths = []
    nonexistent_paths = []
    for text, path, label in regex.findall(source):
        if path.startswith("attachment:"):
            continue
        if not path:  # internal links
            continue
        respath = resolve_path(path, parent_path)
        if is_hyperlink(respath):
            continue
        if not os.path.exists(respath):
            nonexistent_paths.append(respath)
        if os.path.exists(respath) or replace_nonexistent:
            redirected_paths.append(respath)
            new_path = os.path.normpath(os.path.join(
                redirect_path, os.path.basename(path)))
            new_source = new_source.replace(
                "[{0}]({1}{2})".format(text, path, label),
                "[{0}]({1}{2})".format(text, new_path, label))

    return new_source, redirected_paths, nonexistent_paths


class LatexDocLinks(Preprocessor):
    """ a preprocessor to resolve file paths in the notebook:

    1. Extract attachments from markdown cells, to resources['outputs'],
       and redirect their file links to self.filesfolder

    2. If nb.metadata.ipub.bibliography, create resources['bibliopath']

    3. Creates resources['external_file_paths'] = [] and adds to it:

        - local relative file paths referenced in markdown cells by
          '[](path/to/file)'
        - path to nb.metadata.ipub.bibliography (if present)
        - path to nb.metadata.ipub.titlepage.logo (if present)

    4. If self.redirect_external=True,
       redirects relative external file paths to self.filesfolder

    """

    metapath = traits.Unicode(
        '', help="the file path to the notebook").tag(config=True)
    filesfolder = traits.Unicode(
        '', help=("the folder path to dump dump internal content to "
                  "(e.g. images, etc)")).tag(config=True)
    redirect_external = traits.Bool(
        True,
        help="if True, redirect relatively linked paths to filesfolder"
    ).tag(config=True)
    extract_attachments = traits.Bool(
        True,
        help=("extract attachments stored in the notebook"
              "(created by dragging and dropping files into markdown cells)")
    ).tag(config=True)
    output_attachment_template = traits.Unicode(
        "{unique_key}_{cell_index}_{key}{extension}"
    ).tag(config=True)

    def preprocess_cell(self, cell, resources, cell_index):
        """
        Extract attachment

        Parameters
        ----------
        cell : nbformat.notebooknode.NotebookNode
            Notebook cell being processed
        resources : dict
            Additional resources used in the conversion process.  Allows
            preprocessors to pass variables into the Jinja engine.
        cell_index : int
            Index of the cell being processed
        """
        if cell.cell_type != "markdown":
            return cell, resources

        # extract local linked files
        source, rpaths, npaths = extract_file_links(
            cell.source, self.metapath, self.filesfolder)
        if self.redirect_external:
            cell.source = source
        resources['external_file_paths'].extend(rpaths)
        resources['unfound_file_paths'].extend(npaths)

        # extract attachments
        unique_key = resources.get('unique_key', 'attach')
        if 'attachments' in cell and self.extract_attachments:
            attachments = cell.pop('attachments')

            for key, attachment in attachments.items():
                # TODO this only works if there is a single MIME bundle
                (mime_type, data), = attachment.items()

                ext = guess_extension_without_jpe(mime_type)
                if ext is None:
                    ext = '.' + mime_type.rsplit('/')[-1]

                # replace the pointer to the attachment
                filepath = os.path.normpath(
                    os.path.join(self.filesfolder,
                                 self.output_attachment_template.format(
                                     unique_key=unique_key,
                                     cell_index=cell_index,
                                     key=os.path.splitext(key)[0],
                                     extension=ext))
                )
                if "source" in cell:
                    cell["source"] = cell["source"].replace(
                        'attachment:{}'.format(key), filepath)

                # code taken from nbconvert.ExtractOutputPreprocessor
                if (
                    not isinstance(data, string_types)
                    or mime_type == 'application/json'
                ):
                    # Data is either JSON-like and was parsed into a Python
                    # object according to the spec, or data is for sure
                    # JSON.
                    # In the latter case we want to go extra sure that
                    # we enclose a scalar string value into extra quotes by
                    # serializing it properly.
                    data = json.dumps(data)

                # Binary files are base64-encoded, SVG is already XML
                if mime_type in {
                        'image/png', 'image/jpeg', 'application/pdf'}:
                    # data is b64-encoded as text (str, unicode),
                    # we want the original bytes
                    data = a2b_base64(data)
                elif sys.platform == 'win32':
                    data = data.replace('\n', '\r\n').encode("UTF-8")
                else:
                    data = data.encode("UTF-8")

                if filepath in resources['outputs']:
                    raise ValueError(
                        "Your outputs have filename metadata associated "
                        "with them. Nbconvert saves these outputs to "
                        "external files using this filename metadata. "
                        "Filenames need to be unique across the notebook, "
                        "or images will be overwritten. The filename {} is"
                        " associated with more than one output. The second"
                        " output associated with this filename is in cell "
                        "{}.".format(filepath, cell_index)
                    )
                # In the resources, make the figure available
                resources['outputs'][filepath] = data

        return cell, resources

    def preprocess(self, nb, resources):
        """
        Preprocessing to apply on each notebook.
        """

        logger.info('resolving external file paths' +
                    ' in ipub metadata to: {}'.format(self.metapath))

        resources.setdefault("external_file_paths", [])
        resources.setdefault("unfound_file_paths", [])

        if 'ipub' in nb.metadata:

            if 'bibliography' in nb.metadata.ipub:
                bib = nb.metadata.ipub.bibliography
                bib = resolve_path(bib, self.metapath)
                if not os.path.exists(bib):
                    resources['unfound_file_paths'].append(bib)
                else:
                    resources['external_file_paths'].append(bib)
                    resources['bibliopath'] = bib

                if self.redirect_external:
                    nb.metadata.ipub.bibliography = os.path.join(
                        self.filesfolder, os.path.basename(bib))

            if "filepath" in nb.metadata.ipub.get('bibglossary', {}):
                gloss = nb.metadata.ipub.bibglossary.filepath
                gloss = resolve_path(gloss, self.metapath)
                if not os.path.exists(gloss):
                    resources['unfound_file_paths'].append(gloss)
                else:
                    resources['external_file_paths'].append(gloss)
                    resources['bibglosspath'] = gloss

                if self.redirect_external:
                    nb.metadata.ipub.bibglossary.filepath = os.path.join(
                        self.filesfolder, os.path.basename(gloss))

            if 'logo' in nb.metadata.ipub.get('titlepage', {}):
                logo = nb.metadata.ipub.titlepage.logo
                logo = resolve_path(logo, self.metapath)
                if not os.path.exists(logo):
                    resources['unfound_file_paths'].append(logo)
                else:
                    resources['external_file_paths'].append(logo)

                if self.redirect_external:
                    nb.metadata.ipub.titlepage.logo = os.path.join(
                        self.filesfolder, os.path.basename(logo))

        for index, cell in enumerate(nb.cells):
            nb.cells[index], resources = self.preprocess_cell(
                cell, resources, index)

        # filter unique
        resources['external_file_paths'] = list(
            set(resources['external_file_paths']))

        upaths = set(resources.pop("unfound_file_paths"))
        if upaths:
            logger.warning('referenced file(s) do not exist'
                           ': {}'.format(list(upaths)))

        return nb, resources
