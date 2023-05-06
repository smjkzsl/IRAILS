import sys,os,importlib

from irails.config import is_in_app, is_in_irails
def load_module(module_name:str,module_path:str):
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None
def do_command(i18n_tool_file:str):
    if i18n_tool_file.lower()=='gettext':
        i18n_tool_file='pygettext'
    if i18n_tool_file=='pygettext':
        locales_path = os.path.abspath('locales') 
        if not os.path.exists(locales_path):
            os.makedirs(locales_path,exist_ok=True)
        if not '-o' in sys.argv:
            sys.argv.insert(1,'-o') 
            sys.argv.insert(2,f'{locales_path}{os.sep}messages.pot') 
         
            
    _tools_file = os.path.join(sys.prefix,'Tools','i18n',f"{i18n_tool_file}.py")
    module = load_module(i18n_tool_file,_tools_file)
    if module:
        try:
            module.main()
            print(f"Done!")
        except Exception as e:
            print(e)
    else:
        print(f"not found tools file:{i18n_tool_file}")
def main(): 
    #irails pygettext  -a -o messages.pot /path/to/your/dir/*.py
    cur_dir = os.path.abspath(os.curdir)
    root_path = os.path.abspath(os.path.join(cur_dir,"../.."))
    if os.path.exists(root_path) and  os.path.isdir(root_path): 
        if not is_in_irails(root_path) or not is_in_app(cur_dir):
            print(f"Please exec in irails project's app dir ,like `apps/app`")
            exit()
    if len(sys.argv)>2:
         
        cmd = sys.argv.pop(1)
        do_command(cmd)
    else:
        self_file = os.path.basename(__file__).lstrip("_").replace(".py",'')
        print(f"Usage: irails {self_file} [args...]")
        sys.exit(0)
     