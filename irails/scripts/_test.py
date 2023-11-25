import argparse
import importlib
from typing import List
import unittest
import os,sys
import irails
from irails.config import is_in_app,is_in_irails ,ROOT_PATH
from irails._i18n import set_module_i18n

curdir = os.path.abspath(os.curdir)

test_results:List[unittest.result.TestResult] = []

def _get_tests(_root_path):
    all_files = {}
    for root, dirs, files in os.walk(os.path.join(_root_path,'tests')):
        for file in files:
            name,ext = os.path.splitext(file)
            file_path = os.path.join(root, file)
            if file.endswith('.py') and file.startswith('test_'):
                all_files[name] = file_path
    return all_files

def do_test_file(app_dir,file_name  )->unittest.result.TestResult:

    os.chdir(ROOT_PATH)
    app_package = os.path.basename(app_dir)    
    app_package_dir = os.path.dirname(app_dir) 
    if not app_package_dir in irails.apps.__path__:
        irails.apps.__path__.append(app_package_dir)    
    if not os.path.isabs(file_name):
        test_files = _get_tests(app_dir)
        if file_name in test_files:
            file_name = test_files[file_name]
        else:
            raise FileNotFoundError(file_name)
    name,ext = os.path.splitext(os.path.basename(file_name))  
    if not app_package_dir in sys.path:
        sys.path.insert(0,app_package_dir) 
    module_package=f"irails.apps.{app_package}.tests.{name}"
    sys.argv = [file_name]
    print(f"Starting test {file_name}")
    cls = unittest.TestProgram(module=module_package,exit=False) 
    test_results.append(cls.result) 
    return cls.result 

def do_test_app(app_dir ): 
    

    test_files = _get_tests(app_dir) 
    
    for name in test_files: 
        do_test_file(app_dir, test_files[name]) 

def get_all_enabled_apps():
    from irails._loader import collect_apps
    apps = collect_apps(do_load=False)
    return apps

def do_test_project( ): 
     
    response = input("Do you want to continue to test all apps? (y/n)")
    if response.lower() == "y":
         
        apps = get_all_enabled_apps() 
        for app in apps:
            dirs = app['package'].split('.')
            if len(dirs)==2:
                app_dir = os.path.join(curdir,dirs[0],dirs[1])
                do_test_app(app_dir=app_dir )
         
    elif response.lower() == "n":
        print("User chose to cancel.")
    else:
        print("Invalid input.")
     
def main():
    self_file = os.path.basename(__file__).lstrip("_").replace(".py",'')
    parser = argparse.ArgumentParser(
        usage=f"{sys.argv[0]} {self_file} [-h] ",
          description='run project or app tests')
    
    parser.add_argument('args', nargs=argparse.REMAINDER,help="test names in app `tests` dir...")
    args = parser.parse_args()  
    
    
    try:
        if args.args:
            for name in args.args:
                sys.argv.remove(name)
        if is_in_app(curdir):
            if args.args: 
                for name in args.args:
                    do_test_file(curdir,name)
            else:
                do_test_app(curdir)
        elif is_in_irails(curdir):
            do_test_project()
    except Exception as e:
        raise
 
    ok = 0
    fail = 0
     
    cnt = len(test_results)
        
    print(f"count test:{cnt}")
    for ret in test_results:
        if ret.wasSuccessful():
            ok+=1
        else:
            fail+=1
      
    print(f"========= OK:{ok} ==== Fail:{fail} =====================")