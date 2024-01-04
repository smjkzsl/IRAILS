import copy
import importlib
import sys
import os
import yaml

from .config import config, ROOT_PATH
from ._i18n import load_app_translations
from ._i18n import _
from .log import get_logger
import irails
_log=get_logger(__name__)

app_dirs = []
app_enabled = []
_DEFAULT_MANIFEST = yaml.safe_load(""" 
version: '1.0'
author: 'irails' 
plugins: []
depends: []
license: 'MIT'
category: 'System'
packages: ['controllers','models','services']
""")

 



def load_manifest(app_dir):
    file_path = os.path.join(app_dir, 'manifest.yaml')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
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

        path = os.path.join(dir, name)
        if os.path.isdir(path) and name != '__pycache__':
            dirs_list.append(name)
    return dirs_list


def __check_if_enabled(app_name):
    return (app_enabled == "*" or
            not app_enabled or
            (isinstance(app_enabled, list) and app_name in app_enabled))


def load_module(module_name: str, module_path: str):
    if module_name in sys.modules:
        return sys.modules[module_name]
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        return module
     
    return None

# issue.
# def _reload_app(app_name,manifest):
#     _modules = manifest['packages']
#     for m in _modules:
#         module_name = f"irails.apps.{app_name}.{m}"
#         module = importlib.reload(sys.modules[module_name])


def _unload_app(application, app_name):
    '''
    This operation will only temporarily disable  `app_name` , 
    it will not be actually removed from Python due to the mechanism of Python. 
    After disabling it, you must restart irails to ensure database synchronization. 
    After restarting, it can be reinstalled.
    '''
    if app_name in application.apps: 
        _modules = application.apps[app_name]['manifest']['packages']
        if 'routes' in application.apps[app_name]:
            for item in application.apps[app_name]['routes']:
                application.apps[app_name]['routes'][item]['label'] = 'new'
            #delete routes on application
            for route in application.apps[app_name]['router'].routes:
                
                application.routes.remove(route)
            #delete static mount
            for route in application.routes:
                for _dir in application.apps[app_name]['view_dirs']:
                    if route.name == os.path.normpath(_dir):
                        application.routes.remove(route)
            #delete router map on app_name in application
            del application.apps[app_name]['router'].routes[:] 
        #mark application app_name is_installed  is False
        application.apps[app_name]['is_installed'] = False
        #try unload memory from python,it's not realy
        for m in _modules:
            module_name = f"irails.apps.{app_name}.{m}"
            _log.info(_('Unloading module:%s') % module_name)
            
            
                
            if module_name in sys.modules:
                loaded_objects = list(sys.modules[module_name].__dict__.keys())
                # not realy
                for obj in loaded_objects:
                    del sys.modules[module_name].__dict__[obj]

                del sys.modules[module_name]
            if module_name in loaded:
                loaded.remove(module_name)
        importlib.invalidate_caches()
        return True
    else:
        return False
 
    
loaded=[]

def _load_app(abs_app_dir,app_name, manifest: dict,application=None):
    if not manifest:
        return 0
    
    #add python location to find package like 'irails.apps.app_name...'
    if not abs_app_dir in irails.apps.__path__:
        irails.apps.__path__.append(abs_app_dir)

    _modules = manifest['packages']  # eg. ['controllers','services','models']
   
   

    cnt = 0
    for m in _modules:
        module_name = f"irails.apps.{app_name}.{m}"
        if module_name in loaded or module_name in sys.modules:
            cnt += 1
            continue
        _log.info(_('Loading module:%s') % module_name)
        try:  
            # module_path = os.path.join(abs_app_dir,app_name,m,"__init__.py")
            module = importlib.import_module(module_name) 
            if module:
                cnt += 1
                if not module_name in loaded:
                    loaded.append(module_name)
        except ImportError as e: 
            _log.error(_("load app %s failed") % m + " in module:" + module_name)
            _log.error(e.args)
            cnt -= 1
             
    load_app_translations(os.path.join(abs_app_dir,app_name))
    if cnt == len(_modules):
        application.apps[app_name]['is_installed'] = True   
    else:
        print(app_name+" 模块并未完全加载[" + ",".join(_modules) +"]")        
            
    return cnt  


def load_from_dir(abs_app_dir,app:str,do_load=True, application:'irails.core.MvcApp'=None):
    _app_path = os.path.join(abs_app_dir,app)
    manifest = load_manifest(_app_path)
     
    app_info = {}
    module_count = 0
    if manifest:
        app_info = {'app_dir':_app_path, 'package': app, 'manifest': manifest} 

    if manifest and do_load: 
        module_count = _load_app(abs_app_dir,app, manifest,application) 
    
        if application:
            if not app in application.apps:
                # apps[app]['routes'] will generated by core.py->load_controllers
                application.apps[app] = {'routes': {},'route_map':{}}
            if not 'manifest' in application.apps[app]:
                application.apps[app]['manifest'] = manifest
            else:
                raise RuntimeError(
                    _('The app:%s already loaded,Duplicate name in (%s) ') % (app, abs_app_dir))
                
       
            
    return app_info,module_count

def collect_apps(debug=False, do_load: bool = True, application:'irails.core.MvcApp' = None):
    global app_dirs, app_enabled
    app_cfg = config.get('app')
    if app_cfg:
        app_dirs = app_cfg.get("appdirs")
        app_enabled = app_cfg.get("enabled")
    if not app_cfg or not app_dirs:
        application.mode = 0 #single appmode
        raise RuntimeError(_("config error,app configs is empty.please check `appdirs` section"))
    
    load_failed = 0
    loaded = 0
    apps = []
    for app_dir in app_dirs:
        abs_app_dir = os.path.abspath( app_dir)

        app_list = __list_directories(abs_app_dir)
        for app in app_list:
            _app_path=os.path.join(abs_app_dir, app)
            if __check_if_enabled(app):
                ret ,n=  load_from_dir(abs_app_dir,app=app,do_load=do_load,application=application)
                if ret  :
                    apps.append(ret)
                    if n:
                        loaded = loaded + 1
                else:

                    load_failed = load_failed + 1
    if do_load:
        return loaded, load_failed
    else:
        return apps
