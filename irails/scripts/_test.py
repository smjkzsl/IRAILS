import importlib
import unittest
import os,sys
from irails.config import is_in_app,is_in_irails,config
curdir = os.path.abspath(os.curdir)

def load_module(module_name:str,module_path:str):
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None
def _get_tests(_root_path):
    all_files = {}
    for root, dirs, files in os.walk(os.path.join(_root_path,'tests')):
        for file in files:
            name,ext = os.path.splitext(file)
            file_path = os.path.join(root, file)
            if file.endswith('.py') and file.startswith('test_'):
                all_files[name] = file_path
    return all_files
def do_test_app():
    test_files = _get_tests(curdir)
    for name in test_files:
        print(f"Starting test {test_files[name]}")
        module = load_module(name,test_files[name])
        if module:
            sys.argv = [test_files[name]]
            unittest.main(module=module,exit=False )

def do_test_project():
    unittest.main(exit=False)

def main():
    
    if is_in_app(curdir):
        
        do_test_app()
    elif is_in_irails(curdir):
        do_test_project()

    
    pass