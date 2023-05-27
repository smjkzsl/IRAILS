import copy
import importlib
import sys,os
import yaml

from .config import config,ROOT_PATH 
from ._i18n import load_app_translations
from ._i18n import   _

app_dirs = []
app_enabled = []
_DEFAULT_MANIFEST=yaml.safe_load(""" 
version: '1.0'
author: 'irails' 
plugins: []
depends: []
license: 'MIT'
category: 'System'
packages: ['controllers','models','services']
""")

def load_manifest(app_dir):
    file_path = os.path.join(app_dir,'manifest.yaml')
    if os.path.exists(file_path):
        with open(file_path,'r',encoding='utf-8') as f:
            manifest = copy.deepcopy(_DEFAULT_MANIFEST)
            manifest.update(yaml.safe_load(f)) 
            return manifest
    else:
        return None
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
def _load_app(app_dir,manifest:dict): 
    if not manifest:
        return 0
    from .log import _log
    _modules = manifest['packages'] # ['controllers','services','models']
    cnt =  0
    for m in _modules:
        module_name = f"{app_dir}.{m}"
        _log.info(_('Loading module:%s')%module_name)
        try:
            importlib.import_module(module_name) 
            if m=='controllers':
                cnt += 1
        except ImportError as e:
            if m:#=='controllers':
                _log.error(_("load app %s failed")%module_name)
                _log.error(e.args)
                cnt -= 1
            else:
                pass
    return cnt
def _load_apps(debug=False,do_load:bool=True,application:object=None):
    global app_dirs,app_enabled
    app_cfg=config.get('app')
    if app_cfg:
        app_dirs = app_cfg.get("appdir")
        app_enabled = app_cfg.get("enabled")
    unloaded = 0
    loaded = 0
    apps = []
    for app_dir in app_dirs:
        abs_app_dir=os.path.abspath(os.path.join(ROOT_PATH,app_dir))
        
        app_list =  __list_directories(abs_app_dir)
        for app in app_list:
            if __check_if_enabled(app):  
                if do_load:
                    manifest = load_manifest(os.path.join(abs_app_dir,app))
                    if manifest:
                        #_dir = os.path.join(app_dir,app)
                        _abs_app_path =  abs_app_dir
                        if _abs_app_path not in sys.path:
                            sys.path.insert(0,_abs_app_path)
                        debug and print('load app:'+app)
                        n = _load_app(app,manifest)
                        if n:
                            if application:
                                if not app in application.apps:
                                    application.apps[app] = {}
                                elif application.apps[app]['manifest']:
                                    raise RuntimeError(_('The app:%s already loaded,Duplicate name in (%s) ') % (app,abs_app_dir))
                                 
                                application.apps[app]['manifest'] = manifest
                            loaded = loaded + 1
                        else:
                            unloaded = unloaded + 1
                else:
                    #just return the app list
                    apps.append( f"{app_dir}.{app}" )
            else:
                if do_load:
                    unloaded = unloaded + 1
        
    if do_load:
        return loaded,unloaded
    else:
        return apps