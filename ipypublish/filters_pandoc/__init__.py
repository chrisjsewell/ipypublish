"""
pandoc filters for the ipypublish format
"""
import panflute as pf
pf.elements.RAW_FORMATS.add("latex")
pf.elements.RAW_FORMATS.add("tex")
pf.elements.RAW_FORMATS.add("rst")
pf.elements.RAW_FORMATS.add("html5")