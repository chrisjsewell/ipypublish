# See nbconvert/exporters/html.py:
DISPLAY_DATA_PRIORITY_HTML = (
    'application/vnd.jupyter.widget-state+json',
    'application/vnd.jupyter.widget-view+json',
    'application/javascript',
    'text/html',
    'text/markdown',
    'image/svg+xml',
    'text/latex',
    'image/png',
    'image/jpeg',
    'text/plain',
)
# See nbconvert/exporters/latex.py:
DISPLAY_DATA_PRIORITY_LATEX = (
    'text/latex',
    'image/svg+xml',  # this requires sphinx.ext.imgconverter
    'application/pdf',
    'image/png',
    'image/jpeg',
    'text/markdown',
    'text/plain',
)


def choose_output_type(output):
    """Choose appropriate output data types for HTML and LaTeX."""
    if output.output_type == 'stream':
        html_datatype = latex_datatype = 'ansi'
        text = output.text
        output.data = {'ansi': text[:-1] if text.endswith('\n') else text}
    elif output.output_type == 'error':
        html_datatype = latex_datatype = 'ansi'
        output.data = {'ansi': '\n'.join(output.traceback)}
    else:
        for datatype in DISPLAY_DATA_PRIORITY_HTML:
            if datatype in output.data:
                html_datatype = datatype
                break
        else:
            html_datatype = ', '.join(output.data.keys())
        for datatype in DISPLAY_DATA_PRIORITY_LATEX:
            if datatype in output.data:
                latex_datatype = datatype
                break
        else:
            latex_datatype = ', '.join(output.data.keys())
    return html_datatype, latex_datatype
