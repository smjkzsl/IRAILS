import argparse
import sys
import os
from jinja2 import Template
from irails._utils import get_snaked_name, to_camel_case, get_plural_name,ensure_line
import typing

from irails.config import is_in_app, is_in_irails
cur_dir = os.path.abspath(os.curdir)


def render_tpl(src_tpl, dest_file, context: typing.Dict):
    # E:\codedemo\IRAILS\irails\scripts\tpls\app\model.jinja
    tpl_path = os.path.join(os.path.dirname(__file__), 'tpls', 'app')
    tpl_model = os.path.join(tpl_path, src_tpl)
    if not os.path.exists(tpl_model):
        print(f"{tpl_model} not found!exit")
        return False
    if os.path.exists(dest_file):
        print(f"{dest_file} exists!,skip...")
    else:
        with open(tpl_model, 'r') as f:
            content = f.read()

        template = Template(content)
        dest_content = template.render(context)

        with open(dest_file, 'w') as f:
            f.write(dest_content)
            print(f"generated {dest_file}")

    return True


def get_app_name():
    app_dir = os.path.basename(cur_dir)
     
    return f"{app_dir}"


def generate(args):
    app_name = get_app_name()
    if not args.name:
        print(f'controller name is empty,exit!')
        exit()
    name = args.name.pop(0)
    model_name = to_camel_case(name)
    model_path_name = get_snaked_name(name)
    model_plural_name = get_plural_name(model_name).lower()
    context = {"model_name": model_name,
               "model_path_name": model_path_name,
               "model_plural_name": model_plural_name,
               "app_name": app_name,
               }
    columns = []
    if not len(args.name) > 0:
        args.name.append("id")
    columns = args.name
    context["columns"] = columns
    dest_file = os.path.join(cur_dir, "models", model_path_name+'.py')
    src_tpl = "model.jinja"
    if render_tpl(src_tpl=src_tpl, dest_file=dest_file, context=context): #model file
        __init_file = os.path.join(cur_dir,'models','__init__.py')
        ensure_line(__init_file,f"from .{model_path_name} import *")

        service_path_name = model_path_name+'_service'
        dest_file = os.path.join(cur_dir, "services", service_path_name+'.py')
        context['service_name'] = f"{model_name}Service"
        context['service_path_name'] = service_path_name
        if render_tpl(src_tpl="service.jinja", dest_file=dest_file, context=context):#service file
            __init_file = os.path.join(cur_dir,'services','__init__.py')
            ensure_line(__init_file,f"from .{service_path_name} import *")

            dest_file = os.path.join(
                cur_dir, "tests", f"test_{service_path_name}.py")
            if render_tpl(src_tpl="test_service.jinja", dest_file=dest_file, context=context):#test service file
                print("Done!")
                return True
    return False


def main():
    root_path = os.path.abspath(os.path.join(cur_dir, "../.."))
    if os.path.exists(root_path) and os.path.isdir(root_path):
        if not is_in_irails(root_path) or not is_in_app(cur_dir):
            print(f"Please exec in irails project's app dir ,like `apps/app`")
            exit()
    self_file = __file__.lstrip("_").replace(".py", '')
    parser = argparse.ArgumentParser(
        usage=f"{sys.argv[0]} {self_file} [-h] [--name] `model [columns ...]` ...", description='create new model')
    parser.add_argument('--name', help="model name to create")
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not any(args.__dict__.values()):
        parser.print_help()
    if not args.name:
        args.name = args.args
    else:
        args.name = [args.name]
    generate(args)
