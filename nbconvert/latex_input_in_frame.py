def wrap_latex(input, max_length=75, **kwargs):
    if len(input)>max_length:
        # remove double dollars, as they don't allow word wrap
        if len(input) > 3:
            if input[0:2]=='$$' and input[-2:]=='$$':
                input = input[1:-1]
        # change \left( and \right) to \bigg( and \bigg), as they allow word wrap
        input = input.replace(r'\left(',r'\big(')
        input = input.replace(r'\right)',r'\big)')
    
    return input

c = get_config() 
c.NbConvertApp.export_format = 'latex'   
c.TemplateExporter.filters = c.Exporter.filters = {'wrap_latex': wrap_latex}
c.Exporter.template_file = 'latex_input_in_frame.tplx'