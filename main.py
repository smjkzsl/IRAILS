
import os

import irails
from irails.config import config


if __name__=='__main__': 
    
    import uvicorn 
  
    kwargs = {}
    kwargs['reload'] = True 
    kwargs['host'] = '0.0.0.0'
    kwargs['port'] = 8080
    app_cfg =   config.get('app')
    apps_dirs = app_cfg.get("appdirs") 
    kwargs['reload_dirs'] = list(map(os.path.abspath ,apps_dirs))
    # kwargs['reload_includes'] = []
    kwargs['reload_excludes'] = ['*.pyc','*.po']  
    uvicorn.run(app="irails.core:generate_mvc_app",**kwargs) 
    
 