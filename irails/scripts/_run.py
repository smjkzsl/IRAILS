import os,importlib
from irails import  run as runserver 
from irails.config import IS_IN_irails

def main():
    if not IS_IN_irails:
        print(f"Run must run in the directory of irails")
        exit()
        
    module_path = 'main.py'
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_path, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        runserver(module.app,debug=True)
    else:
        print(f'please exec on project\'s root dir')
        exit()