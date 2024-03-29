import json
from datetime import datetime, date
from json import JSONEncoder
import re
import os
from typing import Any, Callable, List, Optional
from .log import get_logger
_log=get_logger(__name__)

 

snake_case_re = re.compile("(?<!^)(?=[A-Z][a-z])")
controller_re = re.compile("([\\w]+)Controller")

_pluralizer = None

import mimetypes
 


def get_media_type(extension):
    """Get the media type for a given extension.

    Args:
        extension: The file extension.

    Returns:
        The media type, or None if the extension is not recognized.
    """

    return mimetypes.guess_type(extension)[0]

def get_controller_name(controller_name):
    """
    >>> get_controller_name("TestController")
    >>> 'Test'
    """
    return controller_re.match(controller_name).group(1)
 
def to_camel_case(x):
    """
    Converts variable_name to camel case notation.
    
    >>> to_camel_case('hello_world')
    >>> 'HelloWorld'

    """
    # Using the regex module to find all instances of an underscore followed by a letter
    # and then replacing that underscore with the uppercase of that letter.
    # Example: hello_world -> HelloWorld
    s = re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x )
    return s[0].upper() + s[1:]
def __init_inflect():
    import inflect
    global _pluralizer
    if not _pluralizer:
        _pluralizer=inflect.engine()
     
    return _pluralizer
def get_plural_name(name:str):
    """
        Return the plural of text, where text is a noun.

        If count supplied, then return text if count is one of:
            1, a, an, one, each, every, this, that

        otherwise return the plural.

        Whitespace at the start and end is preserved.

        >>> get_plural_name("horse")
        >>> 'horses'
    """
    _pluralizer = __init_inflect()
    return _pluralizer.plural(name.lower())
def get_singularize_name(name:str):
    """
    Return the singular of text, where text is a plural noun.

        If count supplied, then return the singular if count is one of:
            1, a, an, one, each, every, this, that or if count is None

        otherwise return text unchanged. 
        Whitespace at the start and end is preserved.  

        >>> get_singularize_name('horses')
        'horse'
        >>> get_singularize_name('knights')
        'knight'
    """
    _pluralizer = __init_inflect()
    return _pluralizer.singular_noun(name)

def get_snaked_name(_name:str):
    """
    Converts a string to snake_case format.
    :param name: string to be converted
    :return: the string in snake_case format
    >>> get_snaked_name("MyCount")
    >>> 'my_count'
    """
    # split the string at every occurrence of a capital letter that is not at the beginning of the string
    # and insert "_" in between each splitted portion
    return snake_case_re.sub("_", _name).lower()
def is_valid_filename(filename):
    if filename is None or len(filename) == 0:
        return False
    if len(filename) > 200:
        return False
    illegal_chars = set('/\\?%*:|"<>')
    if any(char in illegal_chars for char in filename):
        return False
    if ' ' in filename:
        return False
    return True

def ensure_line(filepath, line_to_add,create_if_not_exists=True):
    found = False
    lines = []
    if os.path.exists(filepath):
        # Read in the file
        with open(filepath, 'r') as file:
            lines = file.readlines()

            # Check if the line is already in the file
            for line in lines:
                if line.strip() == line_to_add.strip():
                    found = True
                    break
            if not found:# If the line is not in the file, add it
                lines.append('\n' + line_to_add.strip() + '\n')
                with open(filepath, 'w') as file:
                    file.writelines(lines)
                return True
    else:
        if create_if_not_exists:
            with open(filepath,'w') as file:
                file.write(line_to_add)
            return True  
        else:
            return False            
    
    
_datetime_regex = re.compile(
r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$'
)

_date_regex = re.compile(r'^\d{4}-\d{2}-\d{2}$')

_time_regex = re.compile(r'^\d{2}:\d{2}:\d{2}$')
def is_datetime_format(s):
    if not isinstance(s,str) or not str:
        return False 
    
    def is_valid_datetime_string(datetime_str):
        return bool(_datetime_regex.match(datetime_str))

    def is_valid_date_string(date_str):
        return bool(_date_regex.match(date_str))

    def is_valid_time_string(time_str):
        return bool(_time_regex.match(time_str))
    return is_valid_date_string(s) or is_valid_datetime_string(s) or is_valid_time_string(s)

class iJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)
 


def camelize_classname(base, tablename, table):
    """
    Produce a 'camelized' class name, e.g. 
    'words_and_underscores' -> 'WordsAndUnderscores'
    """

    return str(tablename[0].upper() + \
            re.sub(r'_([a-z])', lambda m: m.group(1).upper(), tablename[1:]))


def pluralize_collection(base, local_cls, referred_cls, constraint):
    """
    Produce an 'uncamelized', 'pluralized' class name, e.g. "
    "'SomeTerm' -> 'some_terms'
    
    """
    
    import inflect
    global _pluralizer
    if not _pluralizer:
        _pluralizer = inflect.engine()
    referred_name = referred_cls.__name__
    uncamelized = re.sub(r'[A-Z]',
                         lambda m: "_%s" % m.group(0).lower(),
                         referred_name)[1:]
    pluralized = _pluralizer.plural(uncamelized)
    return pluralized
def copy_attr(obj1:object, obj2:object ):
    """
        将obj1的属性复制到obj2（如果obj2有相同的属性）。
    """
    for key in dir(obj1):
        if not key.startswith("__") and hasattr(obj2, key):
            value   = getattr(obj1, key)
            # 如果属性值为None，则将属性值设置为空字符串 
            if   value:
                setattr(obj2, key, value)
             
def singleton(cls):
    instances = {}
    def get_instance(*args,**kwargs):
        if cls not in instances:
            instances[cls] = cls(*args,**kwargs)
        return instances[cls]
    return get_instance

def add_redirect_param(url: str, redirect_url: str,key='redirect') -> str:
    from urllib.parse import quote
    if redirect_url:
        redirect_url = quote(redirect_url)
    if "?" in url:
        return url + f"&{key}=" + redirect_url
    else:
        return url + f"?{key}=" + redirect_url
    
def update_manifest(manifest_path,section:str,value:Any,append:bool=False):
    import yaml
    try:
        changed = False
        with open(manifest_path, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader) 

        if not section in data: 
           
           data[section] = value
           changed = True
        else:
            cfg = data[section]
            if append:
                if isinstance(data[section],list): 
                    if not value in data[section]:  
                        data[section]=data[section]+[value] 
                        changed = True
                else:
                    data[section] = data[section] + str(value)
                    changed = True
            elif cfg != value:
                data[section] = value
                changed = True
         
        if changed:
            with open(manifest_path, "w") as f:
                yaml.dump(data, f) 

        return changed
    
    except Exception as e:
        _log.error(f'Error raised {e.args}')
        _log.error(f"Now please open {manifest_path} to modify {section}")
        if append:
            _log.error(f"append value {value}!")
        return False
    
def write_data_to_yaml(file_path,data,overwrite=False):
    """
    """
    import yaml
    to_write=False
    if os.path.exists(file_path) and os.path.isfile(file_path):
        if overwrite:
            to_write=True
    else:
        to_write=True
    if to_write:
        try:
            with open(file_path,'w') as f:
                yaml.dump(data,f)
            return True
        except Exception as e:
            _log.error(e.args)
            return False
    return to_write

def enable_app(app_name,is_enable=True):
        import yaml
        try:
            file = './configs/general.yaml'
 
            with open(file, "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
 
            arr_enabled = data['app']['enabled'] #none is enable all
            if not arr_enabled and is_enable:
                arr_enabled = [app_name] 
            else:
                if isinstance(arr_enabled,list) and is_enable:
                    arr_enabled.append(app_name) 
                elif isinstance(arr_enabled,list) and not is_enable:
                    if app_name in arr_enabled:
                        arr_enabled.remove(app_name)
                
            new_enabled = list(set(arr_enabled))

            data['app']['enabled'] = new_enabled
            with open(file, "w") as f:
                yaml.dump(data, f)
            _log.info(f"configs/general.yaml app.enabled has been added {app_name}!")
            return True
        except Exception as e:
            _log.error(f'an error raised {e.args}')
            _log.error(f"now please open configs/general.yaml to modify app.enabled to add {app_name}!")
            return