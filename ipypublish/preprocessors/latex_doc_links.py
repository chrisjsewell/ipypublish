import logging
import os
from binascii import a2b_base64
import sys
import json
from mimetypes import guess_extension

from six import string_types
import traitlets as traits
from nbconvert.preprocessors import Preprocessor


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


class LatexDocLinks(Preprocessor):
    """ a preprocessor to resolve file paths in the notebook:

    - retrieve external file paths from ipub metadata section,
    - resolve where they are, if the path is relative
    - make sure that the link points to a single folder
    - add 'external_file_paths' and 'bibliopath' (if present) to resources
    - extract attachments from input cells and rename their file links

    """

    metapath = traits.Unicode(
        '', help="the path to the meta data").tag(config=True)
    filesfolder = traits.Unicode(
        '', help="the folder to point towards").tag(config=True)
    extract_attachments = traits.Bool(
        True,
        help=("extract attachments "
              "(created by dragging and dropping files into markdown cells)")
    ).tag(config=True)
    output_attachment_template = traits.Unicode(
        "{unique_key}_{cell_index}_{key}{extension}"
    ).tag(config=True)

    def resolve_path(self, fpath, filepath):
        """resolve a relative path, w.r.t. another filepath """
        if not os.path.isabs(fpath):
            fpath = os.path.join(os.path.dirname(str(filepath)), fpath)
            fpath = os.path.abspath(fpath)

        return fpath

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
            Index of the cell being processed (see base.py)
        """
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

        logging.info('resolving external file paths' +
                     ' in ipub metadata to: {}'.format(self.metapath))
        external_files = []
        if 'ipub' in nb.metadata:

            # if hasattr(nb.metadata.ipub, 'files'):
            #     mfiles = []
            #     for fpath in nb.metadata.ipub.files:
            #         fpath = self.resolve_path(fpath, self.metapath)
            #         if not os.path.exists(fpath):
            #             logging.warning('file in metadata does not exist'
            #                             ': {}'.format(fpath))
            #         else:
            #             external_files.append(fpath)
            #         mfiles.append(os.path.join(
            # self.filesfolder, os.path.basename(fpath)))
            #
            #     nb.metadata.ipub.files = mfiles

            if hasattr(nb.metadata.ipub, 'bibliography'):
                bib = nb.metadata.ipub.bibliography
                bib = self.resolve_path(bib, self.metapath)
                if not os.path.exists(bib):
                    logging.warning('bib in metadata does not exist'
                                    ': {}'.format(bib))
                else:
                    external_files.append(bib)
                    resources['bibliopath'] = bib

                nb.metadata.ipub.bibliography = os.path.join(
                    self.filesfolder, os.path.basename(bib))

            if hasattr(nb.metadata.ipub, 'titlepage'):
                if hasattr(nb.metadata.ipub.titlepage, 'logo'):
                    logo = nb.metadata.ipub.titlepage.logo
                    logo = self.resolve_path(logo, self.metapath)
                    if not os.path.exists(logo):
                        logging.warning('logo in metadata does not exist'
                                        ': {}'.format(logo))
                    else:
                        external_files.append(logo)

                    nb.metadata.ipub.titlepage.logo = os.path.join(
                        self.filesfolder, os.path.basename(logo))

        resources.setdefault("external_file_paths", [])
        resources['external_file_paths'] += external_files

        for index, cell in enumerate(nb.cells):
            nb.cells[index], resources = self.preprocess_cell(
                cell, resources, index)

        return nb, resources
