 
import gettext
import importlib  

import os,sys
import gettext

from typing import Callable,Optional
from .config import config
 
 
observers_dir = {}
_default_localedir = os.path.join(sys.base_prefix, 'share', 'locale')
 
translator:gettext.GNUTranslations = None
trans_dic = {}          
langs = ['en','zh'] 
cfg = config.get('i18n')
 
if   cfg: 
    langs = cfg.get('lang',langs)
for l in langs:
    trans_dic[l] = None
 
def get_all():
    """
    `return` 
    {
        {
            "zh": { 
                "key": "val"
            }
        },
        {
            "en": {
                "key": "val"
            }
        },
        {
            "ja": {}
        }
    }
    """
 
    ret = {}
    for l,t in trans_dic.items():
        if t:
            #skip first the irails framework traslations
            _t = t if t and not t._fallback else t._fallback 
        if _t:
            ret.update({l:_get_catalogs(_t,l)})

    return ret

def _get_catalogs(t:gettext.GNUTranslations,lang:str):
    _catalogs={}
    info = t.info() 
    if info['language'].startswith(lang):
        _catalogs.update(t._catalog)
    if t._fallback:
        _catalogs.update(_get_catalogs(t._fallback,lang))
    
    return _catalogs

 


def load_module(module_name:str,module_path:str):
    # if module_name in sys.modules:
    #     return sys.modules[module_name]
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # sys.modules[module_name] = module
        return module
    return None
def check_compile_po(localedir,lang): 
    po_file = os.path.join(localedir, f'{lang}.po') 
    mo_file = os.path.join(localedir, f'{lang}.mo')
    def do_mfgmft():
         
        _tools_file = os.path.join(sys.prefix,'Tools','i18n',f"msgfmt.py")
        module = load_module('mfgmft',_tools_file)
        if module:
            module.make(po_file,mo_file)
        else:
            print(f"not found tools file : {_tools_file}")
    # 判断po文件是否存在
    if os.path.exists(po_file): 
        if os.path.exists(mo_file):
            mod_time =  (os.stat(mo_file).st_mtime)
        else:
            mod_time = 0
        pod_time =  (os.stat(po_file).st_mtime) 
        if pod_time>mod_time: 
            try:
                if os.path.exists(mo_file):
                    os.remove(mo_file)
            except Exception as e:
                pass
            key = (gettext.GNUTranslations,mo_file)
            if key in gettext._translations:
                del gettext._translations[key]
            do_mfgmft()
 

is_debug = config.get("debug")
if is_debug: #watch locale dir file change
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    import time
    class PoFileHandler(FileSystemEventHandler):
        '''
        check if po file modified then delete loaded module's cached i18n 
        '''
        def __init__(self,hash,handler:Callable,ob:Observer=None ) -> None:
            self.hash = hash
            self.handler = handler
            self.observer:Observer=ob
            super().__init__()
        def on_modified(self, event):
            if not event.is_directory and callable(self.handler):
                 
                if self.recently_modified(event.src_path) :
                    print(f"{event.src_path} has been modified") 
                    self.handler(self.hash,self.observer)

        def recently_modified(self, file_name:str, seconds=2):  
            if not file_name.endswith(".po"):
                return False
            modified_time = os.path.getmtime(file_name)
            current_time = time.time()
            return current_time - modified_time<seconds

    def handler(hash,observer:Observer):
         
        for l,t in trans_dic.items():
            trans_dic[l] = None
        #reload
        for mod_dir in observers_dir:  
            observers_dir[mod_dir].stop()
            observers_dir[mod_dir].unschedule_all()
            load_app_translations(mod_dir)     


def load_app_translations(module_dir,add_debug_watch:bool=True): 
    
    locales_dir = os.path.join(module_dir, "locales") 
    if not os.path.exists(locales_dir):
        return

    
    for l in langs:
         
        t = None 
        try:
            t = gettext.translation("messages", locales_dir, languages=[l])  
        except Exception as e: 
            pass
        if t: 
            
            if not trans_dic[l] is None:
                trans_dic[l].add_fallback(t)
            else:
                trans_dic[l] = t 

    if is_debug and add_debug_watch: 
        observer = Observer()
        event_handler = PoFileHandler(module_dir,handler=handler,ob=observer )
        observer.schedule(event_handler=event_handler,path=locales_dir) 
        observer.start()
        observers_dir[module_dir]=observer    
    
 
 
 
def __init_load_i18n():
    # modify gettext find method
    # load irails framework translations

    _dir = os.path.dirname(__file__)
    # Locate a .mo file using the gettext strategy
    def __new_find(domain, localedir=None, languages=None, all=False):
        # Get some reasonable defaults for arguments that were not supplied
        # all = False
        if localedir is None:
            localedir = _default_localedir
        if languages is None:
            languages = []
            for envar in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
                val = os.environ.get(envar)
                if val:
                    languages = val.split(':')
                    break
            if 'C' not in languages:
                languages.append('C')
        # now normalize and expand the languages
        nelangs = []
        for lang in languages:
            for nelang in gettext._expand_lang(lang):
                if nelang not in nelangs:
                    nelangs.append(nelang)
        # select a language
        if all:
            result = []
        else:
            result = None
        for lang in nelangs:
            
            if lang == 'C':
                break
            # mofile = os.path.join(localedir, lang, 'LC_MESSAGES', '%s.mo' % domain)
            check_compile_po(localedir,lang)
            mofile = os.path.join(localedir, f'{lang}.mo')
            if os.path.exists(mofile):
                
                if all:
                    result.append(mofile)
                else:
                    return mofile
            
        return result

    gettext.find=__new_find #rewrite find method
    load_app_translations(_dir)


__init_load_i18n()


def _ (msg,lang=False):
    if not lang:  lang = langs[0]
    if lang not in trans_dic:
        return msg

    return trans_dic[lang].gettext(msg)
 