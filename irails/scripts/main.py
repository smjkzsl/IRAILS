import argparse
import sys
import importlib.util
import os.path
 
import os
import re
def _ensure_cli():
    executable = os.path.basename(sys.argv[0])
    if not executable.startswith('irails'):
        sys.argv[0] = 'irails'
_ensure_cli()

def is_dev_mode(path):
    dev_mode = True
    irails_srcs = ['__init__.py','_i18n.py','_loader.py','_utils.py','auth.py','base_controller.py','cbv.py']
    for src in irails_srcs:
        p = os.path.join(path,src)
        if not os.path.exists(p):
            dev_mode = False
    return dev_mode
curdir = os.path.abspath(os.curdir)
project_root = os.path.abspath(os.path.join(curdir,"../.."))
if is_dev_mode(os.path.join(project_root,'irails')): 
    sys.path.insert(-1, project_root)
    
sys.path.insert(-1,os.path.abspath(os.curdir))
from irails import __version__
def collect_features():
    """
    return files in current dir start with '_' no sub dir
    """
    
    dir_path = os.path.dirname(os.path.abspath(__file__))  
    py_files = []
    for file in os.listdir(dir_path): 
        if re.match('^_[\w]+\.py$', file) and (not file.startswith("__") and not file.endswith("__")):
            py_files.append(os.path.splitext(file)[0].lstrip('_')) 
    return py_files 

module_dir = os.path.dirname(__file__)
avalible_features = collect_features()

def main():
    
    parser = argparse.ArgumentParser(description='generator for irails')
    parser.add_argument('feature', choices=avalible_features, nargs='?', help='feature to run')
    parser.add_argument('--version', action='version', version=__version__, help='show the version of the program')
    parser.add_argument('args', nargs=argparse.REMAINDER)

    if not avalible_features:
        print(f"no feature on current dir")
        exit()
     
    args = parser.parse_args()
    
    if not args.feature:
        parser.print_help()
        exit()
    args.feature = '_' +args.feature
    
    module_path = os.path.join(module_dir, args.feature + '.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(args.feature, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.argv.pop(1)
        module.main()
    else:
        print(f'Error: {args.feature} feature does not exist')
    
if __name__ == '__main__': 
    main()
