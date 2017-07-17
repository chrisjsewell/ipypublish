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

def _write_roman(num):
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

def _repl(match):
    return _write_roman(int(match.group(0)))
def create_key(input, **kwargs):
    """create sanitized key string which only contains lowercase letters,
    (semi)colons as c, underscores as u and numbers as roman numerals
    in this way the keys with different input should mainly be unique
    
    >>> create_key('fig:A_10name56')
    'figcauxnamelvi'
    
    """
    input = re.compile(r"\d+").sub(_repl, input)
    input = input.replace(':','c')
    input = input.replace(';','c')
    input = input.replace('_','u')    
    return re.sub('[^a-zA-Z]+', '', str(input)).lower()   
