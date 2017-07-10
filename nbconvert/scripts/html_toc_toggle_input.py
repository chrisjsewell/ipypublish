""" create html with a table of contents 
and toggleable input code cells

"""

c = get_config() 
c.NbConvertApp.export_format = 'html'   
c.TemplateExporter.filters = c.Exporter.filters = {}
c.Exporter.template_file = 'html/html_toc_toggle_input.tpl'