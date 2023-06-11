import copy
import importlib
import sys
import os
import yaml

from .config import config, ROOT_PATH
from ._i18n import load_app_translations
from ._i18n import _
from .log import _log

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
import irails
def _load_app(abs_app_dir,app_name, manifest: dict,application=None):
    if not manifest:
        return 0
    if not abs_app_dir in irails.apps.__path__:
        irails.apps.__path__.append(abs_app_dir)

    _modules = manifest['packages']  # ['controllers','services','models']
    cnt = 0
    for m in _modules:
        module_name = f"irails.apps.{app_name}.{m}"
        _log.info(_('Loading module:%s') % module_name)
        try: 
            if module_name in loaded or module_name in sys.modules:
                pass
            else:
                module_path = os.path.join(abs_app_dir,app_name,m,"__init__.py")
                module = load_module(module_name=module_name,module_path=module_path)
                # just unload,try to reload 
                if m=='controllers' and application and app_name in application.apps and application.apps[app_name]['is_installed']==False:
                    # sub_modules = list(module.__dict__.keys())
                    # for sub_ in sub_modules:
                    #     if type(getattr(module,sub_)).__name__=='module': 
                    #         importlib.reload(getattr(module,sub_))
                        
                    module = importlib.reload(module)

                
                # module =   importlib.import_module(module_name) 
            if module:
                cnt += 1
                if not module_name in loaded:
                    loaded.append(module_name)
        except ImportError as e:
            if m:  # =='controllers':
                _log.error(_("load app %s failed") % module_name)
                _log.error(e.args)
                cnt -= 1
            else:
                pass
    if cnt == len(_modules):
        application.apps[app_name]['is_installed'] = True       
            
    return cnt


def collect_apps(debug=False, do_load: bool = True, application: object = None):
    global app_dirs, app_enabled
    app_cfg = config.get('app')
    if app_cfg:
        app_dirs = app_cfg.get("appdir")
        app_enabled = app_cfg.get("enabled")
    if not app_cfg or not app_dir:
        raise RuntimeError(_("Config error,app configs is empty."))
    
    load_failed = 0
    loaded = 0
    apps = []
    for app_dir in app_dirs:
        abs_app_dir = os.path.abspath(os.path.join(ROOT_PATH, app_dir))

        app_list = __list_directories(abs_app_dir)
        for app in app_list:
            manifest = load_manifest(os.path.join(abs_app_dir, app))
            if manifest:
                apps.append({'app_dir':os.path.join(abs_app_dir, app), 'package': app, 'manifest': manifest})

            if __check_if_enabled(app) and manifest and do_load:
                # _dir = os.path.join(app_dir,app)
                # apps_load_path = abs_app_dir
         
                debug and print('load app:'+app)
                n = _load_app(abs_app_dir,app, manifest,application)
                if n:
                    if application:
                        if not app in application.apps:
                            # apps[app]['routes'] will generated by core.py->load_controllers
                            application.apps[app] = {'routes': {},'route_map':{}}
                        if not 'manifest' in application.apps[app]:
                            application.apps[app]['manifest'] = manifest
                        else:
                            raise RuntimeError(
                                _('The app:%s already loaded,Duplicate name in (%s) ') % (app, abs_app_dir))
                        loaded = loaded + 1
                else:
                    load_failed = load_failed + 1

    if do_load:
        return loaded, load_failed
    else:
        return apps
