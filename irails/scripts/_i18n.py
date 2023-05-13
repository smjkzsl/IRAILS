import sys,os,importlib,datetime
from irails import __version__
from irails.config import is_in_app, is_in_irails,YamlConfig
cur_dir = os.path.abspath(os.curdir)
root_path = os.path.abspath(os.path.join(cur_dir,"../.."))
config = YamlConfig(os.path.join(root_path,"configs"))
locales_path = os.path.abspath('locales') 
dev_mode = True
import glob

def get_html_vue_files(_root_path):
    html_vue_files = []
    for root, dirs, files in os.walk(_root_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith('.html') or file_path.endswith('.vue'):
                html_vue_files.append(file_path)
    return html_vue_files

def extract_html_messages(html_file_path):
    # 创建一个 PO 文件
    import polib,re
    po = polib.POFile()

    # 读取 HTML 文件
    with open(html_file_path, 'r', encoding='utf8') as f:
        html_data = f.read()

    # 查找 HTML 中包含的 gettext 翻译字符串
    gettext_re = re.compile(r"_\(['\"](.*?)['\"]\)")
    matches = gettext_re.findall(html_data)

    # 将匹配到的翻译字符串添加到 PO 文件中
    for message in matches:
        # 添加到 PO 文件中
        entry = polib.POEntry(msgid=message)
        po.append(entry)
    if len(matches)<=0:
        return ""
    # 将数据写入 PO 文件
    return str(po)
    # po.save(po_file_path)
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
"X-Generator: irails i18n {version}\\n"
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
        static_files = get_html_vue_files(os.path.join(cur_dir,'views'))
        with open(_pot_file,'a') as f:
            for file in static_files:
                print(f"checking {file}")
                po_entries = extract_html_messages(file)
                if po_entries:
                    f.write(f"#: {file}:")
                    f.write(po_entries)
        with open(_pot_file,'r') as f:
            _pot_content = f.read()
        _pot_content = split_pot(_pot_content)
        
    else:
        print("messages.pot des'nt exists!")
        return
    
    d1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M%z')
    year = datetime.datetime.now().strftime('%Y')
     
     
    d2 = d1
    for lang in nelangs:
        if len(lang)!=5: #ensure like zh-CN ,en-US
            continue
        header = po_header.replace("{d1}",d1).replace("{d2}",d2).replace("{lang}",lang).replace("{YEAR}",year).replace("{version}",__version__)
        path = os.path.join(locales_path,f"{lang}.po")
        #backup 
        if os.path.exists(path):
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S") 
            backup_filename = os.path.join(locales_path,f"{lang}_{timestamp}_bak.po")
            #  
            with open(path, "rb") as src_file:
                with open(backup_filename, "wb") as backup_file:
                    backup_file.write(src_file.read())

        with open(path,'w') as f:
            f.write(header+"\n"+_pot_content)
            
            print(f"generated {path}")
        #gen html files

def do_command(i18n_tool_file:str):
    global dev_mode
    if i18n_tool_file.lower()=='gettext':
        i18n_tool_file='pygettext'
    if i18n_tool_file=='pygettext':
        
        if not os.path.exists(locales_path):
            os.makedirs(locales_path,exist_ok=True)
        if len(sys.argv)<2:
            if dev_mode:
                sys.argv.append(cur_dir)
            else:
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
            if i18n_tool_file=='pygettext':
                convert_pot2po()
            print(f"Done!")
        except Exception as e:
            print(e)
    else:
        print(f"not found tools file:{i18n_tool_file}")
def main(): 
    #irails pygettext  -a -o messages.pot /path/to/your/dir/*.py
    global dev_mode
    irails_srcs = ['__init__.py','_i18n.py','_loader.py','_utils.py','auth.py','base_controller.py','cbv.py']
    for src in irails_srcs:
        p = os.path.join(cur_dir,src)
        if not os.path.exists(p):
            dev_mode = False
    if os.path.exists(root_path) and  os.path.isdir(root_path): 
        if not is_in_irails(root_path) or not is_in_app(cur_dir):
            print(f"Please exec in irails project's app dir ,like `apps/app`")
            if not dev_mode:
                exit()
    if len(sys.argv)>=2:
         
        cmd = sys.argv.pop(1)
        do_command(cmd)
    else:
        self_file = os.path.basename(__file__).lstrip("_").replace(".py",'')
        print(f"Usage: irails {self_file} [args...]")
        sys.exit(0)
     