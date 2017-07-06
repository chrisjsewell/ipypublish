def remove_dollars(input, **kwargs):
    while input.startswith('$'):
        input = input[1:]
    while input.endswith('$'):
        input = input[0:-1]        
    return input

c = get_config() 
c.NbConvertApp.export_format = 'latex'   
c.TemplateExporter.filters = c.Exporter.filters = {'remove_dollars': remove_dollars}
c.Exporter.template_file = 'latex_hide_input_output.tplx'