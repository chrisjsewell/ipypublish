import contextlib 
from functools import total_ordering 
from fnmatch import fnmatch 
import tempfile
import os

class _OpenRead(object):
    def __init__(self, linelist, encoding=None):
        self._linelist = linelist
        self._current_indx = 0
        self._encoding = encoding
    def read(self):
        text = '\n'.join(self._linelist)
        if self._encoding is not None:
            text = text.encode(self._encoding)
        return text
    def readline(self):
        if self._current_indx >= len(self._linelist):
            line = ''
        else:
            line = self._linelist[self._current_indx] + '\n'
        self._current_indx += 1
        if self._encoding is not None:
            line = line.encode(self._encoding)
        return line
    def __iter__(self):
        for line in self._linelist:
            if self._encoding is not None:
                line = line.encode(self._encoding)            
            yield line

class _OpenWrite(object):
    def __init__(self):
        self._str = ''
    def write(self,instr):
        self._str += instr
    def writelines(self, lines):
        for instr in lines:
            self.write(instr)

@total_ordering 
class MockPath(object):
    r"""a mock path, mimicking pathlib.Path, 
    supporting context open method for read/write
    
    Properties
    ----------
    path : str
        the path string
    is_file : bool
        if True is file, else folder
    content : str
        content of the file
    structure:
        structure of the directory

    Examples
    --------
    >>> file_obj = MockPath("path/to/test.txt",is_file=True,
    ...                     content="line1\nline2\nline3")
    ...
    >>> file_obj
    MockFile("test.txt")
    >>> file_obj.name
    'test.txt'
    >>> print(file_obj.to_string())
    File("test.txt") Contents:
    line1
    line2
    line3
    >>> file_obj.is_file()
    True
    >>> file_obj.is_dir()
    False
    >>> with file_obj.open('r') as f:
    ...     print(f.readline().strip())
    line1
    >>> with file_obj.open('w') as f:
    ...     f.write('newline1\nnewline2')
    >>> print(file_obj.to_string())
    File("test.txt") Contents:
    newline1
    newline2
    
    >>> with file_obj.maketemp() as temp:
    ...     with open(temp.name) as f:
    ...         print(f.readline().strip())
    newline1
    
    >>> dir_obj = MockPath(
    ...   structure=[{'dir1':[{'subdir':[]},file_obj]},{'dir2':[file_obj]},file_obj]
    ... )
    >>> dir_obj
    MockFolder("root")
    >>> dir_obj.name
    'root'
    >>> dir_obj.is_file()
    False
    >>> dir_obj.is_dir()
    True
    >>> print(dir_obj.to_string())
    Folder("root") 
      Folder("dir1") 
        Folder("subdir") 
        File("test.txt") 
      Folder("dir2") 
        File("test.txt") 
      File("test.txt") 

    >>> list(dir_obj.iterdir())
    [MockFolder("dir1"), MockFolder("dir2"), MockFile("test.txt")]
    
    >>> new = dir_obj.joinpath('dir3')
    >>> list(dir_obj.iterdir())
    [MockFolder("dir1"), MockFolder("dir2"), MockFile("test.txt")]

    >>> new.mkdir()
    >>> list(dir_obj.iterdir())
    [MockFolder("dir1"), MockFolder("dir2"), MockFolder("dir3"), MockFile("test.txt")]
        
    """
    def __init__(self, path='root', 
                 is_file=False,exists=True,
                 structure=[],content=''):
        self._path = path
        self.name = os.path.basename(path)
        self._exists = exists
        self._is_file = is_file
        self._is_dir = not is_file        
        self._content = content.splitlines()
        
        self.children = []
        for subobj in structure:
            if hasattr(subobj,'keys'):            
                key = list(subobj.keys())[0]
                self.children.append(MockPath(os.path.join(self._path,key),
                                              structure=subobj[key]))
            elif isinstance(subobj,MockPath):
                self.children.append(subobj)
            else:
                raise ValueError('items must be dict_like or MockPath: {}'.format(subobj))        
        
    def is_file(self):
        return self._is_file
    def is_dir(self):
        return self._is_dir
    def exists(self):
        return self._exists
                        
    def joinpath(self, path):
        if len(os.path.split(path)[0]):
            raise NotImplementedError
        for child in self.children:
            if child.name == path:
                return child
                
        # does not yet exist, must use touch or mkdir to convert to file or folder
        new = MockPath(path=os.path.join(self._path,path),exists=False)
        self.children.append(new)
        return new
        
    def mkdir(self):
        if not self._exists:
            self._is_file = False
            self._is_dir = True
            self._exists = True
    def touch(self):
        if not self._exists:
            self._is_file = True
            self._is_dir = False
            self._exists = True

    def iterdir(self):
        for subobj in sorted(self.children):
            if subobj.exists():
                yield subobj
    
    def glob(self, regex):
        for subobj in sorted(self.children):
            if fnmatch(subobj.name,regex):
                yield subobj     
    
    @contextlib.contextmanager    
    def maketemp(self):
        """make a named temporary file containing the file contents """
        if self.is_dir():
            raise IOError('[Errno 21] Is a directory: {}'.format(self.path))
        fileTemp = tempfile.NamedTemporaryFile(mode='w+',delete = False)
        try:
            fileTemp.write('\n'.join(self._content))
            fileTemp.close()
            yield fileTemp
        finally:
            os.remove(fileTemp.name)        
        
    @contextlib.contextmanager    
    def open(self, readwrite='r', encoding=None):
        if self.is_dir():
            raise IOError('[Errno 21] Is a directory: {}'.format(self.path))
            
        if 'r' in readwrite:
            obj = _OpenRead(self._content, encoding)
            yield obj
        elif 'w' in readwrite:
            obj = _OpenWrite()
            yield obj
            self._content = obj._str.splitlines()
        else:
            raise ValueError('readwrite should contain r or w')

    def __gt__(self,other):
        if not hasattr(other, 'name'):
            return NotImplemented
        return self.name > other.name
    def __eq__(self,other):
        if not hasattr(other, 'name'):
            return NotImplemented
        return self.name == other.name
        
    def _recurse_print(self, obj, text='',indent=0,indentlvl=2,file_content=False):
        indent += indentlvl
        for subobj in sorted(obj):
            if not subobj.exists():
                continue
            if subobj.is_dir():            
                text += ' '*indent + '{0}("{1}") \n'.format(self._folderstr, subobj.name)
                text += self._recurse_print(subobj.children,
                                indent=indent,file_content=file_content)
            else:
                if file_content:
                    sep = '\n'+' '*(indent+1)
                    text += ' '*indent + sep.join(['{0}("{1}") Contents:'.format(self._filestr,subobj.name)]+subobj._content) + '\n'
                else:
                    text += ' '*indent + '{0}("{1}") \n'.format(self._filestr,subobj.name)
            
        return text
        
    def to_string(self,indentlvl=2,file_content=False,color=False):
        """convert to string """
        if color:
            self._folderstr = colortxt('Folder','green')
            self._filestr = colortxt('File','blue')
        else:
            self._folderstr = 'Folder'
            self._filestr = 'File'
        
        if self.is_file():
            return '\n'.join(['{0}("{1}") Contents:'.format(self._filestr,self.name)]+self._content)
        elif self.is_dir():
            text = '{0}("{1}") \n'.format(self._folderstr,self.name)
            text += self._recurse_print(self.children,indentlvl=indentlvl,
                                        file_content=file_content)
            
            text = text[0:-1] if text.endswith('\n') else text
            return text
        else:
            return 'MockPath({})'.format(self.name)
        
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        if not self.exists():
            return 'MockVirtualPath("{}")'.format(self.name)
        elif self.is_dir():
            return 'MockFolder("{}")'.format(self.name)
        elif self.is_file():
            return 'MockFile("{}")'.format(self.name)
        else:
            return 'MockPath("{}")'.format(self.name)            
