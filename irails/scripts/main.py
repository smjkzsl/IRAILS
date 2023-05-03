import argparse
import sys
import importlib.util
import os.path
 
import os
import re
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
    
    
    args.feature = '_' +args.feature
    
    module_path = os.path.join(module_dir, args.feature + '.py')
    if sys.argv[0]!='irails':
        sys.argv[0] = 'irails'
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
