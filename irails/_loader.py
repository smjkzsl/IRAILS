import sys,os
from .config import config,ROOT_PATH
app_cfg=config.get('app')
app_dirs = app_cfg.get("appdir")
app_enabled = app_cfg.get("enabled")

def __list_directories(dir):
    """
    遍历目录，返回所有子目录的路径
    """
    dirs_list = [] 
    for name in os.listdir(dir):
       
        path = os.path.join(dir,name)
        if os.path.isdir(path) and name!='__pycache__': 
            dirs_list.append(name)
    return dirs_list

def __check_if_enabled(app_name):
    return (app_enabled == "*" or 
            not app_enabled or 
            (isinstance(app_enabled,list) and app_name in app_enabled))

sys.path.insert(-1,ROOT_PATH)
def _load_apps():
    for app_dir in app_dirs:
        app_list =  __list_directories(app_dir)
        for app in app_list:
            if __check_if_enabled(app): 
                __import__(f'{app_dir}.{app}')
 
        
        
 