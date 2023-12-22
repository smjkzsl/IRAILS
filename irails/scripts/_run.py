import argparse
import os
import sys
import irails
from irails.config import IS_IN_irails
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
    
    
    
    args.port = args.port or 8080
    args.host = args.host or "127.0.0.1"
    irails.core.run_server(args.host,args.port,args.debug)  