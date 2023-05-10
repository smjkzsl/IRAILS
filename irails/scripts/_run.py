import argparse
import os, sys
import uvicorn
from irails.config import IS_IN_irails
 
from irails.core import application
from irails.config import config

def main():
     
    if not IS_IN_irails:
        print(f"`run` command must run in the directory of irails project")
        exit()
    self_file = os.path.basename(__file__).lstrip("_").replace(".py",'')
    parser = argparse.ArgumentParser(usage=f"{sys.argv[0]} {self_file} [-h] [-p port]", description='run app') 
    parser.add_argument('-p','--port',type=int, help="http port")    
    parser.add_argument('-d','--debug',action='store_true',  help="enable debug mode")    
    args = parser.parse_args()
    
    kwargs = { }

    if args.port:
        kwargs['port'] = args.port
    kwargs['reload'] = True
    if args.debug: 
        kwargs['reload'] = args.debug 
        app_cfg = config.get('app')
        apps_dirs = app_cfg.get("appdir") 
        kwargs['reload_dirs'] = apps_dirs
        kwargs['reload_includes'] = ['*.po']
    # module_path = 'main.py'
    # spec = importlib.util.spec_from_file_location(module_path, module_path)
    # module = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(module)
    
    from uvicorn.main import logger
    from irails.config import set_logger
    set_logger(logger=logger)

    uvicorn.run(app="irails.core:generate_mvc_app",**kwargs)      
       