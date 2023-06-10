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

# def _reload_app(app_name,manifest):
#     _modules = manifest['packages']
#     for m in _modules:
#         module_name = f"irails.apps.{app_name}.{m}"
#         module = importlib.reload()


def _unload_app(application, app_name):
    if app_name in application.apps: 
        _modules = application.apps[app_name]['manifest']['packages']
        for route in application.apps[app_name]['router'].routes:
            application.routes.remove(route)
        del application.apps[app_name]['router'].routes[:] 
        del application.apps[app_name]
        for m in _modules:
            module_name = f"irails.apps.{app_name}.{m}"
            _log.info(_('Unloading module:%s') % module_name)
            
            
                
            if module_name in sys.modules:
                loaded_objects = list(sys.modules[module_name].__dict__.keys())
                # 模块对象中删除所有已加载的对象
                for obj in loaded_objects:
                    del sys.modules[module_name].__dict__[obj]

                del sys.modules[module_name]
            if module_name in loaded:
                loaded.remove(module_name)
        importlib.invalidate_caches()
        return True
    else:
        return False
# class CustomLoader(importlib.abc.Loader):
#     def create_module(self, spec):
#         return None

#     def exec_module(self, module):
#         pass

# class CustomFinder(importlib.abc.MetaPathFinder):
#     def find_spec(self, fullname, path, target=None):
#         # 当前的例子只允许 irails.apps.* 来导入
#         if fullname.startswith("irails.apps."):
#             app_name = fullname.split('.')[2]
#             for _dir in app_dirs:
#                 file_path = f'{_dir}/{app_name}/__init__.py'
#                 if os.path.exists(file_path):
#                     spec = importlib.util.spec_from_file_location(fullname, file_path, loader=CustomLoader())
#                     return spec
#         return None
    
loaded=[]
import irails
def _load_app(abs_app_dir,app_name, manifest: dict):
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
        
            
    return cnt


def collect_apps(debug=False, do_load: bool = True, application: object = None):
    global app_dirs, app_enabled
    app_cfg = config.get('app')
    if app_cfg:
        app_dirs = app_cfg.get("appdir")
        app_enabled = app_cfg.get("enabled")
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
                n = _load_app(abs_app_dir,app, manifest)
                if n:
                    if application:
                        if not app in application.apps:
                            # apps[app]['routes'] will generated by core.py->load_controllers
                            application.apps[app] = {'routes': {}}
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
