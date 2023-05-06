import importlib
import sys,os
from .config import config,ROOT_PATH,_log
from ._i18n import load_app_translations
from gettext import gettext as _
app_cfg=config.get('app')
app_dirs = app_cfg.get("appdir")
app_enabled = app_cfg.get("enabled")

def __list_directories(dir):
    """
    return all subdirectory under :dir
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

def load_module(module_name:str,module_path:str):
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None
def _load_app(app_dir):
    try:
        _path = os.path.join(ROOT_PATH,app_dir.split(".")[0])
        if _path not in sys.path:
            sys.path.insert(-1,_path)
        _log.info(_('Loading app:%s')%app_dir)
        return importlib.import_module(app_dir)
          
    except ImportError as e:
        _log.error(_("load app %s failed")%app_dir)
        _log.error(e.args)
        raise e
    
def _load_apps(debug=False):
    if ROOT_PATH not in sys.path:
        sys.path.insert(-1,ROOT_PATH)
    unloaded = 0
    loaded = 0
    for app_dir in app_dirs:
        app_list =  __list_directories(app_dir)
        for app in app_list:
            if __check_if_enabled(app):  
                _dir = os.path.join(app_dir,app)
                module = _load_app(f'{app_dir}.{app}')
                if module:
                    t =  load_app_translations(_dir)
                    setattr(module,"_translation",t)
                    loaded = loaded + 1
                else:
                    unloaded = unloaded + 1
            else:
                unloaded = unloaded + 1
        
    
    return loaded,unloaded