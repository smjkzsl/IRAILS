import datetime
import gettext
import importlib  

import os,sys
import gettext
from typing import Union
_default_localedir = os.path.join(sys.base_prefix, 'share', 'locale')
_old_find = gettext.find
def _expand_lang(loc):
    import locale
    loc = locale.normalize(loc)
    COMPONENT_CODESET   = 1 << 0
    COMPONENT_TERRITORY = 1 << 1
    COMPONENT_MODIFIER  = 1 << 2
    # split up the locale into its base components
    mask = 0
    pos = loc.find('@')
    if pos >= 0:
        modifier = loc[pos:]
        loc = loc[:pos]
        mask |= COMPONENT_MODIFIER
    else:
        modifier = ''
    pos = loc.find('.')
    if pos >= 0:
        codeset = loc[pos:]
        loc = loc[:pos]
        mask |= COMPONENT_CODESET
    else:
        codeset = ''
    pos = loc.find('_')
    if pos >= 0:
        territory = loc[pos:]
        loc = loc[:pos]
        mask |= COMPONENT_TERRITORY
    else:
        territory = ''
    language = loc
    ret = []
    for i in range(mask+1):
        if not (i & ~mask):  # if all components for this combo exist ...
            val = language
            if i & COMPONENT_TERRITORY: val += territory
            if i & COMPONENT_CODESET:   val += codeset
            if i & COMPONENT_MODIFIER:  val += modifier
            ret.append(val)
    ret.reverse()
    return ret
# Locate a .mo file using the gettext strategy
def __new_find(domain, localedir=None, languages=None, all=False):
    # Get some reasonable defaults for arguments that were not supplied
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

def check_compile_po(localedir,lang): 
    po_file = os.path.join(localedir, f'{lang}.po') 
    mo_file = os.path.join(localedir, f'{lang}.mo')
    def do_command():
        from ._loader import load_module
        _tools_file = os.path.join(sys.prefix,'Tools','i18n',f"msgfmt.py")
        module = load_module('mfgmft',_tools_file)
        if module:
            module.make(po_file,mo_file)
        else:
            print(f"not found tools file : mfgmft")
    # 判断po文件是否存在
    if os.path.exists(po_file): 
        if os.path.exists(mo_file):
            mod_time =  (os.stat(mo_file).st_mtime)
        else:
            mod_time = 0
        pod_time =  (os.stat(po_file).st_mtime) 
        if pod_time>mod_time: 
            do_command()
# 获取当前模块的 ModuleSpec 实例
module_spec = importlib.util.find_spec(__name__)

__all_trans = {}           
def load_app_translations(module_dir,is_core:bool=False,lan=None) -> gettext.GNUTranslations: 
    global __all_trans
    if module_dir in __all_trans:
        return __all_trans[module_dir]
    if not is_core:
        from .config import config
        cfg = config.get('i18n')
        if not cfg:
            lan = ['en','zh']
        else:
            lan = cfg.get('lang')
        if not isinstance(lan,list):
            lan=[lan]
    else:
        if not lan:
            lan = ['en','zh']
    # 加载翻译文件
    locales_dir = os.path.join(module_dir, "locales")
    ret = None
    try:
        ret = gettext.translation("messages", locales_dir, languages=lan) 
         
    except FileNotFoundError as e:
        pass
    
    ret = gettext
    __all_trans[module_dir] = ret
    return ret
 
 