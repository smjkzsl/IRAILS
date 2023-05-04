import argparse
import os,importlib,sys
from irails import  run as runserver 
from irails.config import IS_IN_irails

def main():

    if not IS_IN_irails:
        print(f"`run` command must run in the directory of irails project")
        exit()
    self_file = os.path.basename(__file__).lstrip("_").replace(".py",'')
    parser = argparse.ArgumentParser(usage=f"{sys.argv[0]} {self_file} [-h] [-p port]", description='run app') 
    parser.add_argument('-p','--port',type=int, help="http port")    
    parser.add_argument('-d','--debug',action='store_true',  help="enable debug mode")    
    args = parser.parse_args()
    module_path = 'main.py'
    kwargs = {'debug':False}
    if args.debug:
        kwargs['debug'] = args.debug
    if args.port:
        kwargs['port'] = args.port
    def do_run(app):
        runserver(app,**kwargs)
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_path, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        do_run(module.app) 
    else:
        from irails import generate_mvc_app
        app = generate_mvc_app()
        do_run(app)
         
        # print(f'please exec on irals project\'s dir,missing main.py')
        # exit()