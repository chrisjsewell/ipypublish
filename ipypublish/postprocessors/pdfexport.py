#!/usr/bin/env python
""" a module for exporting latex file to pdf
TODO could this be refactored as nbconvert postprocessor
"""
import os
import shutil
import tempfile
from subprocess import Popen, PIPE, STDOUT
import webbrowser

import six
from traitlets import Bool, Unicode

from ipypublish.postprocessors.base import IPyPostProcessor


class PDFExport(IPyPostProcessor):
    """ a post processor to convert tex to pdf using latexmk
    """
    @property
    def allowed_mimetypes(self):
        return ("text/latex")

    @property
    def requires_path(self):
        return True

    @property
    def logger_name(self):
        return "pdf-export"

    files_folder = Unicode(
        "_static",
        help="the path (relative to the main file path) "
        "containing external files"
    ).tag(config=True)

    convert_in_temp = Bool(
        False,
        help="run conversion in a temporary directory, "
        "and copy back only PDF file"
    ).tag(config=True)

    debug_mode = Bool(
        False,
        help="run in debug mode").tag(config=True)

    open_in_browser = Bool(
        False,
        help="launch a html page containing a pdf browser").tag(config=True)

    def run_postprocess(self, stream, mimetype, filepath, resources):
        """ should not be called directly

        Parameters
        ----------
        stream: str
            the main file contents
        filepath: None or pathlib.Path
            the path to the output file

        Returns
        -------
        stream: str
        filepath: None or pathlib.Path

        """
        self.logger.info('running pdf conversion')
        self._export_pdf(filepath)
        return stream, filepath, resources

    def _export_pdf(self, texpath):

        if not texpath.exists():
            self.handle_error(
                'the target file path does not exist: {}'.format(
                    texpath), IOError)

        texname = os.path.splitext(texpath.name)[0]
        # NOTE outdir was originally passed, but would this ever be different
        # to the texpath's parent

        external_files = texpath.parent.joinpath(self.files_folder)

        if external_files.exists() and not external_files.is_dir():
            self.handle_error(
                'the external folder path is not a directory: {}'.format(
                    external_files), IOError)

        self.check_exe_exists(
            'latexmk',
            'requires the latexmk executable to run. '
            'See http://mg.readthedocs.io/latexmk.html#installation',
        )

        if self.convert_in_temp:
            out_folder = tempfile.mkdtemp()
            try:
                exitcode = self._run_latexmk(
                    texpath, out_folder, external_files)
                if exitcode == 0:
                    shutil.copyfile(
                        os.path.join(out_folder, texname + '.pdf'),
                        str(texpath.parent.joinpath(texname + '.pdf')))
            finally:
                shutil.rmtree(out_folder)
        else:
            exitcode = self._run_latexmk(
                texpath, str(texpath.parent), external_files)

        if exitcode == 0:
            self.logger.info('pdf conversion complete')

            view_pdf = VIEW_PDF.format(
                pdf_name=texname.replace(' ', '%20') + '.pdf')
            view_pdf_path = texpath.parent.joinpath(texname + '.view_pdf.html')
            with view_pdf_path.open('w', encoding='utf-8') as fobj:
                fobj.write(six.u(view_pdf))
        else:
            self.handle_error(
                'pdf conversion failed: '
                'Try running with pdf-debug flag',
                RuntimeError)

        if self.open_in_browser:
            #  2 opens the url in a new tab
            webbrowser.open(view_pdf_path.as_uri(), new=2)

        return

    def _run_latexmk(self, texpath, out_folder, external_files):
        """ run latexmk conversion
        """
        # make sure tex file in right place
        outpath = os.path.join(out_folder, texpath.name)
        if os.path.dirname(str(texpath)) != str(out_folder):
            self.logger.debug('copying tex file to: {}'.format(
                os.path.join(str(out_folder), texpath.name)))
            shutil.copyfile(str(texpath), os.path.join(
                str(out_folder), texpath.name))

        # make sure the external files folder is in right place
        if external_files.exists():
            self.logger.debug('external files folder set')
            outfilespath = os.path.join(out_folder, str(external_files.name))
            if str(external_files) != str(outfilespath):
                self.logger.debug(
                    'copying external files to: {}'.format(outfilespath))
                if os.path.exists(outfilespath):
                    shutil.rmtree(outfilespath)
                shutil.copytree(str(external_files), str(outfilespath))

        # run latexmk in correct folder
        with change_dir(out_folder):
            latexmk = ['latexmk', '-xelatex', '-bibtex', '-pdf']
            latexmk += [] if self.debug_mode else ["--interaction=batchmode"]
            latexmk += [outpath]
            self.logger.info('running: ' + ' '.join(latexmk))

            def log_latexmk_output(pipe):
                for line in iter(pipe.readline, b''):
                    self.logger.info('latexmk: {}'.format(
                        line.decode("utf-8").strip()))

            process = Popen(latexmk, stdout=PIPE, stderr=STDOUT)
            with process.stdout:
                log_latexmk_output(process.stdout)
            exitcode = process.wait()  # 0 means success

        return exitcode


class change_dir:  # noqa: N801
    """Context manager for changing the current working directory"""

    def __init__(self, new_path):
        self.newPath = os.path.expanduser(new_path)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


VIEW_PDF = r"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
    <meta http-equiv="content-type" content="text/html; charset=windows-1252">
    <title>View PDF</title>

    <script type="text/javascript">
       var filepath = "{pdf_name}";
       var timer = null;

       function refresh(){{
          var d = document.getElementById("pdf"); // gets pdf-div
          d.innerHTML = '<iframe style="position: absolute; height: 100%; border: none" id="ipdf" src='+window.filepath+'  width="100%"></iframe>';
       }}

       function autoRefresh(){{
          timer = setTimeout("autoRefresh()", 20000);
          refresh();
       }}

       function manualRefresh(){{
          clearTimeout(timer);
          refresh();
       }}
       function check_pdf() {{
         var newfile = document.f.userFile.value;
         ext = newfile.substring(newfile.length-3,newfile.length);
         ext = ext.toLowerCase();
         if(ext != 'pdf') {{
           alert('You selected a .'+ext+
                 ' file; please select a .pdf file instead!'+filepath);
           return false; }}
         else
             alert(newfile);
             window.filepath = newfile;
             alert(filepath);
             refresh();
           return true; }}
    </script>

</head>
<body>
    <!-- <form name=f onsubmit="return check_pdf();"
        action='' method='POST' enctype='multipart/form-data'>
        <input type='submit' name='upload_btn' value='upload'>
        <input type='file' name='userFile' accept="application/pdf">
    </form> -->
    <button onclick="manualRefresh()">manual refresh</button>
    <button onclick="autoRefresh()">auto refresh</button>
    <div id="pdf"></div>
</body>
<script type="text/javascript">refresh();</script>
</html>
"""  # noqa: E501
