import os
import sys
import yaml
import logging
from hashlib import md5
from typing import Dict
import os.path
import re
 

def is_cli_mode():
    executeble = sys.argv[0]
    executeble = os.path.basename(executeble)
    # print(f"current executeble:" + executeble)
    return (executeble.lower().startswith('irails'))

def is_in_app(directory):
    """
    check exists controllers , views dir in :directory
    """
    manifest = os.path.join(directory,'manifest.yaml')

    # controller_dir = os.path.join(directory, 'controllers')
    # views_dir = os.path.join(directory, 'views')
    return os.path.exists(manifest)
    


def is_in_irails(directory):
    """
    check exists configs dir,   main.py and configs/general.yaml 
    """ 
    configs_dir = os.path.join(directory, 'configs') 

    if not os.path.exists(configs_dir):  # or not os.path.exists(main_file):
        return False
    general_file = os.path.join(configs_dir, 'general.yaml') 
    if not os.path.exists(general_file):
        return False

    return True


ROOT_PATH = os.path.realpath(os.curdir)

IS_IN_irails = is_in_irails(ROOT_PATH)




def _extract_name(string):
    match = re.search(r'{([^}]*)}', string)
    if match:
        return match.group(1)
    else:
        return None


class YamlConfig:
    _raw_config: Dict = {}

    def __init__(self, filename: str = "", config: Dict = {},merge_by_group=False,recursion=False):
        self.filename = filename
        self.config = config
        self.load(merge_by_group,recursion)

    def __getitem__(self, key: str):
        return self.get(key)

    def __setitem__(self, key: str, value):
        self.set(key, value)

    def reload(self) -> bool:
        return self.load()

    def load(self,merge_by_group=False,recursion=False) -> bool:
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                self.config = yaml.safe_load(f)
                YamlConfig._raw_config = self.config
        elif os.path.isdir(self.filename) :
            self.config = self._merge_yaml_files(self.filename,merge_by_group,recursion)
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

    def dump(self) -> str:
        return yaml.safe_dump(self.config) if self.config else ""

    def save(self) -> bool:
        if not self.filename:
            return False
        with open(self.filename, "w") as f:
            yaml.safe_dump(self.config, f)
        return True

    def get(self, key: str, default=None):
        value = self.config.get(key, default)
        if isinstance(value, str):
            value = self._resolve_value(value, key)
        elif isinstance(value, dict):
            value = YamlConfig(filename="", config=value)
        return value

    def set(self, key: str, value):
        self.config[key] = value

    def delete(self, key: str):
        del self.config[key]
    def __contains__(self,key):
        return key in self.config
    
    def _merge_dicts(self, dict1: Dict, dict2: Dict) -> Dict:
        for key in dict2:
            if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                dict1[key] = self._merge_dicts(dict1[key], dict2[key])
            else:
                dict1[key] = dict2[key]
        return dict1

    def _merge_yaml_files(self, dir_path: str,merge_by_group=False,recursion=False) -> Dict:
        merged_config = {}
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path) and file_name.endswith(".yaml"):
                if merge_by_group:
                    _key = file_name.split(".")[0]
                    file_config = {_key:self._load_yaml_file(file_path)}
                else:
                    file_config = self._load_yaml_file(file_path)
                if isinstance(file_config, dict):
                    merged_config = self._merge_dicts(
                        merged_config, file_config)
            elif os.path.isdir(file_path) and recursion:
                if merge_by_group:
                    _key = os.path.basename(file_path)
                    dir_config = {_key:self._merge_yaml_files(file_path)}
                else:
                    dir_config = self._merge_yaml_files(file_path)
                merged_config = self._merge_dicts(merged_config, dir_config)
        return merged_config

    def _load_yaml_file(self, file_path: str) -> Dict:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)

    def _resolve_value(self, value: str, key: str) -> str:
        while "{" in value and "}" in value:
            name = _extract_name(value)
            if not name:
                break
            if name == key:
                raise RuntimeError(
                    f"Configure file error: circular reference `{name}`")
            if "." in name:
                segment_name, sub_key = name.split(".", 1)
                if segment_name == "ROOT":
                    # value = value.replace("{" + name + "}", self.config.get(sub_key, ""))
                    value = value.replace(
                        "{" + name + "}", YamlConfig(config=self._raw_config).get(sub_key, ""))
                else:
                    # segment_config = self.config.get(segment_name, {})
                    segment_config =  config.get(segment_name, {})
                    if isinstance(segment_config, dict) or isinstance(segment_config,YamlConfig):
                        sub_keys = sub_key.split(".")
                        sub_value = segment_config
                        for sub_key in sub_keys:
                            sub_value = sub_value.get(sub_key, {})
                        value = value.replace("{" + name + "}", str(sub_value))
            else:
                value = value.replace(
                    "{" + name + "}", self.config.get(name, ""))
        return value

if is_in_app(ROOT_PATH):
    ROOT_PATH = os.path.join(ROOT_PATH,"../..")
    config = YamlConfig( os.path.join(ROOT_PATH,"configs"))
    if not is_cli_mode():
        os.chdir(ROOT_PATH)
elif IS_IN_irails:
    config = YamlConfig(os.path.join(ROOT_PATH, "configs"))
else:
    # print(f"configs dir not found anywhere!")
    config = {}
_project_name = os.path.basename(ROOT_PATH)
debug = False




