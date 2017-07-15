from nose.tools import eq_, raises
from ipypublish.utils import MockPath
from ipypublish.scripts import nbmerge, nbexport

    
class Test_main(object):
    def setup(self):
        self.file1 = MockPath('2test.ipynb',is_file=True,
        content=r"""{
 "cells": [
      {
       "cell_type": "markdown",
       "metadata": {},
       "source": ["hallo"]
      },
      {
       "cell_type": "code",
       "execution_count": 2,
       "metadata": {},
       "source": [
            "a=1\n",
            "print(a)"
           ],
           "outputs": [
            {
             "name": "stdout",
             "output_type": "stream",
             "text": ["1\n"]
            }
           ]
      }
     ],
 "metadata": {
      "test_name": "notebook1",
      "kernelspec": {
       "display_name": "Python 3",
       "language": "python",
       "name": "python3"
      },
      "language_info": {
       "codemirror_mode": {
        "name": "ipython",
        "version": 3
       },
       "file_extension": ".py",
       "mimetype": "text/x-python",
       "name": "python",
       "nbconvert_exporter": "python",
       "pygments_lexer": "ipython3",
       "version": "3.6.1"
      }},
     "nbformat": 4,
     "nbformat_minor": 2
}""")
        self.file2 = MockPath('1test.ipynb',is_file=True,
        content=r"""{
 "cells": [
      {
       "cell_type": "markdown",
       "metadata": {},
       "source": ["hallo"]
      },
      {
       "cell_type": "code",
       "execution_count": 2,
       "metadata": {},
       "source": [
            "a=1\n",
            "print(a)"
           ],
           "outputs": [
            {
             "name": "stdout",
             "output_type": "stream",
             "text": ["1\n"]
            }
           ]
      }
     ],
 "metadata": {
      "test_name": "notebook2",
      "kernelspec": {
       "display_name": "Python 3",
       "language": "python",
       "name": "python3"
      },
      "language_info": {
       "codemirror_mode": {
        "name": "ipython",
        "version": 3
       },
       "file_extension": ".py",
       "mimetype": "text/x-python",
       "name": "python",
       "nbconvert_exporter": "python",
       "pygments_lexer": "ipython3",
       "version": "3.6.1"
      }},
     "nbformat": 4,
     "nbformat_minor": 2
}""")
        self.directory = MockPath('dir1',structure=[self.file1,self.file2])

    def test_nbmerge_one_notebook(self):
        nb, path = nbmerge.merge_notebooks(self.file1)
        eq_(nb.metadata.test_name,"notebook1")
        eq_(len(nb.cells),2)

    def test_nbmerge_two_notebooks(self):
        nb, path = nbmerge.merge_notebooks(self.directory)
        eq_(nb.metadata.test_name,"notebook2")
        eq_(len(nb.cells),4)

    def test_nbexport_latex_empty(self):
        template = ''
        config = {}
        nb, path = nbmerge.merge_notebooks(self.file1)
        (body, resources), exe = nbexport.export_notebook(nb,'Latex',config,template)
        eq_(exe,'.tex')        
        eq_(body,'')

    def test_nbexport_latex_mkdown1(self):
        template = """
((* block markdowncell scoped *))
test123
((* endblock markdowncell *))
        """
        config = {}
        nb, path = nbmerge.merge_notebooks(self.file1)
        (body, resources), exe = nbexport.export_notebook(nb,'Latex',config,template)
        eq_(exe,'.tex')        
        eq_(body.strip(),'test123')

    def test_nbexport_latex_mkdown2(self):
        template = """
((*- extends 'display_priority.tplx' -*))
((* block markdowncell scoped *))
(((cell.source)))
((* endblock markdowncell *))
        """
        config = {}
        nb, path = nbmerge.merge_notebooks(self.file1)
        (body, resources), exe = nbexport.export_notebook(nb,'Latex',config,template)
        eq_(exe,'.tex')        
        eq_(body.strip(),'hallo')
        
    def test_nbexport_html_empty(self):
        template = ''
        config = {}
        nb, path = nbmerge.merge_notebooks(self.file1)
        (body, resources), exe = nbexport.export_notebook(nb,'HTML',config,template)
        eq_(exe,'.html')        
        eq_(body,'')
        
    def test_nbexport_html_mkdown1(self):
        template = """
{% block markdowncell scoped %}
test123
{% endblock markdowncell %}
        """
        config = {}
        nb, path = nbmerge.merge_notebooks(self.file1)
        (body, resources), exe = nbexport.export_notebook(nb,'HTML',config,template)
        eq_(exe,'.html')        
        eq_(body.strip(),'test123')

    def test_nbexport_html_mkdown2(self):
        template = """
{%- extends 'display_priority.tpl' -%}
{% block markdowncell scoped %}
{{cell.source}}
{% endblock markdowncell %}
        """
        config = {}
        nb, path = nbmerge.merge_notebooks(self.file1)
        (body, resources), exe = nbexport.export_notebook(nb,'HTML',config,template)
        eq_(exe,'.html')        
        eq_(body.strip(),'hallo')
