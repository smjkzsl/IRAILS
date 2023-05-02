import argparse
import sys,os
from typing import Any
from jinja2 import Template
from irails._utils import is_valid_filename,get_controller_name,get_snaked_name
from  irails.config import IS_IN_irails

class Generator():
    def __init__(self,args) -> None:
        self.args=args
        pass
    def gen_common(self):
        '''#todo: check configs dir
                  check data dir

        '''
        pass
    def gen_tpl(self,tpl_file,dest,context={}, use_micro=True,dir_only=True):
        tpl_dir = os.path.dirname(__file__)+"/tpls/app"
        tpl_file = os.path.join(tpl_dir,tpl_file)
        dest = os.path.normpath(dest)
        if not os.path.exists(tpl_file):
            raise Exception(f"{tpl_file} does not exists!")
        dir = os.path.normpath(os.path.dirname(dest))
        if not os.path.exists(dir):
            os.makedirs(dir,exist_ok=True)
            print(f"create {dir}")
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
    def add_enabled_to_app(self,app_name):
        import yaml
        try:
            file = './configs/general.yaml'
 
            with open(file, "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
 
            enabled = data['app']['enabled']
            if not enabled:
                enabled = [app_name]
            else:
                if isinstance(enabled,list):
                    enabled.append(app_name) 
            new_enabled = list(set(enabled))

            data['app']['enabled'] = new_enabled
            with open(file, "w") as f:
                yaml.dump(data, f)
        except Exception as e:
            print(f'an error raised {e.args}')
            print(f"now please open configs/general.yaml to modify app.enabled to add {app_name}!")
            return
        print(f"configs/general.yaml app.enabled has been added {app_name}!")
    
    def do_copy(self,tpl_file,dest_file,over_write=False):
        dest_file  = os.path.normpath(dest_file)
        if os.path.exists(dest_file) and not over_write:
            print(f'{dest_file} is exists,skip...')
            return True
        os.makedirs(os.path.dirname(dest_file),exist_ok=True)
        with open(tpl_file,'r') as f:
            content = f.read()
            dest_content = content
            # template = Template(content)
            # dest_content = template.render(context) 
            with open(dest_file,'w') as f:
                f.write(dest_content)
        print(f"create {dest_file}")

    def add_home_view(self,app_dir,app_name):
        dist_file = os.path.join(app_dir,app_name,"views","home","home.html")
        tpl_file = os.path.dirname(__file__)+"/tpls/app/home.tpl"
        
        context = {'app_name':app_name}
        self.do_copy(tpl_file,dist_file)
        tpl_file = os.path.dirname(__file__)+"/tpls/app/home.css.tpl"
        dist_file = os.path.join(app_dir,app_name,"views","home","home.css")
        self.do_copy(tpl_file,dist_file)
        return True
    
    def add_home_controller(self,app_dir,app_name):
        dest_file = os.path.join(app_dir,app_name,"controllers","home_controller.py")
        dest_file = os.path.normpath(dest_file)
        if os.path.exists(dest_file):
            print(f'{dest_file} is exists,skip...')
            return True
        with open(dest_file,'w') as f:
            f.write("""
# -*- coding: utf-8 -*- 
from irails import api_router,api,Request,Response,BaseController,application,WebSocket,WebSocketDisconnect,UploadFile,File
@api_router(auth='none')
class HomeController(BaseController): 
    @api.get("/")
    def home(self): 
        '''
        :title Home
        '''
        routers_map = application.routers_map
        return self.view()
            """)
        print(f"create {dest_file}")
        _init_file = os.path.join(app_dir,app_name,"controllers","__init__.py")
        if os.path.exists(_init_file):
            print(f"{_init_file} exists,skip...")
            return True
        with open(_init_file,'w') as f:
            f.write(f"from . import home_controller")
        print(f"create {_init_file}")
        return True
    
    def __call__(self) -> Any:
        if not self.args.dir:
            self.args.dir = input("please input dir to store app[default=apps]:")
            if not self.args.dir:
                self.args.dir = 'apps'
        assert is_valid_filename(self.args.dir)
        if not self.args.name:
            print("except app name") 
            exit()
        cnt = 0
        app_name = ""
        for name in self.args.name:
            if not is_valid_filename(name) :
                print(f'{name} is not avalided!')
                exit() 
            app_name = get_snaked_name(name)
            store_dir = self.args.dir
            store_dir = os.path.join(store_dir,app_name)
            if os.path.exists(store_dir):
                if os.path.isdir(store_dir):
                    if bool(os.listdir(store_dir)):
                        print(f"directory {store_dir} is exists and is not empty!")
                        exit()
            
            
            dirs_items =  {
                'controllers':{'tpl':'controller.tpl','dest':f'{app_name}_controller.py','micro':True} , 
                'models': {'tpl':'model.tpl','dest' : f'{app_name}_model.py','micro':True},
                'services':{'tpl':'service.tpl','dest': f'{app_name}_service.py','micro':True },
                'views': [
                    {'tpl' : 'view.tpl','dest': f'{app_name}/home.html','micro':False},
                    {'tpl' : 'home.css.tpl','dest': f'{app_name}/home.css','micro':False}
                    ] ,
                
                'tests': {'tpl':'test.tpl','dest': f'test_{app_name}.py','micro':True}
            }
            context = {'app':app_name}
            for dir in dirs_items:
                _current_dir = os.path.join(store_dir,dir)
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
                    self.gen_tpl(tpl_file=tpl,dest=dest,context=context,use_micro=micro) 
            _init_file = os.path.normpath(os.path.join(store_dir,'__init__.py'))
            with open(_init_file,'w') as f: #root path of app's dir
                f.write(f"from .controllers import *")
            
            print(f"create {_init_file}")

            self.add_enabled_to_app(app_name)
            self.add_home_controller(self.args.dir,app_name)
            self.add_home_view(self.args.dir,app_name)
            cnt += 1
        if cnt:
            print(f"now ,you can cd to {self.args.dir}/{app_name} and run `irails controller controller's name` to create controllers")
            print(f"now ,you can also run `burcelee run` to run project")
        print(f"Done! created {cnt} app[s]")
    pass

def main():
    if not IS_IN_irails:
        print(f"Please exec in irails project dir")
        exit()
    self_file = __file__.lstrip("_").replace(".py",'')
    parser = argparse.ArgumentParser(usage=f"{sys.argv[0]} {self_file} [-h]  [-d DIR] [--name NAME] `app` ...", description='new app')
    parser.add_argument('--name',help="name to create app")
    parser.add_argument('-d','--dir',help="dir to store app files")
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()
    if not any(args.__dict__.values()):
        parser.print_help()

    if not args.name:
        args.name = args.args
    else:
        args.name = [args.name]
    _gen = Generator(args)
    _gen()