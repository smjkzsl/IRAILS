import argparse
import importlib
import unittest
import os,sys
from irails.config import is_in_app,is_in_irails,config
from irails._i18n import set_module_i18n
curdir = os.path.abspath(os.curdir)

def load_module(module_name:str,module_path:str):
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
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

def do_test_file(app_dir,file_name,print_out=None):
    if not os.path.isabs(file_name):
        test_files = _get_tests(app_dir)
        if file_name in test_files:
            file_name = test_files[file_name]
        else:
            raise FileNotFoundError(file_name)
    name,ext = os.path.splitext(os.path.basename(file_name))

    app_package = os.path.basename(app_dir)    
    module = load_module(f"{app_package}.tests.{name}",file_name)
    
    if module:
        
        set_module_i18n(module,f"{app_package}.tests.{name}")
        sys.argv = [file_name]
        kwargs = {'module':module,'exit':False}
        if print_out:
            kwargs['buffer']=print_out
        unittest.main(**kwargs)

def do_test_app(app_dir, print_out=None):
    
    test_files = _get_tests(app_dir)
    
    app_package_dir = os.path.dirname(app_dir)
    if not app_package_dir in sys.path:
        sys.path.insert(0,app_package_dir)
    for name in test_files:
        print(f"Starting test {test_files[name]}")
        do_test_file(app_dir, test_files[name])
    
    sys.path.remove(app_package_dir)

def get_all_enabled_apps():
    from irails._loader import collect_apps
    apps = collect_apps(do_load=False)
    return apps
def do_test_project(print_out=None): 
     
    response = input("Do you want to continue to test all apps? (y/n)")
    if response.lower() == "y":
         
        apps = get_all_enabled_apps() 
        for app in apps:
            dirs = app['package'].split('.')
            if len(dirs)==2:
                app_dir = os.path.join(curdir,dirs[0],dirs[1])
                do_test_app(app_dir=app_dir, print_out=print_out)
         
    elif response.lower() == "n":
        print("User chose to cancel.")
    else:
        print("Invalid input.")
     
def main():
    self_file = os.path.basename(__file__).lstrip("_").replace(".py",'')
    parser = argparse.ArgumentParser(
        usage=f"{sys.argv[0]} {self_file} [-h] [--verbose]",
          description='run project or app tests')
    parser.add_argument('-v','--verbose',action='store_true', help="full verbose with testing")  
    parser.add_argument('args', nargs=argparse.REMAINDER,help="test names in app `tests` dir...")
    args = parser.parse_args()  
    import io
    print_out = io.StringIO() if not args.verbose else None
    if print_out:
        sys.stdout = print_out
        sys.stderr = print_out
    if args.verbose:
        if '-v' in sys.argv:
            sys.argv.remove('-v')
        if '--verbose' in sys.argv:
            sys.argv.remove('--verbose')
    try:
        if args.args:
            for name in args.args:
                sys.argv.remove(name)
        if is_in_app(curdir):
            if args.args: 
                for name in args.args:
                    do_test_file(curdir,name,print_out)
            else:
                do_test_app(curdir,print_out)
        elif is_in_irails(curdir):
            do_test_project(print_out)
    except Exception as e:
        raise
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    if not print_out: 
        return 0
    else:
        import re
        pattern_starting = r"^Starting test .*$"
        pattern = r"Ran \d+ test in [\d\.]+s$" 
        result:str = print_out.getvalue()
        tested_line = []
        lines = result.split("\n")
        lnt = 0
        matched_fail = False
        cnt = 0
        ok = 0
        fail = 0
        for line in lines:
            
            if re.match(pattern=pattern_starting,string=line):
                cnt+=1
                if tested_line:
                    tested_line.append("\n") 
                tested_line.append(f'Starting {cnt}:~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                 
                tested_line.append(line) # Starting test filename..
                matched_fail = False
            elif re.match(pattern=pattern,string= line):
                tested_line.append(line)    #Ran 1 test in ..s
                status = lines[lnt+2]
                if status=="OK":
                    ok+=1
                
                tested_line.append(status) #OK or others
                matched_fail = False
            elif re.match(pattern=r"^FAIL:.*$", string=line) or re.match(pattern=r"^ERROR:",string=line)  :
                if not matched_fail:
                    fail+=1
                matched_fail=True
            elif  matched_fail:
                tested_line.append(line) 
            lnt += 1
    
    print("\n\ntest finished ,results:")
    print("====================================================")
    print("\n".join(tested_line))
    print(f"=========OK:{ok}====Fail:{fail}======================")