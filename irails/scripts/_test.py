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
def do_test_app(app_dir, print_out):
    
    test_files = _get_tests(app_dir)
    for name in test_files:
        print(f"Starting test {test_files[name]}")
        module = load_module(name,test_files[name])
        if module:
            sys.argv = [test_files[name]]
            unittest.main(module=module,exit=False,buffer=print_out )
    
    
def get_all_enabled_apps():
    from irails._loader import _load_apps
    apps = _load_apps(do_load=False)
    return apps
def do_test_project(print_out): 
    _old_stdout = sys.stdout
    _old_stderr = sys.stderr
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    response = input("Do you want to continue to test all apps? (y/n)")
    if response.lower() == "y":
        sys.stdout = _old_stdout
        sys.stderr = _old_stderr
        apps = get_all_enabled_apps() 
        for app in apps:
            dirs = app.split('.')
            if len(dirs)==2:
                app_dir = os.path.join(curdir,dirs[0],dirs[1])
                do_test_app(app_dir=app_dir, print_out=print_out)
         
    elif response.lower() == "n":
        print("User chose to cancel.")
    else:
        print("Invalid input.")
    sys.stdout = _old_stdout
    sys.stderr = _old_stderr
def main():
    import io
    print_out = io.StringIO() 
    sys.stdout = print_out
    sys.stderr = print_out
    try:
        if is_in_app(curdir):
            do_test_app(curdir,print_out)
        elif is_in_irails(curdir):
            do_test_project(print_out)
    except Exception as e:
        raise
    if print_out:
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
            elif re.match(pattern=r"^FAIL:.*$", string=line):
                fail+=1
                matched_fail=True
            elif  matched_fail:
                tested_line.append(line) 
            lnt += 1
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    print("\n\ntest finished ,results:")
    print("====================================================")
    print("\n".join(tested_line))
    print(f"=========OK:{ok}====Fail:{fail}======================")