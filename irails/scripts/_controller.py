import argparse
import sys,os,re
from typing import Any
from jinja2 import Template
from irails._utils import is_valid_filename,get_controller_name,get_snaked_name,to_camel_case,ensure_line
from  irails.config import is_in_irails,is_in_app

class Generator():
    def __init__(self,args,dir) -> None:
        self.args = args
        self.dir = dir
        pass
    def gen_common(self):
        '''#todo: check configs dir
                  check data dir

        '''
        pass
    def gen_tpl(self,tpl_file,dest,context={}, use_micro=True,dir_only=False):
        tpl_dir = os.path.dirname(__file__)+"/tpls/app"
        tpl_file = os.path.join(tpl_dir,tpl_file)
        dest = os.path.normpath(dest)
        if not os.path.exists(tpl_file):
            raise Exception(f"{tpl_file} does not exists!")
        if os.path.exists(dest):
            print(f"{dest} is exists! skip..")
            return True
        dir = os.path.dirname(dest) 
        os.makedirs(dir,exist_ok=True)
        if not dir_only:
            with open(tpl_file,'r') as f:
                content = f.read()
            dest_content = content
            if use_micro:
                template = Template(content)
                dest_content = template.render(context)
            
            
            with open(dest,'w') as f:
                f.write(dest_content)
            print(f"create {dest}")
        return True
    def str_to_upper(self,name):
        new_name = name.title().replace("_", "")
        return new_name
    def is_valid_class_name(self,name):
        if not isinstance(name, str):
            return False 
        if not re.match(r'^[a-zA-Z_]', name):
            return False 
        if not re.match(r'^\w+$', name):
            return False 
        import keyword
        if keyword.iskeyword(name):
            return False 
        return True
    

    def __call__(self) -> Any:
         
        if not self.args.name:
            print(f'controller name is empty,exit!')
            exit()
        name = self.args.name.pop(0)
        if name:
            if not is_valid_filename(name) :
                print(f'{name} is not avalided!')
                exit() 

            store_dir = self.dir
            controller_name:str = to_camel_case(name)
            controler_path_name = get_snaked_name(name)
            # store_dir = os.path.join(store_dir,controler_path_name )
            
            # controller_name = self.str_to_upper(name)
            if not self.is_valid_class_name(controller_name):
                print(f"{controller_name} is a not valided class name,exit...")
                exit() 
            acts = []
            actions = self.args.name
            if len(actions)==0:actions.append('index')

            dirs_items =  {
                'controllers':{'tpl':'controller.tpl','dest':f'controllers/{controler_path_name}_controller.py','micro':True} , 
                'models': {'tpl':'model.jinja','dest' : f'models/{controler_path_name}_model.py','micro':True},
                'services':{'tpl':'service.jinja','dest': f'services/{controler_path_name}_service.py','micro':True },
                'views': [
                    {'tpl' : 'view.tpl','dest': f'views/{controler_path_name}/index.html','micro':False},
                    {'tpl' : 'css.tpl','dest': f'views/{controler_path_name}/index.css','micro':False}
                    ] ,
                
                'tests': {'tpl':'test_controller.jinja','dest': f'tests/test_{controler_path_name}.py','micro':True}
            }
            context = {'ctrl_name':controller_name,'ctrl_path':controler_path_name,'actions':actions}
            for dir in dirs_items:
                _current_dir = store_dir#os.path.join(store_dir,dir)
                os.makedirs(_current_dir,exist_ok=True)
                items = dirs_items[dir]
                if isinstance(items,list):
                    _item = items
                else:
                    _item = [items]
                for item in _item:
                    tpl = item['tpl']
                    dest = os.path.join(_current_dir , item['dest'])
                    micro = item['micro']
                    #controller file will generate last time
                    self.gen_tpl(tpl_file=tpl,dest=dest,context=context,use_micro=micro,dir_only=dir=='controllers') 
            controller_file = os.path.join(_current_dir,'controllers',f"{controler_path_name}_controller.py")
            __init_file = os.path.join(_current_dir,'controllers','__init__.py')
            ensure_line(__init_file,f"from . import {controler_path_name}_controller")
            __init_file = os.path.join(_current_dir,'models','__init__.py')
            ensure_line(__init_file,f"from . import {controler_path_name}_model")
            __init_file = os.path.join(_current_dir,'services','__init__.py')
            ensure_line(__init_file,f"from . import {controler_path_name}_service")
            
            for action in actions:
                acts.append(f"""
    @api.get('/{action}')
    def {action}(self):
        return self.view()                
""")
                _view_file = os.path.join(_current_dir,'views',controler_path_name,f"{action}.html")
                if not os.path.exists(_view_file):
                    with open(_view_file,'w') as f:
                        f.write(f"{controller_name}.{action} view file.in:{_view_file}")
                    print(f'create {_view_file}')
                else:
                    print(f'{_view_file} was exists,skip generate')
            actions = "\n".join(acts)
            context['actions'] = actions    
            self.gen_tpl(tpl_file=dirs_items['controllers']['tpl'],dest=controller_file,context=context,use_micro=True,dir_only=False) 

        print("Done!")
    pass


def main():
     
    cur_dir = os.path.abspath(os.curdir)
    root_path = os.path.abspath(os.path.join(cur_dir,"../.."))
    if os.path.exists(root_path) and  os.path.isdir(root_path): 
        if not is_in_irails(root_path) or not is_in_app(cur_dir):
            print(f"Please exec in irails project's app dir ,like `apps/app`")
            exit()
    self_file = __file__.lstrip("_").replace(".py",'')
    parser = argparse.ArgumentParser(usage=f"{sys.argv[0]} {self_file} [-h] [--name] `controller [action ...]` ...", description='create new controller')
    parser.add_argument('--name',help="controller name to create")
    parser.add_argument('args', nargs=argparse.REMAINDER)
     
    args = parser.parse_args()
    if not any(args.__dict__.values()):
        parser.print_help()
    if not args.name:
        args.name = args.args
    else:
        args.name = [args.name]
    _gen = Generator(args,cur_dir)
    _gen()