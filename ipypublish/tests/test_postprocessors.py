import os
from ipypublish.postprocessors.pdfexport import PDFExport
from ipypublish.postprocessors.reveal_serve import RevealServer


def test_pdf_export(temp_folder):

    tex_content = """
\\documentclass{article}
\\begin{document}
hallo world
\\end{document}
"""

    tex_path = os.path.join(temp_folder, 'test.tex')
    pdf_path = os.path.join(temp_folder, 'test.pdf')

    with open(tex_path, 'w') as f:
        f.write(tex_content)

    pdfexport = PDFExport()
    pdfexport.postprocess(tex_content, 'text/latex', tex_path)

    assert os.path.exists(pdf_path)


def test_reveal_server():
    RevealServer()
    # TODO test reveal server runs correctly,
    # possibly use https://github.com/eugeniy/pytest-tornado
