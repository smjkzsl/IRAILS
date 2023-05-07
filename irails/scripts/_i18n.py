import sys,os,importlib

from irails.config import is_in_app, is_in_irails,YamlConfig
cur_dir = os.path.abspath(os.curdir)
root_path = os.path.abspath(os.path.join(cur_dir,"../.."))
config = YamlConfig(os.path.join(root_path,"configs"))
locales_path = os.path.abspath('locales') 

def load_module(module_name:str,module_path:str):
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None
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
po_header = """
# SOME DESCRIPTIVE TITLE.
# Copyright (C) {YEAR} ORGANIZATION
# FIRST AUTHOR <EMAIL@ADDRESS>, {YEAR}.
#
msgid ""
msgstr ""

"Project-Id-Version: \\n"
"POT-Creation-Date: {d1}\\n"
"PO-Revision-Date: {d2}\\n"
"Last-Translator: \\n"
"Language-Team: \\n"
"Language: {lang}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=1; plural=0;\\n"
"Generated-By: pygettext.py 1.5\\n"
"X-Generator: Poedit 3.2.2\\n"
"""
def split_pot(content:str):
    lines = content.split("\n")
    l = -1
    for line in lines:
        l+=1
        if line.startswith('"Generated-By'):
            break
    if l>0:
        return "\n".join(lines[l+1:])
    
def convert_pot2po():
    cfg = config.get('i18n')
    if not cfg:
        lan = ['en','zh']
    else:
        lan = cfg.get('lang',['en','zh'])
    print('current configure languages:'+str(lan))
    # now normalize and expand the languages
    nelangs = []
    for lang in lan:
        for nelang in _expand_lang(lang):
            if nelang not in nelangs:
                nelangs.append(nelang)
    _pot_file = os.path.join(locales_path,"messages.pot")
    if os.path.exists(_pot_file):
        print(f"generated {_pot_file}")
        with open(_pot_file,'r') as f:
            _pot_content = f.read()
        _pot_content = split_pot(_pot_content)
        
    else:
        print("messages.pot des'nt exists!")
        return
    import datetime
    d1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M%z')
    year = datetime.datetime.now().strftime('%Y')
     
     
    d2 = d1
    for lang in nelangs:
        if len(lang)!=5:
            continue
        header = po_header.replace("{d1}",d1).replace("{d2}",d2).replace("{lang}",lang).replace("{YEAR}",year)
        path = os.path.join(locales_path,f"{lang}.po")
        with open(path,'w') as f:
            f.write(header+"\n"+_pot_content)
            print(f"generated {path}")

def do_command(i18n_tool_file:str):
    if i18n_tool_file.lower()=='gettext':
        i18n_tool_file='pygettext'
    if i18n_tool_file=='pygettext':
        
        if not os.path.exists(locales_path):
            os.makedirs(locales_path,exist_ok=True)
        if len(sys.argv)<2:
            for d in ['controllers','services','models']:
                sys.argv.append(d)

        if not '-o' in sys.argv:
            sys.argv.insert(1,'-o') 
            sys.argv.insert(2,f'{locales_path}{os.sep}messages.pot') 
         
            
    _tools_file = os.path.join(sys.prefix,'Tools','i18n',f"{i18n_tool_file}.py")
    module = load_module(i18n_tool_file,_tools_file)
    if module:
        try:
            module.main()
            convert_pot2po()
            print(f"Done!")
        except Exception as e:
            print(e)
    else:
        print(f"not found tools file:{i18n_tool_file}")
def main(): 
    #irails pygettext  -a -o messages.pot /path/to/your/dir/*.py
    
    if os.path.exists(root_path) and  os.path.isdir(root_path): 
        if not is_in_irails(root_path) or not is_in_app(cur_dir):
            print(f"Please exec in irails project's app dir ,like `apps/app`")
            exit()
    if len(sys.argv)>=2:
         
        cmd = sys.argv.pop(1)
        do_command(cmd)
    else:
        self_file = os.path.basename(__file__).lstrip("_").replace(".py",'')
        print(f"Usage: irails {self_file} [args...]")
        sys.exit(0)
     