import argparse
import sys,os
from typing import Any
from jinja2 import Template
from irails._utils import is_valid_filename,get_controller_name,get_snaked_name,update_manifest,enable_app
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
     
    
        
    def set_root_controller_to_config(self,app_dir,app_name):
        import yaml
        try:
            file = './configs/general.yaml' 
            with open(file, "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader) 
            app_cfg = data['app'] 
            changed = False
            if not 'root' in app_cfg:
                data['app']['root']=f"{app_dir}.{app_name}" 
                changed = True
            else: 
                if not app_cfg['root']:
                    data['app']['root']=f"{app_dir}.{app_name}" 
                    changed = True
            if changed:
                with open(file, "w") as f:
                    yaml.dump(data, f)
                print(f'set {app_dir}.{app_name} to root on configs/general.yaml.')

            return changed
        except Exception as e:
            print(f'an error raised {e.args}')
            print(f"now please open configs/general.yaml to modify app.root to add {app_dir}.{app_name}!")
            return
         
    def do_copy(self,tpl_file,dest_file,micro=False,over_write=False,context={}):
        dest_file  = os.path.normpath(dest_file)
        if os.path.exists(dest_file) and not over_write:
            print(f'{dest_file} is exists,skip...')
            return True
        os.makedirs(os.path.dirname(dest_file),exist_ok=True)
        with open(tpl_file,'r') as f:
            content = f.read()
            dest_content = content
            if micro:
                 
                template = Template(content)
                dest_content = template.render(context) 
            with open(dest_file,'w') as f:
                f.write(dest_content)
        print(f"create {dest_file}")

    def add_home_view(self,app_dir,app_name:str):
        dist_file = os.path.join(app_dir,app_name,"views","home","home.html")
        tpl_file = os.path.dirname(__file__)+"/tpls/app/home.tpl"
        
        
        self.do_copy(tpl_file,dist_file)
        tpl_file = os.path.dirname(__file__)+"/tpls/app/home.css.tpl"
        dist_file = os.path.join(app_dir,app_name,"views","home","home.css")
        self.do_copy(tpl_file,dist_file,micro = True,context={'app_name':app_name.title()})
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
from irails import route,api,Request,Response,BaseController,application
@route(auth='none')
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
            
            
            dirs_items =  [
                'controllers',
                'models',
                'services',
                'views',
                'locales',
                'tests'
            ]
            context = {'app':app_name}
            for dir in dirs_items:
                _current_dir = os.path.join(store_dir,dir)
                print(f"creating {_current_dir}")
                os.makedirs(_current_dir,exist_ok=True)
            
            manifest_path = os.path.join(store_dir,'manifest.yaml')
            manifest_tpl_file = os.path.dirname(__file__)+"/tpls/app/manifest.jinja"
            self.do_copy(manifest_tpl_file,manifest_path,True,context=context)   
             
            # _init_file = os.path.normpath(os.path.join(store_dir,'__init__.py'))
            # with open(_init_file,'w') as f: #root path of app's dir
            #     f.write(f"from .controllers import *")
            
            # print(f"create {_init_file}")

            enable_app(app_name)
            if self.set_root_controller_to_config(self.args.dir,app_name):
                self.add_home_controller(self.args.dir,app_name)
                self.add_home_view(self.args.dir,app_name)
                update_manifest(manifest_path=manifest_path,section = 'packages',value= 'controllers',append=True)
            cnt += 1
        if cnt:
            print(f"now ,you can cd to {self.args.dir}/{app_name} and run `irails controller \"controller's name`\" to create controllers")
            print(f"now ,you can also run `burcelee run` to run project")
        print(f"Done! created {cnt} app[s]")
    pass

def main():
    if not IS_IN_irails:
        print(f"Please exec in irails project dir")
        exit()
    self_file = os.path.basename(__file__).lstrip("_").replace(".py",'')
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