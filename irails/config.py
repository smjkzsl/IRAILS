import os,sys
import yaml
import logging
from hashlib import md5
from typing import Dict
import os.path
import re

def is_in_irails(directory):
    """
    check exists configs dir,   main.py and configs/general.yaml 
    """
    
    configs_dir = os.path.join(directory, 'configs')
    main_file = os.path.join(directory, 'main.py')

    if not os.path.exists(configs_dir) or not os.path.exists(main_file):
        return False  
    general_file = os.path.join(configs_dir, 'general.yaml')

    if not os.path.exists(general_file):
        return False
    
    return True
ROOT_PATH = os.path.realpath(os.curdir)
 
IS_IN_irails = is_in_irails(ROOT_PATH)
def is_cli_mode():
    executeble = sys.argv[0]
    executeble = os.path.basename(executeble)
    # print(f"current executeble:" + executeble)
    return (executeble.lower().startswith('irails'))

def _extract_name(string):
    match = re.search(r'{([^}]*)}', string)
    if match:
        return match.group(1)
    else:
        return None

class YamlConfig:
    _raw_config = {}
    def __init__(self, filename:str="",config:Dict={}):
        self.filename = filename
        self.config = config
        self.load()
    def __getitem__(self,key):
        return self.get(key)
    def __setitem__(self,key,value):
        self.set(key,value)
    def reload(self):
        return self.load()
    def load(self):
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                self.config = yaml.safe_load(f)
                YamlConfig._raw_config = self.config

        elif os.path.isdir(self.filename):
            self.config = self._merge_yaml_files(self.filename)
            YamlConfig._raw_config = self.config
        elif self.config:
            return True
        else:
            if is_cli_mode():
                pass
            else:
                raise Exception(f"{self.filename} is not a file or directory")
            return False
        return True
    def dump(self):
        return yaml.safe_dump(self.config) if self.config else ""
    def save(self):
        if not self.filename:
            return False
        with open(self.filename, "w") as f:
            yaml.safe_dump(self.config, f)
        return True
    def get(self, key:str, default=None): 
        
        
        value = self.config.get(key, default)
        if isinstance(value,str) and value.find("{")>-1:
            while value.find("{")>-1 and value.find("}")>0:
                name = _extract_name(value)
                if name:
                    if name==key:
                        raise RuntimeError(f"configure file error circular reference `{name}`")
                    
                    if name.find(".")>0:
                        paris = name.split(".")
                        _root_value = self._raw_config[paris.pop(0)]
                        _value = _root_value
                        while paris:
                            _value = _value[paris.pop(0)]
                            while _value.find("{")>-1 and value.find("}")>0:
                                _name = _extract_name(_value)
                                if _name:
                                    _expr = _root_value.get(_name,"")
                                    _x = f"{_name}"
                                    _value = _value.replace('{'+_x+'}',_expr)
                        return _value
                        pass
                    
                    expr = self.config.get(name,"")
                x = f"{name}"
                value = value.replace('{'+x+'}',expr)
        elif isinstance(value,dict):
            return YamlConfig(filename="",config=value)
        return value
    
    def set(self, key, value):
        self.config[key] = value

    def delete(self, key):
        del self.config[key]

    def _merge_dicts(self, dict1, dict2):
        for key in dict2:
            if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                dict1[key] = self._merge_dicts(dict1[key], dict2[key])
            else:
                dict1[key] = dict2[key]
        return dict1

    def _merge_yaml_files(self, dir_path):
        global _log
        merged_config = {}
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path) and file_name.endswith(".yaml"):
                file_config = self._load_yaml_file(file_path)
                if isinstance(file_config, dict):
                    merged_config = self._merge_dicts(merged_config, file_config)
                # else:
                #     _log.warn(f"YAML file {file_path} must contain a dictionary")
            elif os.path.isdir(file_path):
                dir_config = self._merge_yaml_files(file_path)
                merged_config = self._merge_dicts(merged_config, dir_config)
        return merged_config

    def _load_yaml_file(self, filename):
        with open(filename, "r") as f:
            return yaml.safe_load(f)
def __init_log(__logCfg):
    if not __logCfg:
        return None
    from fastapi.logger import logger
    __log_level = __logCfg['level'] or 'DEBUG'
    __log_file = __logCfg['file'] or None 
    __isdebug = config.get("debug") or False
    logger.name = __logCfg.get("name",'iRails')
    if __log_file:
        __log_file = os.path.abspath(__log_file)
    log_format="%(asctime)s %(name)s:%(levelname)s:%(message)s"
    datefmt="%Y-%M-%d %H:%M:%S" 
    if __log_file:
        if __isdebug:
            try:
                os.remove(__log_file)
            except:
                pass
            import io
            
        handler = logging.FileHandler(__log_file,mode='a')
        
    else:
        import sys
        handler = logging.StreamHandler(sys.stdout)  
    handler.setLevel(logging._nameToLevel[__log_level]) 
    handler.setFormatter(logging.Formatter(fmt= log_format,datefmt=datefmt)) 
    logger.addHandler(handler)
    
    logger.setLevel(logging._nameToLevel[__log_level]) 
    return logger
    # return logging.getLogger(__logCfg['name'] or 'FastapiMvcFramework')

config = YamlConfig(os.path.join(ROOT_PATH,"configs") )

_log = __init_log(config.get("log"))
if _log:
    _log.setLevel(logging.DEBUG)

