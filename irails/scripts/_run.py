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
    parser = argparse.ArgumentParser(usage=f"{sys.argv[0]} {self_file} [-h] [--host] [-p port]", description='run app') 
    parser.add_argument('-p','--port',type=int, help="http port")    
    parser.add_argument('--host',type=str, help="host name[default:127.0.0.1]")    
    parser.add_argument('-d','--debug',action='store_true',  help="enable debug mode")    
    args = parser.parse_args()
    
    kwargs = { }
    if args.host:
        kwargs['host'] = args.host
    if args.port:
        kwargs['port'] = args.port
     
     
    args.debug = config.get("debug",False)
    if args.debug: 
        kwargs['reload'] = args.debug 
        app_cfg = config.get('app')
        apps_dirs = app_cfg.get("appdirs") 
        kwargs['reload_dirs'] = list(map(os.path.abspath ,apps_dirs))
        # kwargs['reload_includes'] = []
        kwargs['reload_excludes'] = ['*.pyc','*.po'] 
    
    uvicorn.run(app="irails.core:generate_mvc_app",**kwargs)      
       