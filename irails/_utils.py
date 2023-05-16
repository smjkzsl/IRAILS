import json
from datetime import datetime, date
from json import JSONEncoder
import re
import os
snake_case_re = re.compile("(?<!^)(?=[A-Z][a-z])")
controller_re = re.compile("([\\w]+)Controller")

_pluralizer = None
def get_controller_name(controller_name):
    return controller_re.match(controller_name).group(1)
 
def to_camel_case(x):
    """转大驼峰法命名"""
    s = re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x )
    return s[0].upper() + s[1:]
def get_plural_name(name:str):
    import inflect
    global _pluralizer
    if not _pluralizer:
        _pluralizer = inflect.engine()
    return _pluralizer.plural(name)

def get_snaked_name(_name:str):
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

def ensure_line(filepath, line_to_add):
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
    else:
        with open(filepath,'w') as file:
            file.write(line_to_add)
        return True              
    # If the line is not in the file, add it
    if not found:
        lines.append('\n' + line_to_add.strip() + '\n')
        with open(filepath, 'w') as file:
            file.writelines(lines)
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
    "Produce a 'camelized' class name, e.g. "
    "'words_and_underscores' -> 'WordsAndUnderscores'"

    return str(tablename[0].upper() + \
            re.sub(r'_([a-z])', lambda m: m.group(1).upper(), tablename[1:]))


def pluralize_collection(base, local_cls, referred_cls, constraint):
    "Produce an 'uncamelized', 'pluralized' class name, e.g. "
    "'SomeTerm' -> 'some_terms'"
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