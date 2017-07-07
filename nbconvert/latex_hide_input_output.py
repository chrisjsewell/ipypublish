def remove_dollars(input, **kwargs):
    """remove dollars from start/end of file"""
    while input.startswith('$'):
        input = input[1:]
    while input.endswith('$'):
        input = input[0:-1]        
    return input

def first_para(input, **kwargs):
    r"""get only ttext before a \n (i.e. the fist paragraph)"""
    return input.split('\n')[0]
    
import re
from collections import OrderedDict

def write_roman(num):
    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num > 0:
                roman_num(num)
            else:
                break

    return "".join([a for a in roman_num(num)])

def repl(match):
    return write_roman(int(match.group(0)))
def create_key(input, **kwargs):
    """create sanitized key string which only contains lowercase letters,
    (semi)colons as c, underscores as u and numbers as roman numerals
    in this way the keys with different input should mainly be unique
    
    >>> sanitize_key('fig:A_10name56')
    'figcauxnamelvi'
    
    """
    input = re.compile(r"\d+").sub(repl, input)
    input = input.replace(':','c')
    input = input.replace(';','c')
    input = input.replace('_','u')    
    return re.sub('[^a-zA-Z]+', '', str(input)).lower()   
    
c = get_config() 
c.NbConvertApp.export_format = 'latex'   
c.TemplateExporter.filters = c.Exporter.filters = {'remove_dollars': remove_dollars,
                                                    'first_para': first_para,
                                                    'create_key': create_key}
c.Exporter.template_file = 'latex_hide_input_output.tplx'