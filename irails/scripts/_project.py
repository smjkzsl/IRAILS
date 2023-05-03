import argparse
import sys,os
from typing import Any
from jinja2 import Template
import shutil
from irails._utils import is_valid_filename

class Generator():
    def __init__(self,args) -> None:
        self.args=args
        pass
    def gen_common(self):
        '''#todo: check configs dir
                  check data dir

        '''
        pass
    def gen_tpl(self,tpl_file,dest,context={}, use_micro=True):
        tpl_dir = os.path.dirname(__file__)+"/tpls/project"
         
       
         
    def __call__(self) -> Any:
        curdir = os.getcwd()
        if not self.args.dir:
            self.args.dir = input(f"please input dir to store project:")
            if not self.args.dir:
                print("project dir can't be empty")
                exit()
            assert is_valid_filename(self.args.dir)
        project_dir = os.path.abspath(self.args.dir)
        if os.path.exists(project_dir):
            if os.path.isdir(project_dir):
                if bool(os.listdir(project_dir)):
                    print(f"directory {self.args.dir} is exists and is not empty!")
                    exit()
        # os.makedirs(project_dir,exist_ok=True)
        tpl_dir = os.path.dirname(__file__)+"/tpls/project"
        try:
            if shutil.copytree(tpl_dir , project_dir): 
                os.makedirs(os.path.join(project_dir,'uploads'),exist_ok=True)
                os.makedirs(os.path.join(project_dir,'data'),exist_ok=True)
                print("Done!")
        except Exception as e:
            print("Error!")
            print(e.args)
            exit()

def main():
    self_file = os.path.basename(__file__).lstrip("_").replace(".py",'')
    parser = argparse.ArgumentParser(usage=f"{sys.argv[0]} {self_file} [-h] [-d DIR]", description='new app') 
    parser.add_argument('-d','--dir',help="dir to store project files")
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not any(args.__dict__.values()):
        parser.print_help()
        exit()
    if not args.dir:
        if args.args and len(args.args)==1:
            args.dir = args.args[0]
    if not args.dir:
        parser.print_help()
        exit()
    _gen = Generator(args)
    _gen()